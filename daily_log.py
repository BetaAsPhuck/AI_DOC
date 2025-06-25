from core.database import log_daily_info, generate_daily_report
from datetime import datetime, timedelta
print("\n📅 Unos dnevnog izveštaja")
print("1️⃣ Danas")
print("2️⃣ Juče")
print("3️⃣ Unesi tačan datum (YYYY-MM-DD)")

# 🔹 Izbor dana
while True:
    choice = input("Za koji dan unosiš podatke? (1, 2 ili 3): ")
    if choice == "1":
        date = datetime.now().strftime("%Y-%m-%d")
        break
    elif choice == "2":
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        break
    elif choice == "3":
        custom = input("Unesi datum (YYYY-MM-DD): ")
        try:
            datetime.strptime(custom, "%Y-%m-%d")
            date = custom
            break
        except ValueError:
            print("⚠️ Pogrešan format. Probaj ponovo.")
    else:
        print("⚠️ Molim unesi 1, 2 ili 3.")

print(f"\n🗓 Unos za datum: {date}")

# 🔹 Broj obroka
while True:
    try:
        meals = int(input("🍽 Unesi broj obroka tog dana: "))
        break
    except ValueError:
        print("⚠️ Molim unesi ceo broj (npr. 3)")

# 🔹 Komentar
comment = input("🧠 Napiši kratak komentar (aktivnost, stres, ishrana...): ")

# 🔹 Ocena dana
while True:
    try:
        rating = int(input("🙂 Oceni dan od 1 (loš) do 5 (odličan): "))
        if 1 <= rating <= 5:
            break
        else:
            print("⚠️ Unesi broj između 1 i 5.")
    except ValueError:
        print("⚠️ Molim unesi broj između 1 i 5.")

# 🔹 Snimi u bazu
log_daily_info(date, meals, comment, rating)
print("\n✅ Dnevni unos sačuvan!")

# 🔹 Prikaz izveštaja
print("\n📋 Dnevni izveštaj:")
print("-" * 40)
print(generate_daily_report(date))
print("-" * 40)
