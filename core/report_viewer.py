from core.database import generate_daily_report, calculate_tir_over_period
from datetime import datetime, timedelta

print("\n📋 Dobrodošao u Pregled Dnevnih Izveštaja")
print("-" * 50)
print("Unesi:")
print("🗓  tačan datum u formatu YYYY-MM-DD")
print("📆  '7' za pregled poslednjih 7 dana")
print("📆  '14' za pregled poslednjih 14 dana")
print("📆  '30' za pregled poslednjih 30 dana")
print("📆  '90' za pregled poslednjih 90 dana")
print("❌  'exit' za izlaz")
print("-" * 50)
while True:
    choice = input("👉 Unos: ").strip().lower()

    if choice == "exit":
        print("👋 Izlaz iz pregleda.")
        break

    elif choice == "7":
        print("\n📅 Nedeljni izveštaj (poslednjih 7 dana)\n")
        for i in range(6, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"\n🗓 Izveštaj za {day}:")
            print(generate_daily_report(day))
            print("-" * 50)

        print(calculate_tir_over_period(7))

    elif choice == "14":
        print("\n📅 Nedeljni izveštaj (poslednjih 14 dana)\n")
        for i in range(13, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"\n🗓 Izveštaj za {day}:")
            print(generate_daily_report(day))
            print("-" * 50)
        print(calculate_tir_over_period(14))
    
    elif choice == "30":
        print("\n📅 Nedeljni izveštaj (poslednjih 30 dana)\n")
        for i in range(29, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"\n🗓 Izveštaj za {day}:")
            print(generate_daily_report(day))
            print("-" * 50)
        print(calculate_tir_over_period(30))
    
    elif choice == "90":
        print("\n📅 Nedeljni izveštaj (poslednjih 90 dana)\n")
        for i in range(89, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"\n🗓 Izveštaj za {day}:")
            print(generate_daily_report(day))
            print("-" * 50)
        print(calculate_tir_over_period(90))

    else:
        try:
            datetime.strptime(choice, "%Y-%m-%d")
            print(f"\n🗓 Izveštaj za {choice}:")
            print(generate_daily_report(choice))
            print("-" * 50)
        except ValueError:
            print("❌ Pogrešan format datuma. Koristi YYYY-MM-DD ili broj dana.")
