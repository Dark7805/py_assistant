import os
from text_to_speech import speak

def play_music():
    os.system("start wmplayer")  # Windows Media Player
    speak("Playing music")

def exit_program():
    speak("Goodbye!")
    exit()
