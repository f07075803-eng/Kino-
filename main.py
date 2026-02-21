import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# --- KONFIGURATSIYA ---
API_TOKEN = '8599100876:AAGhk-U0gLCKNUAEf5Q1qThzsaAH-WHYmmA'
ADMIN_ID = 7257755738
CHANNELS = ["@u_uz_channel"]  # Majburiy a'zolik uchun kanallar (userneymini yozing)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Ma'lumotlar bazasi o'rniga oddiy lug'at (Real loyihada SQLite yoki MongoDB yaxshiroq)
movies_db = {
    "101": {"name": "O'rgimchak odam", "link": "https://t.me/your_channel/1"},
    "102": {"name": "Qasoskorlar", "link": "https://t.me/your_channel/2"},
}

class AdminStates(StatesGroup):
    waiting_for_movie_data = State()

# --- FUNKSIYALAR ---
async def check_sub(user_id):
    """Kanallarga a'zolikni tekshirish"""
    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if chat_member.status == 'left':
            return False
    return True

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    is_sub = await check_sub(message.from_user.id)
    if is_sub:
        await message.answer(f"Xush kelibsiz, {message.from_user.full_name}!\n"
                             f"Kino kodini kiriting:")
    else:
        btn = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            btn.add(types.InlineKeyboardButton(text="Kanalga o'tish", url=f"https://t.me/{ch[1:]}"))
        btn.add(types.InlineKeyboardButton(text="Tekshirish", callback_data="check"))
        await message.answer("Botdan foydalanish uchun kanallarga a'zo bo'ling:", reply_markup=btn)

@dp.callback_query_handler(text="check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("Rahmat! Endi kino kodini yuborishingiz mumkin.")
    else:
        await call.answer("Hali a'zo emassiz!", show_alert=True)

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin xush kelibsiz! Yangi kino qo'shish uchun format:\n"
                             "<code>kod|nomi|link</code> ko'rinishida yozing.")
        await AdminStates.waiting_for_movie_data.set()

@dp.message_handler(state=AdminStates.waiting_for_movie_data)
async def add_movie(message: types.Message, state: FSMContext):
    try:
        data = message.text.split('|')
        movies_db[data[0]] = {"name": data[1], "link": data[2]}
        await message.answer(f"Kino saqlandi: {data[1]}")
    except:
        await message.answer("Xato! Format: kod|nomi|link")
    await state.finish()

@dp.message_handler()
async def search_movie(message: types.Message):
    code = message.text
    if code in movies_db:
        movie = movies_db[code]
        await message.answer(f"🎬 <b>Nomi:</b> {movie['name']}\n\n"
                             f"📥 <b>Yuklab olish:</b> {movie['link']}")
    else:
        await message.answer("Afsuski, bu kod bilan hech qanday kino topilmadi. 😔")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
