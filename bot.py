import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from openai import OpenAI
from dotenv import load_dotenv
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("__main__.log"),  
        logging.StreamHandler()  
    ]
)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
openai_client = OpenAI(api_key=OPENAI_API_KEY)
@dp.message(CommandStart())
async def start(message: Message):
    try:
        await message.answer("Привет! Отправь мне голосовое сообщение, и я отвечу!")
    except Exception as e:
        logging.error(f"Ошибка в обработчике start: {e}", exc_info=True)
        await message.answer("Возникла ошибка, попробуйте снова.")
@dp.message()
async def voice_handler(message: Message):
    try:
        if not message.voice:
            warning_msg = await message.answer("Пожалуйста, отправь голосовое сообщение!")
            await asyncio.sleep(2) 
            await message.delete() 
            await warning_msg.delete() 
            return
        processing_msg = await message.answer("Обрабатываю голосовое сообщение...")  
        voice = message.voice
        file = await bot.get_file(voice.file_id)
        file_path = file.file_path
        ogg_file = f"voice_{message.from_user.id}.ogg"
        await bot.download_file(file_path, ogg_file)
        with open(ogg_file, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        text = transcript.text
        os.remove(ogg_file)  
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": text}]
        )
        reply_text = response.choices[0].message.content
        tts_file = f"reply_{message.from_user.id}.mp3"
        tts_audio = openai_client.audio.speech.create(
            model="tts-1", voice="alloy", input=reply_text
        )
        with open(tts_file, "wb") as f:
            f.write(tts_audio.content)
        audio = FSInputFile(tts_file)  
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id) 
        await message.answer_voice(audio)
        os.remove(tts_file)
    except Exception as e:
        logging.error(f"Ошибка в voice_handler: {e}", exc_info=True)
        await message.answer("Возникла ошибка, попробуйте снова.")
async def main():
    while True:
        try:
            logging.info("Бот запущен и работает...")
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Глобальная ошибка в main(): {e}", exc_info=True)
            await asyncio.sleep(5)  
if __name__ == "__main__":
    asyncio.run(main())