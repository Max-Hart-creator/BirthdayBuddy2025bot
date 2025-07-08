from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

DATA_FILE = "birthdays.json"

def load_birthdays():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_birthdays(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Надішли мені ім'я і дату народження у форматі:\n\nПетро 1999-08-12"
    )

async def add_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        name, date_str = text.split()
        datetime.strptime(date_str, "%Y-%m-%d")
        data = load_birthdays()
        user_id = str(update.message.chat_id)
        data.setdefault(user_id, []).append({"name": name, "date": date_str})
        save_birthdays(data)
        await update.message.reply_text(f"Збережено: {name} — {date_str}")
    except:
        await update.message.reply_text("Невірний формат. Введи: Ім'я 1999-08-12")

async def check_birthdays():
    data = load_birthdays()
    today = datetime.today()
    today_str = today.strftime("%m-%d")
    three_days_later = (today + timedelta(days=3)).strftime("%m-%d")

    for user_id, people in data.items():
        for person in people:
            bday_mmdd = person["date"][5:]
            if bday_mmdd == today_str:
                await app.bot.send_message(chat_id=int(user_id),
                    text=f"🎉 Сьогодні день народження у {person['name']}!")
            elif bday_mmdd == three_days_later:
                await app.bot.send_message(chat_id=int(user_id),
                    text=f"📅 Через 3 дні день народження у {person['name']}!")

async def main():
    global app
    import os
app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), add_birthday))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_birthdays, 'cron', hour=9)
    scheduler.start()

    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
