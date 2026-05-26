import os
import time
import threading
import requests
from flask import Flask

TOKEN = os.getenv("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

user_data = {}

questions = [
    ("date", "Date?"),
    ("contract", "Contract number?"),
    ("carrier", "Carrier?"),
    ("loading", "Loading address?"),
    ("unloading", "Unloading address?"),
    ("cargo", "Cargo?"),
    ("price", "Price?"),
    ("payment", "Payment terms?"),
    ("driver", "Driver / phone / truck?"),
    ("extra", "Extra conditions?")
]

def send_message(chat_id, text):
    requests.post(
        f"{URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def handle_text(chat_id, text):
    if text == "/start":
        send_message(chat_id, "Bot started. Type /new")
        return

    if text == "/new":
        user_data[chat_id] = {"step": 0, "answers": {}}
        send_message(chat_id, questions[0][1])
        return

    if chat_id not in user_data:
        send_message(chat_id, "Type /new")
        return

    step = user_data[chat_id]["step"]
    key = questions[step][0]

    user_data[chat_id]["answers"][key] = text
    user_data[chat_id]["step"] += 1

    if user_data[chat_id]["step"] >= len(questions):
        a = user_data[chat_id]["answers"]

        result = f"""
NEW REQUEST

Date:
{a['date']}

Contract:
{a['contract']}

Carrier:
{a['carrier']}

Loading:
{a['loading']}

Unloading:
{a['unloading']}

Cargo:
{a['cargo']}

Price:
{a['price']}

Payment:
{a['payment']}

Driver:
{a['driver']}

Extra:
{a['extra']}
"""

        send_message(chat_id, result)
        del user_data[chat_id]

    else:
        next_step = user_data[chat_id]["step"]
        send_message(chat_id, questions[next_step][1])

def poll():
    offset = 0

    while True:
        try:
            r = requests.get(
                f"{URL}/getUpdates",
                params={"timeout": 30, "offset": offset}
            ).json()

            for update in r["result"]:
                offset = update["update_id"] + 1

                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]

                    handle_text(chat_id, text)

        except Exception as e:
            print(e)

        time.sleep(1)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

threading.Thread(target=poll).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
