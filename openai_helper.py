import openai
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
async def get_assistant_response(text: str):
    try:
        response = await openai.ChatCompletion.create(
            model="gpt-4",  
            messages=[{"role": "user", "content": text}],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Произошла ошибка при обработке запроса: {str(e)}"
async def transcribe_audio(audio_file):
    try:
        response = await openai.Audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return response['text']
    except Exception as e:
        return f"Ошибка при транскрипции аудио: {str(e)}"
async def text_to_speech(text: str):
    try:
        response = await openai.Audio.create(
            model="whisper-1", 
            input=text
        )
        return response 
    except Exception as e:
        return f"Ошибка при генерации речи: {str(e)}"
