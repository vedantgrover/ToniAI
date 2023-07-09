import os
from dotenv import load_dotenv

import pyaudio
import wave
import struct
import pvporcupine
import openai

openai.api_key = os.getenv("OPENAI")

CHUNK = 512  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit)
CHANNELS = 1  # Mono audio
RATE = 16000  # Sampling rate (samples per second)

# Recording Parameters
MAX_RECORD_DURATIONS = 10  # Maximum recording duration
SILENCE_THRESHOLD = 3  # Stops recording after three seconds of silence
SILENCE_CHUNK = int(RATE / CHUNK)
SILENCE_LEVEL = 200

load_dotenv()
porcupine = pvporcupine.create(
    access_key=os.getenv("PVPORCUPINE"),
    keyword_paths=["wake_model/toni_wake_model.ppn"]
)


def get_audio():
    # Getting Audio
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    silence_counter = 0
    is_recording = False

    print("Listening for hotwords...")
    while True:
        # Read audio data from the stream
        audio_data = stream.read(CHUNK)

        # Convert audio data to an array of signed shorts
        pcm = struct.unpack_from("h" * CHUNK, audio_data)

        rms_energy = sum([abs(x) for x in pcm]) / CHUNK

        # Pass audio data to PVPorcupine for hotword detection
        keyword_index = porcupine.process(pcm)

        # Check if a hotword is detected
        if keyword_index >= 0:
            if not is_recording:
                # Start recording
                print("Recording started...")
                is_recording = True
            silence_counter = 0

        # Record audio frames if hotword is detected
        if is_recording:
            frames.append(audio_data)

            # Check for silence and stop recording if silence threshold is reached
            if rms_energy < SILENCE_LEVEL:
                silence_counter += 1
                if silence_counter >= SILENCE_CHUNK:
                    print("Silence threshold reached. Recording finished.")
                    break
            else:
                silence_counter = 0

    stream.stop_stream()
    stream.close()
    audio.terminate()

    WAVE_INPUT_FILENAME = "input.wav"
    wf = wave.open(WAVE_INPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    # Converting to Text
    audio_file = open(WAVE_INPUT_FILENAME, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript.text
