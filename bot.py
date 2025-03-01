import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from aiogram.types import Message
from aiogram.filters import Command
from handlers import handle_all_updates, start, voice_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("__main__.log"), logging.StreamHandler()]
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))  # Обработчик команды "/start"
async def start_command(message: Message):
    await start(message)

@dp.message(lambda message: message.content_type == "text")  # Обработчик всех текстовых сообщений
async def handle_text_message(message: Message):
    if message.text:
        await handle_all_updates(message, bot)
    

@dp.message(lambda message: message.content_type == "voice")  # Обработчик голосовых сообщений
async def handle_voice_message(message: Message):
    try:
        logging.info(f"Получено голосовое сообщение: {message.voice.file_id}")
        await voice_handler(message, bot)
    except Exception as e:
        logging.error(f"Ошибка при обработке голосового сообщения: {e}", exc_info=True)
        await message.answer("Возникла ошибка при обработке голосового сообщения.")

async def main():
    try:
        logging.info("Бот запущен и работает...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Глобальная ошибка в main(): {e}", exc_info=True)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
