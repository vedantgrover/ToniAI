from dotenv import  load_dotenv

from voice_synthesis import *
#from voice_input import *
from intelligence import *
from pydub import AudioSegment
from pydub.playback import play
import pvporcupine
import os

from playsound import  playsound

load_dotenv()
porcupine = pvporcupine.create(
    access_key=os.getenv("PVPORCUPINE"),
    keyword_paths=["toni.ppn"]
)
if __name__ == "__main__":
    user_input = input("Input:> ")

    create_voice_file(get_chat_response(user_input))

    print("Playing Response...")
    playsound("output.wav")


