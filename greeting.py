import os
import time
import json
import pyttsx3
import speech_recognition as sr



# Initialize the TTS engine
engine = pyttsx3.init()

# Path to save user data
USER_DATA_PATH = "user_data.json"

def speak(text):
    engine.say(text)  # Convert text to speech
    engine.runAndWait()  # Wait for the speech to finish

# Function to capture oral input (speech recognition)
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)


# Function to greet the user based on the time of day
def greet_user(name):
    current_time = time.localtime()
    hour = current_time.tm_hour

    if hour < 12:
        greeting = f"Good morning, {name}!"
    elif hour < 18:
        greeting = f"Good afternoon, {name}!"
    else:
        greeting = f"Good evening, {name}!"

    print(greeting)
    engine.say(greeting)
    engine.runAndWait()

# Function to initialize greeting by checking if user details are saved
def initialize_greeting():
    if os.path.exists(USER_DATA_PATH):
        # Load user data from the file
        with open(USER_DATA_PATH, 'r') as file:
            user_data = json.load(file)
        name = user_data.get("name")
        interests = user_data.get("interests")
        greet_user(name)  # Greet the user by name
        print(f"Your interests: {interests}")  # Optionally print or use the interests
    else:
        # If no user data is found, ask for name and interests
        
        speak("Hello! What is your name? ")
        name = recognize_speech()
        interests = speak("What are you interested in? ")

        # Save the user data to a file
        user_data = {
            "name": name,
            "interests": interests
        }
        with open(USER_DATA_PATH, 'w') as file:
            json.dump(user_data, file)

        greet_user(name)  # Greet the user by name
        print(f"Your interests: {interests}")  # Optionally print or use the interests
