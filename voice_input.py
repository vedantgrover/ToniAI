import os

import pyaudio
import wave
import struct
import pvporcupine
import openai

openai.api_key = os.getenv("OPENAI")

CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit)
CHANNELS = 1  # Mono audio
RATE = 16000  # Sampling rate (samples per second)
HOT_WORDS = ["Toni"]

# Recording Parameters
MAX_RECORD_DURATIONS=10 # Maximum recording duration
SILENCE_THRESHOLD = 3 # Stops recording after three seconds of silence
SILENCE_CHUNK = int(RATE/CHUNK)

porcupine = pvporcupine.create(
    access_key=os.getenv("PVPORCUPINE"),
    keywords=HOT_WORDS
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

        # Pass audio data to PVPorcupine for hotword detection
        keyword_index = porcupine.process(pcm)

        # Check if a hotword is detected
        if keyword_index >= 0:
            if not is_recording:
                # Start recording
                recording = True
                print(f"Hotword '{HOT_WORDS[keyword_index]}' detected! Recording started...")
            silence_counter = 0

        # Record audio frames if hotword is detected
        if is_recording:
            frames.append(audio_data)

            # Check for silence and stop recording if silence threshold is reached
            if audio_data.count(b"\x00") == len(audio_data):
                silence_counter += 1
                if silence_counter >= SILENCE_CHUNK:
                    print("Silence threshold reached. Recording finished.")
                    break
            else:
                silence_counter = 0

    stream.stop_stream()
    stream.close()
    audio.terminate()

    WAVE_OUTPUT_FILENAME = "output.wav"
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    # Converting to Text
    audio_file = open(WAVE_OUTPUT_FILENAME, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript.text
