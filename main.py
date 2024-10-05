import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
import dotenv
import os

from aiogram.types import Message

from ai import FlowerAI
from db import FlowerDatabase

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ['TELEGRAM_API_TOKEN'])
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello!")


@dp.message(Command("my_orders"))
async def cmd_start(message: Message):
    await message.answer(str(db.get_orders(message.chat.id)))


@dp.message(F.text)
async def client_conversation(message: Message):
    chat_id = message.chat.id
    db.add_message_buffer(message.text, message.chat.id, True)
    history = db.get_all_messages(chat_id)
    history_text = "".join([f"{'User' if i[3] else 'Bot'}: {i[2]}\n" for i in history])
    ai = FlowerAI()
    reponse = await ai.client_conversation(message.chat.id, message.text, history_text)
    await message.answer(reponse, parse_mode="HTML")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    db = FlowerDatabase()
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception(e)
    finally:
        db.close()
