import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import socket
import wikipedia  # Import Wikipedia module
import app_launcher  # Import the app launcher module
import pyttsx3  # Import pyttsx3 for text-to-speech
import threading  # Import threading for background tasks
from greeting import initialize_greeting

# Initialize the TTS engine
engine = pyttsx3.init()

# Function to check internet connection
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)  # Check for internet
        return True
    except OSError:
        return False


# Function for Google Speech Recognition (Online)
def recognize_google_online():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for Google (Online)...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print("You said (Google):", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand (Google).")
        return ""
    except sr.RequestError:
        print("Could not request results from Google (Online).")
        return ""


# Function for Vosk Speech Recognition (Offline)
def recognize_vosk_offline():
    model = Model(r"D:\Code\Python_Project\vosk-model-small-en-us-0.15")  # Absolute path to the Vosk model
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Listening for Vosk (Offline)...")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            print("You said (Vosk):", text)
            return text


# Function to search Wikipedia
def search_wikipedia(query):
    try:
        print(f"Searching Wikipedia for: {query}")
        summary = wikipedia.summary(query, sentences=2)  # Get a short summary of the page
        print("Wikipedia Search Result:", summary)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        print("Disambiguation Error:", e.options)
        return "Could not find a specific result, please be more specific."
    except wikipedia.exceptions.HTTPError:
        return "There was an issue with Wikipedia. Please check your connection."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Function for TTS (Text-to-Speech)
def speak(text):
    engine.say(text)  # Convert text to speech
    engine.runAndWait()  # Wait for the speech to finish


# Function to open applications in a separate thread (non-blocking)
def open_application_in_background(command):
    thread = threading.Thread(target=app_launcher.handle_application, args=(command,))
    thread.start()



# Main function to choose the recognition method based on internet connection
def recognize_speech():
    if is_connected():  # If connected to the internet
        return recognize_google_online()  # Use Google
    else:
        return recognize_vosk_offline()  # Use Vosk for offline
    

# Function to stop the program (Gracefully)
def stop_program():
    global running
    running = False 

# Main Program: Loop to keep the app running until "stop" is said
def run_app():
    initialize_greeting()
    print("Say the name of the app you want to open, or ask for information... or say 'stop' to exit.")
    speak("Say the name of the app you want to open, or ask for information... or say 'stop' to exit.")  # Assistant speaks this
    
    while True:  # Keep running until the "stop" command is recognized
        command = recognize_speech()  # Get the voice command
        
        if "stop" in command:
            print("Stopping the application.")
            speak("Stopping the application.")
            stop_program()
            break  # Exit the loop if "stop" is said
        
        if "search wikipedia" in command:  # Check if the user wants to search Wikipedia
            query = command.replace("search wikipedia", "").strip()
            if query:
                result = search_wikipedia(query)  # Search Wikipedia
                speak(result)  # Assistant speaks the result
            else:
                speak("Please say the topic you want to search for.")
        
        elif "who is" in command or "what is" in command:  # Detect information queries (e.g., who is Virat Kohli)
            query = command.replace("who is", "").replace("what is", "").strip()
            if query:
                result = search_wikipedia(query)  # Search Wikipedia
                speak(result)  # Assistant speaks the result
            else:
                speak("Please specify a person or topic to search for.")
        
        else:
            open_application_in_background(command)  # Open the application in the background
            continue  # Continue listening for new commands after task completion


if __name__ == "__main__":
    run_app()  # Start the app and keep listening until "stop" is said
