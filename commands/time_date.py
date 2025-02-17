import datetime
from text_to_speech import speak

def get_time():
    current_time = datetime.datetime.now().strftime("%H:%M")
    speak(f"The time is {current_time}")

def get_date():
    today = datetime.date.today().strftime("%B %d, %Y")
    speak(f"Today's date is {today}")
