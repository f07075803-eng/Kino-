import logging
from aiogram import Bot, Dispatcher, executor, types
from flask import Flask
from threading import Thread
import os

# --- MA'LUMOTLAR ---
API_TOKEN = '8599100876:AAGhk-U0gLCKNUAEf5Q1qThzsaAH-WHYmmA'
ADMIN_ID = 7257755738

# --- RENDER UCHUN SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Ishlamoqda!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def admin_keyboard():
    buttons = [
        [types.KeyboardButton("📊 Statistika"), types.KeyboardButton("✉️ Xabar yuborish")],
        [types.KeyboardButton("🎬 Kinolar"), types.KeyboardButton("🔐 Kanallar")],
        [types.KeyboardButton("👤 Adminlar"), types.KeyboardButton("⚙️ Sozlamalar")],
        [types.KeyboardButton("⬅️ Orqaga")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=admin_keyboard())
    else:
        await message.answer("👋 Salom! Kino kodini yuboring...")

@dp.message_handler(lambda m: m.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📊 Statistika: 1 foydalanuvchi.")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
