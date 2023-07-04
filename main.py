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
    print(get_audio())
