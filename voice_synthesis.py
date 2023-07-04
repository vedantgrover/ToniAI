import requests
import os
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = 1024


def create_voice_file(text: str):
    url = "https://api.elevenlabs.io/v1/text-to-speech/JD1jiNioKc79QJXOlhRH"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.getenv("ELEVENLABS")
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.wav', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
