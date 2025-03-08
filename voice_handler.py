import logging
from aiogram import types
from main import bot
from openai_api import transcribe_audio, get_assistant_response, text_to_speech
import aiohttp
from dotenv import load_dotenv
import os
load_dotenv() 
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
async def download_voice(voice: types.Voice) -> str:
    try:
        file_info = await bot.get_file(voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    file_name = "voice.ogg"
                    with open(file_name, "wb") as f:
                        f.write(await response.read())
                    return file_name
    except Exception as e:
        logging.error(f"Ошибка при загрузке голосового сообщения: {str(e)}")
    return None

async def handle_voice(message: types.Message):
    
    voice_file = await download_voice(message.voice)
    if not voice_file:
        await message.reply("Ошибка загрузки голосового сообщения.")
        return
    
    text = await transcribe_audio(voice_file)
    response_text = await get_assistant_response(text)
    
    audio_data = await text_to_speech(response_text)
    if audio_data:
        await message.reply_voice(types.BufferedInputFile(audio_data.getvalue(), filename="response.ogg"))
    else:
        await message.reply("Ошибка генерации аудио ответа.")

async def handle_text(message: types.Message):
    await message.reply("Отправьте мне голосовое сообщение.")
