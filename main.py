import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = '8599100876:AAGhk-U0gLCKNUAEf5Q1qThzsaAH-WHYmmA'
ADMIN_ID = 7257755738
CHANNELS = ["@u_uz_channel"] # Kanal userneymini @ bilan yozing

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Vaqtinchalik ma'lumotlar bazasi
movies_db = {
    "101": "https://t.me/c/123456/1",
    "102": "https://t.me/c/123456/2"
}

# --- FUNKSIYALAR ---
async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            # Agar bot kanalda admin bo'lmasa yoki kanal topilmasa
            return False
    return True

# --- HANDLERLAR ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    is_sub = await check_subscription(message.from_user.id)
    if is_sub:
        await message.answer(f"Xush kelibsiz! Kino kodini yuboring.")
    else:
        buttons = [
            [InlineKeyboardButton(text="Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNELS[0][1:]}")],
            [InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Botdan foydalanish uchun kanalga a'zo bo'ling:", reply_markup=keyboard)

@dp.callback_query(F.data == "check_sub")
async def check_callback(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.edit_text("Rahmat! Endi kod yuborishingiz mumkin.")
    else:
        await call.answer("Siz hali a'zo emassiz!", show_alert=True)

@dp.message(F.text)
async def get_movie(message: types.Message):
    code = message.text
    if code in movies_db:
        await message.answer(f"🎬 Siz izlagan kino: {movies_db[code]}")
    else:
        await message.answer("Bunday kodli kino topilmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
