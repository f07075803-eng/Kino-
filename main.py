import logging
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

# Vaqtinchalik baza (Render o'chib yonsa tozalanadi, lekin hozir ishlashini ko'rasiz)
movies_db = {}
users_db = set()

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Active!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run, daemon=True).start()

# --- BOT SOZLAMALARI ---
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Kino qo'shish bosqichlari
class MovieState(StatesGroup):
    waiting_for_video = State()
    waiting_for_code = State()

# Tugmalar
def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📊 Statistika", "✉️ Xabar yuborish")
    kb.row("🎬 Kino qo'shish", "🔐 Kanallar")
    kb.add("⬅️ Orqaga")
    return kb

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    users_db.add(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin paneliga xush kelibsiz!", reply_markup=admin_kb())
    else:
        await message.answer("🍿 Salom! Kino kodini yuboring...")

# --- KINO QO'SHISH FUNKSIYASI ---

@dp.message_handler(lambda m: m.text == "🎬 Kino qo'shish", user_id=ADMIN_ID)
async def start_add(message: types.Message):
    await MovieState.waiting_for_video.set()
    await message.answer("🎬 Menga videoni (kino) yuboring...")

@dp.message_handler(content_types=['video'], state=MovieState.waiting_for_video)
async def get_video(message: types.Message, state: FSMContext):
    await state.update_data(vid_id=message.video.file_id)
    await MovieState.waiting_for_code.set()
    await message.answer("✅ Video qabul qilindi. Endi bu kino uchun **KOD** yuboring (masalan: 101):")

@dp.message_handler(state=MovieState.waiting_for_code)
async def get_code(message: types.Message, state: FSMContext):
    code = message.text
    data = await state.get_data()
    movies_db[code] = data['vid_id'] # Bazaga saqlash
    await state.finish()
    await message.answer(f"🚀 Tayyor! Endi kim botga `{code}` deb yozsa, ushbu kino yuboriladi.", reply_markup=admin_kb())

# --- STATISTIKA ---
@dp.message_handler(lambda m: m.text == "📊 Statistika", user_id=ADMIN_ID)
async def show_stats(message: types.Message):
    await message.answer(f"📊 Statistika:\n👤 Foydalanuvchilar: {len(users_db)}\n🎬 Kinolar: {len(movies_db)}")

# --- KINO QIDIRISH (HAMMA UCHUN) ---
@dp.message_handler()
async def search(message: types.Message):
    code = message.text
    if code in movies_db:
        await bot.send_video(message.chat.id, movies_db[code], caption=f"🎬 Kod: {code}")
    elif message.from_user.id == ADMIN_ID:
        pass # Admin tugmalari uchun
    else:
        await message.answer("❌ Bunday kodli kino topilmadi.")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
    
