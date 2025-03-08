import asyncio
from main import dp, bot
from voice_handler import handle_voice, handle_text
from aiogram import F
from aiogram import types
from aiogram.filters.command import Command
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправьте мне голосовое сообщение.")


async def main():
    dp.message(F.voice)(handle_voice)
    dp.message(F.text)(handle_text)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
