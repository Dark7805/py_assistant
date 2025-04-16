import os
import time
import json
import speech_recognition as sr
from text_to_speech import speak  # Importing speak from centralized TTS

# Path to save user data
USER_DATA_PATH = "user_data.json"

# Function to capture oral input (speech recognition)
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you please repeat?")
        return ""
    except sr.RequestError:
        speak("Sorry, the speech service is not available at the moment.")
        return ""

# Function to greet the user based on the time of day
def greet_user(name, interests):
    hour = time.localtime().tm_hour

    # Construct the greeting based on the time of day
    if hour < 12:
        greeting = f"Good morning, {name}!"
    elif hour < 18:
        greeting = f"Good afternoon, {name}!"
    else:
        greeting = f"Good evening, {name}!"

    # Print and speak the greeting
    print(greeting)
    speak(greeting)  # Speak the greeting only
    print(f"Your interests: {interests}")
    speak(f"Your interests are {interests}.")  # Optionally, speak the interests

# Function to initialize greeting
def initialize_greeting():
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, 'r') as file:
            user_data = json.load(file)
        name = user_data.get("name")
        interests = user_data.get("interests")
        greet_user(name, interests)
        
        print(f"Your interests: {interests}")
    else:
        speak("Hello! What is your name?")
        name = recognize_speech()

        speak("What are you interested in?")
        interests = recognize_speech()

        # Debug: Print recognized interests to check
        print(f"Recognized interests: {interests}")

        user_data = {
            "name": name,
            "interests": interests
        }
        with open(USER_DATA_PATH, 'w') as file:
            json.dump(user_data, file)

        greet_user(name, interests)
        print(f"Your interests: {interests}")

# App opening prompt (separate)
def openingApp():
    speak("Opening the app. Please wait.")
