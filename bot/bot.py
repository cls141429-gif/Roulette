# bot/bot.py
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from aiogram import types
from dotenv import load_dotenv
from game_storage import load_users, save_users

load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL") or "https://your-domain.example/web/"

if not API_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"balance": 1000}
        save_users(users)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(text="Play LuckyJet", web_app=WebAppInfo(url=WEB_APP_URL))
    keyboard.add(btn)
    await message.answer(
        "Привет! Это демо LuckyJet. Баланс хранится локально. Никаких реальных денег.",
        reply_markup=keyboard
    )

@dp.message(Command(commands=["balance"]))
async def cmd_balance(message: types.Message):
    users = load_users()
    uid = str(message.from_user.id)
    bal = users.get(uid, {"balance":0})["balance"]
    await message.answer(f"Твой баланс: {bal} монет")

@dp.message(Command(commands=["give"]))
async def cmd_give(message: types.Message):
    users = load_users()
    uid = str(message.from_user.id)
    users.setdefault(uid, {"balance":0})
    users[uid]["balance"] += 100
    save_users(users)
    await message.answer("Выданы +100 монет (демо)")

@dp.message()
async def default_msg(message: types.Message):
    if message.text == "Play LuckyJet":
        await message.answer("Открой Web App кнопку ниже", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text="Play LuckyJet", web_app=WebAppInfo(url=WEB_APP_URL))))
    else:
        await message.reply("Используй /start, /balance или /give")

if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
