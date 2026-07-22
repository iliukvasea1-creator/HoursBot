from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

from datetime import datetime
import json
import os

from config import BOT_TOKEN
from sheets import (
    add_work_hours,
    already_sent_today,
    get_month_hours,
)

ASK_NAME = 1

USERS_FILE = "users.json"


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


users = load_users()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id in users:
        await update.message.reply_text(
            f"Вітаю, {users[user_id]}!\n"
            "Надішліть лише кількість відпрацьованих годин.\n\n"
            "Наприклад:\n"
            "8\n"
            "7.5"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Вітаю!\n\n"
        "Введіть ваше ім'я та прізвище."
    )

    return ASK_NAME


async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.message.text.strip()

    users[user_id] = name
    save_users(users)

    await update.message.reply_text(
        f"Дякую, {name}!\n"
        "Тепер просто надсилайте кількість годин.\n\n"
        "Наприклад:\n"
        "8"
    )

    return ConversationHandler.END


async def show_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await update.message.reply_text(
            "Спочатку виконайте команду /start."
        )
        return

    total = get_month_hours(users[user_id])
    month = datetime.now().strftime("%m.%Y")

    await update.message.reply_text(
        f"📅 {month}\n\n"
        f"👤 {users[user_id]}\n"
        f"🕒 Разом: {total} годин"
    )
async def save_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await update.message.reply_text(
            "Спочатку виконайте команду /start."
        )
        return

    text = update.message.text.strip().replace(",", ".")

    try:
        hours = float(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Введіть тільки число.\n\nНаприклад:\n8\n7.5"
        )
        return

    if already_sent_today(users[user_id]):
        await update.message.reply_text(
            "❌ Ви вже відправили години за сьогодні."
        )
        return

date = datetime.now().strftime("%d.%m.%Y")

add_work_hours(
    date=date,
    worker=users[user_id],
    hours=hours,
)

await update.message.reply_text(
    f"✅ Записано!\n\n"
    f"Дата: {date}\n"
    f"Працівник: {users[user_id]}\n"
    f"Години: {hours}"
)

    await update.message.reply_text(
        f"✅ Записано!\n\n"
        f"Дата: {date}\n"
        f"Працівник: {users[user_id]}\n"
        f"Години: {hours}"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    save_name,
                )
            ],
        },
        fallbacks=[],
    )

    app.add_handler(conv)

    app.add_handler(CommandHandler("hours", show_hours))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            save_hours,
        )
    )

    print("Бот запущений...")

    app.run_polling()


if __name__ == "__main__":
    main()