# storage.py
import csv
from datetime import datetime

def save_entry(user_input, assistant_reply):
    with open("health_log.csv", mode="a", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), user_input, assistant_reply])
