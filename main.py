import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import socket
import wikipedia
import app_launcher
import pyttsx3
import threading
import queue
import requests
from greeting import initialize_greeting

# Initialize the TTS engine
engine = pyttsx3.init()
speech_queue = queue.Queue()

# Function to check internet connection
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

# Function for Google Speech Recognition (Online)
def recognize_google_online():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        speak("Hmm, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        speak("Oops! I can't connect to Google right now. Let's try something else.")
        return ""

# Function for Vosk Speech Recognition (Offline)
def recognize_vosk_offline():
    model = Model(r"D:\\Code\\Python_Project\\vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Listening (Offline)...")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            print("You said:", text)
            return text

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        print(f"Searching Wikipedia for: {query}")
        summary = wikipedia.summary(query, sentences=2)
        print("Wikipedia says:", summary)
        return summary
    except wikipedia.exceptions.DisambiguationError:
        return "That topic has multiple meanings. Could you specify a bit more?"
    except wikipedia.exceptions.HTTPError:
        return "I'm having trouble reaching Wikipedia right now. Try again later."
    except Exception:
        return "Sorry, I couldn't find anything on that topic."

# Function to get specific smart responses from Wolfram Alpha
def get_smart_response(command):
    api_url = "http://api.wolframalpha.com/v1/result?appid=YOUR_APP_ID&i=" + command
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.text
        return "I'm sorry, I couldn't find a direct answer to that."
    except:
        return "I'm having trouble retrieving data. Try again later."

# Function to open or close applications in the background
def open_or_close_application(command):
    print(f"Attempting to handle app command: {command}")  # Debugging line
    thread = threading.Thread(target=app_launcher.handle_application, args=(command,))
    thread.start()

# Function for TTS (Text-to-Speech)
def speak(text):
    print("Speaking:", text)
    engine.say(text)
    engine.runAndWait()

# Main function to recognize speech
def recognize_speech():
    if is_connected():
        return recognize_google_online()
    else:
        return recognize_vosk_offline()

# Function to stop the program
def stop_program():
    global running
    running = False 

# Main Program
def run_app():
    initialize_greeting()
    speak("Hello! How may I assist you today?")
    
    while True:
        command = recognize_speech()

        if "stop" in command:
            speak("Alright, shutting down. Talk to you later!")
            stop_program()
            break 
        
        # Handle Smart Responses
        if "highest score of" in command:
            entity = command.replace("highest score of", "").strip()
            response = get_smart_response(f"highest score of {entity}")
            speak(response)
            continue
        
        # Search Wikipedia for specific queries
        if "search wikipedia" in command:
            query = command.replace("search wikipedia", "").strip()
            if query:
                result = search_wikipedia(query)
                speak(result)
            else:
                speak("What would you like to search for?")
        
        elif "who is" in command or "what is" in command:
            query = command.replace("who is", "").replace("what is", "").strip()
            if query:
                result = search_wikipedia(query)
                speak(result)
            else:
                speak("Can you specify the topic a bit more?")
        
        elif "how are you" in command:
            speak("I'm feeling fantastic! How about you?")
        
        elif "tell me a joke" in command:
            speak("Why did the computer catch a cold? Because it left its Windows open!")
        
        elif "thank you" in command:
            speak("You're very welcome! Always happy to help.")
        
        elif "open" in command or "close" in command:
            open_or_close_application(command)
        
        else:
            speak("Got it! Let me take care of that for you.")
            
if __name__ == "__main__":
    run_app()
