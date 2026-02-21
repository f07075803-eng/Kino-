import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from flask import Flask
from threading import Thread
import os

# --- KONFIGURATSIYA ---
API_TOKEN = '8599100876:AAGhk-U0gLCKNUAEf5Q1qThzsaAH-WHYmmA'
ADMIN_ID = 7257755738
CHANNELS = ['@SizningKanalingiz'] # Majburiy obuna kanallarini shu yerga yozing

# Ma'lumotlarni saqlash (Vaqtinchalik, MongoDB ulanmaguncha)
movies_db = {} 
users_list = set()

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Faol!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run, daemon=True).start()

# --- BOT ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class AdminStates(StatesGroup):
    waiting_for_movie = State()
    waiting_for_code = State()
    waiting_for_ad = State()

# Tugmalar
def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📊 Statistika", "✉️ Xabar yuborish")
    kb.row("🎬 Kino qo'shish", "🔐 Kanallar")
    kb.add("⬅️ Orqaga")
    return kb

# Obunani tekshirish funksiyasi
async def check_sub(user_id):
    for channel in CHANNELS:
        status = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if status.status == 'left':
            return False
    return True

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    users_list.add(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin panel", reply_markup=admin_kb())
    else:
        if await check_sub(message.from_user.id):
            await message.answer("🍿 Kino kodini yuboring...")
        else:
            btn = types.InlineKeyboardMarkup()
            for ch in CHANNELS:
                btn.add(types.InlineKeyboardButton(text="Kanalga a'zo bo'lish", url=f"https://t.me/{ch[1:]}"))
            btn.add(types.InlineKeyboardButton(text="Tekshirish ✅", callback_data="check"))
            await message.answer("❌ Kino ko'rish uchun kanallarga a'zo bo'ling!", reply_markup=btn)

# Kino qo'shish jarayoni
@dp.message_handler(lambda m: m.text == "🎬 Kino qo'shish", user_id=ADMIN_ID)
async def add_movie_start(message: types.Message):
    await AdminStates.waiting_for_movie.set()
    await message.answer("Videoni yuboring...")

@dp.message_handler(content_types=['video'], state=AdminStates.waiting_for_movie)
async def get_video(message: types.Message, state: FSMContext):
    await state.update_data(file_id=message.video.file_id)
    await AdminStates.waiting_for_code.set()
    await message.answer("Kino uchun kod yozing:")

@dp.message_handler(state=AdminStates.waiting_for_code)
async def get_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    movies_db[message.text] = data['file_id']
    await state.finish()
    await message.answer(f"✅ Saqlandi! Kod: {message.text}", reply_markup=admin_kb())

# Xabar yuborish (Reklama)
@dp.message_handler(lambda m: m.text == "✉️ Xabar yuborish", user_id=ADMIN_ID)
async def send_ad_start(message: types.Message):
    await AdminStates.waiting_for_ad.set()
    await message.answer("Reklama xabarini yuboring (rasm, matn, video)...")

@dp.message_handler(state=AdminStates.waiting_for_ad, content_types=types.ContentTypes.ANY)
async def start_broadcasting(message: types.Message, state: FSMContext):
    count = 0
    for user in users_list:
        try:
            await message.copy_to(user)
            count += 1
        except: pass
    await state.finish()
    await message.answer(f"✅ Reklama {count} kishiga yuborildi.")

# Kino qidirish
@dp.message_handler()
async def search(message: types.Message):
    if message.text in movies_db:
        if await check_sub(message.from_user.id):
            await bot.send_video(message.chat.id, movies_db[message.text])
        else:
            await message.answer("Avval kanallarga a'zo bo'ling!")
    else:
        if message.from_user.id != ADMIN_ID:
            await message.answer("Kino topilmadi ❌")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
            
