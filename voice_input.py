import os

import pyaudio
from pydub import AudioSegment
import openai

openai.api_key = os.getenv("OPENAI")

CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit)
CHANNELS = 1  # Mono audio
RATE = 44100  # Sampling rate (samples per second)
RECORD_SECONDS = 5 # Duration of recording

def get_audio():
    # Getting Audio
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []

    print("Recording started...")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_segment = AudioSegment(
        data=b"".join(frames),
        sample_width=audio.get_sample_size(FORMAT),
        channels=CHANNELS,
        frame_rate=RATE
    )

    MP3_OUTPUT_FILENAME = "voice_input.mp3"
    audio_segment.export(MP3_OUTPUT_FILENAME, format="mp3")

    # Converting to Text
    audio_file = open("voice_input.mp3", "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    print(transcript)
