import os
import json
import requests
from datetime import datetime, timedelta
from storage import save_entry
from memory_utils import load_memory, save_memory
from database import (
    init_db, save_check_in, save_ai_response,
    generate_daily_report
)

# Inicijalizacija baze i memorije
init_db()

# sistemski prompt
conversation = [{
    "role": "system",
    "content": (
        "Odgovaraj ljubazno na srpskom jeziku, kratko sa ne više od 100 reči i jasno. Ukoliko pređeš limit od 100 reči skrati odgovor."
        "Ti si AI kućni doktor koji korisniku pomaže da analizira zdravlje koristeći njegove dnevne podatke. "
        "Korisnik ti daje informacije o glukozi, navikama, obrocima, snu i svom opštem stanju."
        "Korisnik pokušava:\n"
        "- Stabilizaciju šećera u krvi\n"
        "- Bolji san i više energije\n"
        "- Stvaranje zdravih navika\n\n"
        "Kada dobiješ dnevni JSON izveštaj, koristi sledeću strukturu:\n\n"
        "```\n"
        "{\n"
        "  \"avg\": float,                // prosečna glukoza (mmol/L)\n"
        "  \"min\": float,                // najniža vrednost\n"
        "  \"min_time\": \"HH:MM\",       // vreme najniže\n"
        "  \"max\": float,                // najviša vrednost\n"
        "  \"max_time\": \"HH:MM\",       // vreme najviše\n"
        "  \"range\": float,              // raspon (max - min)\n"
        "  \"tir\": float,                // Time in Range ( između 4-10 mmol)\n"
        "  \"hypo\": int,                 // broj hipoglikemija (<4)\n"
        "  \"hyper\": int,                // broj hiperglikemija (>10)\n"
        "  \"meals\": int,                // broj obroka\n"
        "  \"comment\": string,           // opis dana\n"
        "  \"rating\": int                // ocena dana (1–5)\n"
        "}\n"
        "```\n\n"

    )
}]

conversation += load_memory()

# Kreiranje prompta za model
def build_prompt(conversation):
    prompt = ""
    for message in conversation[-10:]:
        role = "Korisnik" if message["role"] == "user" else "Asistent"
        prompt += f"{role}: {message['content']}\n"

    prompt += (

        "- Napravi analizu (trendovi, vreme najvise i najnize vrednosti,raspon vrednosti)\n"

    )
    return prompt


# Funkcija za komunikaciju sa lokalnim Ollama modelom
def query_ollama(prompt):
    print("\n📤\n")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=300
        )

        if response.status_code != 200:
            print(f"❌ Greška od Ollama API-ja: {response.status_code}")
            return "[Greška: AI nije odgovorio]"

        return response.json().get("response", "[Nema odgovora iz modela]")

    except requests.exceptions.RequestException as e:
        print(f"❌ Problem sa vezom ka lokalnom modelu: {e}")
        return "[Greška u komunikaciji sa lokalnim modelom]"


# 🩺 Dobrodošlica
print("🩺 Dobrodošao u AI Smart Home Doktor (lokalni model)\n")

# 🔁 Glavna petlja
while True:
    user_input = input("> ")
    if user_input.lower() in ['exit', 'quit']:
        print("👋 Zatvaranje aplikacije.")
        break

    if user_input.lower() == "reset memory":
        if os.path.exists("memory.json"):
            os.remove("memory.json")
            print("🧹 Memorija očišćena. Počinjem od nule.\n")
        conversation = [conversation[0]]
        continue

    save_check_in(user_input)
    conversation.append({"role": "user", "content": user_input})

    # 🧾 Ubacivanje dnevnog izveštaja ako se pominje glukoza
    user_input_lower = user_input.lower()
    if any(word in user_input_lower for word in ["glukoza", "secer", "glikemija", "analiza"]):
        if "juce" in user_input_lower:
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "danas" in user_input_lower:
            target_date = datetime.now().strftime("%Y-%m-%d")
        else:
            target_date = None

        if target_date:
            raw_json = generate_daily_report(target_date)

            try:
                parsed = json.loads(raw_json)
                if "error" in parsed:
                    conversation.append({
                        "role": "system",
                        "content": f"⚠️ {parsed['error']} za {target_date}."
                    })
                else:
                    formatted_json = json.dumps(parsed, ensure_ascii=False, indent=2)
                    conversation.append({
                        "role": "system",
                        "content": (
                            f"📅 Dnevni izveštaj glukoze za {target_date} u JSON formatu:\n"
                            f"{formatted_json}\n\n"
                            "Na osnovu ovih podataka, analiziraj regulaciju šećera u krvi i daj preporuke."
                        )
                    })
                    print(f"\n📊 JSON izveštaj ubačen u prompt za datum {target_date}.\n")

            except Exception as e:
                conversation.append({
                    "role": "system",
                    "content": f"❌ Greška pri parsiranju JSON izveštaja: {e}"
                })


    # 📤 Slanje prompta
    prompt = build_prompt(conversation)
    response_text = query_ollama(prompt)

    # 🧠 Čuvanje odgovora
    print("\n🧐 Odgovor lokalnog AI asistenta:\n" + "-" * 40)
    print(response_text.strip())
    print("-" * 40)

    save_ai_response(response_text)
    conversation.append({"role": "assistant", "content": response_text})
    save_entry(user_input, response_text)
    save_memory(conversation)
