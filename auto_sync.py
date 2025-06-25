import time
import schedule
from core.database import store_glucose_from_nightscout, init_db

init_db()
print("Inicijalizujem Bazu podataka...")
print("🔄 Pokrećem automatsko sinhronizovanje sa Nightscout serverom...")

def sync():
    print("📡 Povlačenje podataka sa Nightscout...")
    store_glucose_from_nightscout()

# 🕒 Svakih 10 minuta
schedule.every(10).minutes.do(sync)

# 🟢 Prvo pokretanje odmah
sync()

while True:
    schedule.run_pending()
    time.sleep(30)
