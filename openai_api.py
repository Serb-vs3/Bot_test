import openai
import aiohttp
from io import BytesIO
from config import OPENAI_API_KEY, ASSISTANT_ID

openai.api_key = OPENAI_API_KEY
openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def transcribe_audio(file_path: str) -> str:
    try:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        form = aiohttp.FormData()
        form.add_field("file", open(file_path, "rb"), filename="voice.ogg")
        form.add_field("model", "whisper-1")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=form) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("text", "Ошибка распознавания")
    except Exception as e:
        return f"Ошибка при распознавании аудио: {str(e)}"

async def get_assistant_response(user_message: str) -> str:
    try:
        thread = await openai_client.beta.threads.create()
        await openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        run = await openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            run_status = await openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            if run_status.status == "requires_action":
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": tool_call.function.arguments
                    })

                await openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run_status.status == "completed":
                break

        messages = await openai_client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value

    except Exception as e:
        return f"Ошибка: {str(e)}"

async def text_to_speech(text: str) -> BytesIO:
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "input": text,
            "voice": "alloy"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    audio_bytes = await response.read()
                    return BytesIO(audio_bytes)

    except Exception as e:
        return None
