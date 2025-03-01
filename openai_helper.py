import openai
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
openai.api_key = OPENAI_API_KEY
async def get_assistant_response(text: str):
    try:
        thread = await openai.beta.threads.create()
        await openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text
        )
        run = await openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID  
        )
        while True:
            run_status = await openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            await asyncio.sleep(1) 
        messages = await openai.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
    except Exception as e:
        return f"Произошла ошибка при обработке запроса: {str(e)}"
async def transcribe_audio(audio_file):
    try:
        response = await openai.Audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return response.text 
    except Exception as e:
        return f"Ошибка при транскрипции аудио: {str(e)}"
async def text_to_speech(text: str):
    try:
        response = await openai.Audio.speech.create(  
            model="tts-1",
            input=text,
            voice="alloy"  
        )
        return response
    except Exception as e:
        return f"Ошибка при генерации речи: {str(e)}"
