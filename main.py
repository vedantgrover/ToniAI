from dotenv import load_dotenv

from voice_synthesis import *
from voice_input import *
from intelligence import *
from pydub import AudioSegment
from pydub.playback import play
import pvporcupine
import os

from playsound import playsound

if __name__ == "__main__":
    user_input: str = ""

    while True:
        user_input = get_audio()
        print(user_input)

        if user_input.lower() == "quit":
            break

        chat_response = get_chat_response(user_input)
        print(chat_response)
        create_voice_file(chat_response)

        print("Playing Response...")
        playsound("output.wav")
