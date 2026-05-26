import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

user_data = {}

questions = [
    ("date", "📅 Дата заявки?"),
    ("contract", "📄 Номер договора?"),
    ("carrier", "🚚 Перевозчик?"),
    ("loading", "📍 Адрес загрузки?"),
    ("unloading", "📍 Адрес разгрузки?"),
    ("cargo", "📦 Что за груз?"),
    ("price", "💰 Стоимость перевозки?"),
    ("payment", "💳 Условия оплаты?"),
    ("driver", "👤 Водитель / телефон / машина?"),
    ("extra", "⚠️ Дополнительные условия?"),
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 Главтрансальянс бот запущен!\n\nНапишите /new для создания заявки."
    )

async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    user_data[chat_id] = {
        "step": 0,
        "answers": {}
    }

    await update.message.reply_text(
        "🚛 Создание новой заявки\n\n" + questions[0][1]
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id not in user_data:
        await update.message.reply_text(
            "Напишите /new для создания заявки."
        )
        return

    step = user_data[chat_id]["step"]

    key, question = questions[step]

    user_data[chat_id]["answers"][key] = text

    user_data[chat_id]["step"] += 1

    if user_data[chat_id]["step"] < len(questions):
        next_question = questions[user_data[chat_id]["step"]][1]

        await update.message.reply_text(next_question)

    else:
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

        await update.message.reply_text(result)

        del user_data[chat_id]

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("new", new))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("Бот запущен...")

app.run_polling(drop_pending_updates=True)
