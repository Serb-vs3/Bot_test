import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import handle_all_updates, start
from aiogram.filters import CommandStart
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("__main__.log"), logging.StreamHandler()]
)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
@dp.message()
async def handle_message(message):
    await handle_all_updates(message, bot)
@dp.message(CommandStart())
async def start_command(message):
    await start(message)
async def main():
    try:
        logging.info("Бот запущен и работает...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Глобальная ошибка в main(): {e}", exc_info=True)
        await asyncio.sleep(5)
if __name__ == "__main__":
    asyncio.run(main())
