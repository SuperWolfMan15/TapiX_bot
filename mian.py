import os
import random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from dotenv import load_dotenv

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Промокоды
PROMOCODES = [
    "SUNNYDAY", "BITEBYTE", "LUCKYCLAP", "COZYTAP", "TAPWAVE",
    "ZAPBOOM", "QUIETPOWER", "TAPSTORM", "CLOUDYCODE", "BUBBLETAP",
    "GAMERGRIND", "EASYTAP", "FINALHIT"
]

# Словари пользователей и их рефералов
users = {}
invited_by = {}

# Flask сервер для Railway
app = Flask(__name__)

@app.route("/")
def home():
    return "TapiX Bot is running!"

# Создание клавиатуры
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Пригласить друзей", callback_data="invite")],
        [InlineKeyboardButton("🎁 Мои промокоды", callback_data="promos")]
    ])

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    args = context.args

    if uid not in users:
        users[uid] = {"invites": 0, "promos": []}

        # Обработка приглашения
        if args:
            try:
                inviter_id = int(args[0])
                if inviter_id != uid and inviter_id in users:
                    if uid not in invited_by:
                        invited_by[uid] = inviter_id
                        users[inviter_id]["invites"] += 1

                        # Выдача промокода
                        if users[inviter_id]["invites"] == 5:
                            code = random.choice(PROMOCODES)
                            users[inviter_id]["promos"].append(code)
                            await context.bot.send_message(
                                inviter_id,
                                f"🎉 Поздравляем! Вы пригласили 5 друзей и получили промокод: {code}"
                            )
            except:
                pass

    await update.message.reply_text(
        f"Привет, {user.first_name}!\nЭто бот TapiX 🎮",
        reply_markup=main_menu()
    )

# Обработка нажатий кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "invite":
        invite_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await query.edit_message_text(
            f"🔗 Ваша ссылка для приглашения:\n{invite_link}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
            ])
        )

    elif query.data == "promos":
        promos = users.get(user_id, {}).get("promos", [])
        if promos:
            await query.edit_message_text(
                f"🎁 Ваши промокоды:\n" + "\n".join(promos),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
                ])
            )
        else:
            await query.edit_message_text(
                "❌ У вас пока нет промокодов.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
                ])
            )

    elif query.data == "back":
        await query.edit_message_text(
            f"Главное меню 📱",
            reply_markup=main_menu()
        )

# Основной запуск
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    await app.run_polling()

# Flask запуск на Railway
if __name__ == "__main__":
    import asyncio
    from threading import Thread

    # Запуск Flask в отдельном потоке
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))).start()

    # Запуск Telegram-бота
    asyncio.run(main())