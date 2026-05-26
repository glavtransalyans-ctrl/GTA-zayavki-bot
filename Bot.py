import os
import time
import threading
import requests
from flask import Flask

TOKEN = os.getenv("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

user_data = {}

questions = [("date","Дата заявки?"),("contract","Номер договора?"),("carrier","Перевозчик?"),("loading","Адрес загрузки?"),("unloading","Адрес разгрузки?"),("cargo","Что за груз?"),("price","Стоимость перевозки?"),("payment","Условия оплаты?"),("driver","Водитель / телефон / машина?"),("extra","Дополнительные условия?")]

def send_message(chat_id, text):
  requests.post(
  f"{URL}/sendMessage",
  json={"chat_id": chat_id, "text": text}
  )

def handle_text(chat_id, text):
    if text == "/start":
        send_message(chat_id, "🚛 Главтрансальянс бот запущен!\n\nНапишите /new для создания заявки.")
        return

    if text == "/new":
        user_data[chat_id] = {"step": 0, "answers": {}}
        send_message(chat_id, "🚛 Создание новой заявки\n\n" + questions[0][1])
        return

    if chat_id not in user_data:
        send_message(chat_id, "Напишите /new для создания заявки.")
        return

    step = user_data[chat_id]["step"]
    key, _ = questions[step]

    user_data[chat_id]["answers"][key] = text
    user_data[chat_id]["step"] += 1

    if user_data[chat_id]["step"] < len(questions):
        next_question = questions[user_data[chat_id]["step"]][1]
        send_message(chat_id, next_question)
        return

    a = user_data[chat_id]["answers"]

    result = f"""
✅ ЗАЯВКА ГОТОВА

📅 Дата:
{a['date']}

📄 Договор:
{a['contract']}

🚚 Перевозчик:
{a['carrier']}

📍 Загрузка:
{a['loading']}

📍 Разгрузка:
{a['unloading']}

📦 Груз:
{a['cargo']}

💰 Стоимость:
{a['price']}

💳 Оплата:
{a['payment']}

👤 Водитель:
{a['driver']}

⚠️ Доп. условия:
{a['extra']}
"""

    send_message(chat_id, result)
    del user_data[chat_id]

def bot_loop():
    offset = 0
    print("Бот запущен...")

    while True:
        try:
            r = requests.get(
                f"{URL}/getUpdates",
                params={"offset": offset, "timeout": 30}
            )
            data = r.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                handle_text(chat_id, text)

        except Exception as e:
            print("Ошибка:", e)
            time.sleep(5)

app = Flask(__name__)

@app.route("/")
def home():
    return "GTA bot is running"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
