import logging
import asyncio
from aiogram import types
from aiogram.types import FSInputFile
from config import openai_client
from aiogram import Bot
from openai import AsyncOpenAI
import os
import tempfile
async def handle_all_updates(message: types.Message, bot: Bot):
    logging.info(f"Обновление id={message.message_id} получено. Тип: {message.content_type}")
    if message.text == "/start":
        await start(message)
        return
    if message.content_type == "text":
        warning_msg = await message.answer("Пожалуйста, отправь голосовое сообщение!")
        await asyncio.sleep(2)
        await message.delete()
        await warning_msg.delete()
        return
    elif message.content_type == "voice":
        await voice_handler(message, bot)
async def start(message: types.Message):
    try:
        await message.answer("Привет! Отправь мне голосовое сообщение, и я отвечу!")
    except Exception as e:
        logging.error(f"Ошибка в обработчике start: {e}", exc_info=True)
        await message.answer("Возникла ошибка, попробуйте снова.")
async def voice_handler(message: types.Message, bot: Bot):
    try:
        processing_msg = await message.answer("Обрабатываю голосовое сообщение...")
        voice = message.voice
        file = await bot.get_file(voice.file_id)
        file_path = file.file_path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
            temp_file_path = temp_file.name
            await bot.download_file(file_path, temp_file_path)
        with open(temp_file_path, "rb") as audio_file:
            transcript = await openai_client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        text = transcript.text
        os.remove(temp_file_path)
        response = await openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": text}]
        )
        reply_text = response.choices[0].message.content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts_file_path = temp_file.name
            tts_audio = await openai_client.audio.speech.create(
                model="tts-1", voice="alloy", input=reply_text
            )
            with open(tts_file_path, "wb") as f:
                f.write(tts_audio.content)

            audio = FSInputFile(tts_file_path)
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
            await message.answer_voice(audio)
    except Exception as e:
        logging.error(f"Ошибка в voice_handler: {e}", exc_info=True)
        await message.answer("Возникла ошибка, попробуйте снова.")
