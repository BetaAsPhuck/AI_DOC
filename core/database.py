import sqlite3
import requests
import pytz
import json
from datetime import datetime, timedelta

NIGHTSCOUT_URL = "https://moj-ai-doktor-56838254bbe0.herokuapp.com/api/v1/entries.json?count=2000"
DB_NAME = "health_data.db"



def run_proactive_glucose_check():
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        SELECT timestamp, glucose_value FROM glucose
        WHERE date(timestamp) = ?
    ''', (target_date,))
    readings = c.fetchall()
    conn.close()

    if not readings:
        return f"📅 {target_date}: Nema dostupnih merenja glukoze."

    values = [g for _, g in readings]
    count = len(values)
    avg_glucose = round(sum(values) / count, 1)
    min_val = min(values)
    max_val = max(values)

    in_range = [v for v in values if 4.0 <= v <= 10.0]
    tir_percent = round(100 * len(in_range) / count, 1)

    hypo_events = len([v for v in values if v < 4.0])
    hyper_events = len([v for v in values if v > 10.0])

    question_parts = []

    # Dodavanje pitanja na osnovu proseka
    if avg_glucose > 10:
        question_parts.append("📈 Glukoza ti je u proseku bila viša od normalnog. Da li si imao/la veće obroke ili bio/la pod stresom?")
    elif avg_glucose < 4:
        question_parts.append("📉 Prosečna glukoza je bila niska?")
    else:
        question_parts.append("✅ Prosečna glukoza je bila u zdravom opsegu.")

    # TIR komentar
    if tir_percent < 70:
        question_parts.append(f"🔍 Samo {tir_percent}% vremena si bio u opsegu 4–10 mmol/L. Da li znaš šta je moglo uticati na to?")
    else:
        question_parts.append(f"🎯 Tvoj TIR je bio {tir_percent}%, što je dobro!")

    # Epizode
    if hypo_events > 1:
        question_parts.append(f"⚠️ Bilo je {hypo_events} epizoda ispod 4 mmol/L. Da li si uočio simptome hipoglikemije?")
    if hyper_events > 1:
        question_parts.append(f"⚠️ Bilo je {hyper_events} epizoda iznad 10 mmol/L. Secas li se sta si jeo?")

    final_prompt = (
        f"📅 {target_date}\n"
        f"🔢 Prosečna glukoza: {avg_glucose} mmol/L\n"
        f"🔻 Minimum: {min_val} mmol/L\n"
        f"🔺 Maksimum: {max_val} mmol/L\n"
        f"📊 Time in Range: {tir_percent}%\n\n" +
        "\n".join(question_parts)
    )

    return final_prompt

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Tabela za navike
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            start_date TEXT
        )
    ''')

    # Tabela za dnevne upise korisnika
    c.execute('''
        CREATE TABLE IF NOT EXISTS check_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_input TEXT
        )
    ''')

    # Tabela za AI odgovore
    c.execute('''
        CREATE TABLE IF NOT EXISTS ai_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ai_text TEXT
        )
    ''')

    # Tabela za glukozu
    c.execute('''
        CREATE TABLE IF NOT EXISTS glucose (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT UNIQUE,
            glucose_value INTEGER,
            source TEXT
        )
    ''')       
    # Tabela za dnevne navike i komentare
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            meals INTEGER,
            comment TEXT,
            rating INTEGER
        )
    ''')

    

    conn.commit()
    conn.close()

def save_check_in(user_input):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO check_ins (timestamp, user_input) VALUES (?, ?)",
              (datetime.now().isoformat(), user_input))
    conn.commit()
    conn.close()

def save_ai_response(ai_text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO ai_responses (timestamp, ai_text) VALUES (?, ?)",
              (datetime.now().isoformat(), ai_text))
    conn.commit()
    conn.close()

def add_habit(name, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO habits (name, description, start_date) VALUES (?, ?, ?)",
              (name, description, datetime.now().date().isoformat()))
    conn.commit()
    conn.close()

def insert_glucose_entry(timestamp, glucose_value, source="nightscout"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR IGNORE INTO glucose (timestamp, glucose_value, source)
            VALUES (?, ?, ?)
        ''', (timestamp, glucose_value, source))
        conn.commit()

        if c.rowcount == 0:
            print(f"⚠️  Preskočeno - već postoji unos za: {timestamp}")
        else:
            print(f"✅ Unet zapis: {timestamp} | {glucose_value} mmol/L")

    except Exception as e:
        print(f"❌ Greška pri upisu: {e}")
    finally:
        conn.close()

def store_glucose_from_nightscout():
    response = requests.get(NIGHTSCOUT_URL)
    print("📡 Status kod:", response.status_code)

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"🔍 Vraćeno {len(data)} unosa iz Nightscout API-ja")

            for entry in data:
                timestamp = entry.get('dateString')
                sgv = entry.get('sgv')  # u mg/dL

                if timestamp and sgv:
                    mmol = round(sgv / 18.0, 1)
                    insert_glucose_entry(timestamp, mmol, source="entries")
        except Exception as e:
            print("❌ JSON parsing greška:", e)
    else:
        print("❌ Nije moguće dohvatiti podatke sa Nightscout servera.")

def get_recent_glucose(days=3):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, glucose_value FROM glucose
        WHERE timestamp >= datetime('now', ?)
        ORDER BY timestamp DESC
    ''', (f'-{days} days',))
    rows = c.fetchall()
    conn.close()



    # Konverzija UTC → lokalno vreme (Srbija: Europe/Belgrade)
    local_tz = pytz.timezone('Europe/Belgrade')
    converted = []

    for ts_str, glucose in rows:
        try:
            utc_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            local_time = utc_time.astimezone(local_tz)
            formatted = local_time.strftime("%Y-%m-%d %H:%M")
            converted.append((formatted, glucose))
        except Exception as e:
            print(f"⚠️ Greška u konverziji vremena: {e}")
            converted.append((ts_str, glucose))  # fallback ako konverzija padne

    return converted

def log_daily_info(date, meals, comment, rating):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO daily_logs (date, meals, comment, rating)
        VALUES (?, ?, ?, ?)
    ''', (date, meals, comment, rating))
    conn.commit()
    conn.close()

def generate_daily_report(date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Glukoza za taj dan
    c.execute('''
        SELECT timestamp, glucose_value FROM glucose
        WHERE date(timestamp) = ?
    ''', (date,))
    readings = c.fetchall()

    if not readings:
        return json.dumps({
            "date": date,
            "error": "Nema glukoznih podataka za ovaj dan"
        })

    values = [g for _, g in readings]
    timestamps = [t for t, _ in readings]
    min_val = min(values)
    max_val = max(values)
    avg_val = round(sum(values) / len(values), 1)
    glucose_range = round(max_val - min_val, 1)
    min_index = values.index(min_val)
    max_index = values.index(max_val)

    # Prilagodba vremena
    def fix_time(ts):
        try:
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
            except:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return (dt + timedelta(hours=2)).strftime("%H:%M")

    min_time = fix_time(timestamps[min_index])
    max_time = fix_time(timestamps[max_index])

    # Time in range
    in_range = [v for v in values if 4 <= v <= 10]
    below_range = [v for v in values if v < 4]
    above_range = [v for v in values if v > 10]

    tir_percent = round((len(in_range) / len(values)) * 100, 1)
    hypo_count = len(below_range)
    hyper_count = len(above_range)

    # Dnevni log
    c.execute('SELECT meals, comment, rating FROM daily_logs WHERE date = ?', (date,))
    log = c.fetchone()
    meals = log[0] if log else None
    comment = log[1] if log else None
    rating = log[2] if log else None

    conn.close()

    # JSON format za AI
    report = {
        "date": date,
        "avg": avg_val,
        "min": min_val,
        "min_time": min_time,
        "max": max_val,
        "max_time": max_time,
        "glucose_range": glucose_range,
        "tir_percent": tir_percent,
        "hypo_events": hypo_count,
        "hyper_events": hyper_count,
        "meals": meals,
        "comment": comment,
        "rating": rating
    }

    return json.dumps(report, ensure_ascii=False, indent=2)


def calculate_tir_over_period(days, lower_bound=4.0, upper_bound=10.0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT glucose_value FROM glucose
        WHERE timestamp >= datetime('now', ?)
    ''', (f'-{days} days',))
    readings = c.fetchall()
    conn.close()

    if not readings:
        return f"📆 {days} dana: nema podataka."

    total = len(readings)
    in_range = sum(1 for (g,) in readings if lower_bound <= g <= upper_bound)
    tir_percentage = round(in_range / total * 100, 1)

    return f"📊 TIR za poslednjih {days} dana: {tir_percentage}% (4–10 mmol/L)"


# Pokreni test ručno
if __name__ == "__main__":
    print("🚀 Pokrećem init_db()...")
    init_db()
    print("✅ Baza inicijalizovana.")
    
    print("📡 Pokušavam da učitam podatke sa Nightscout...")
    store_glucose_from_nightscout()

