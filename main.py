import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import socket
import wikipedia
import app_launcher
import threading
import queue
import time
from greeting import initialize_greeting, openingApp
from text_to_speech import speak  # Centralized TTS import
from fuzzywuzzy import fuzz

# Queues for async handling
app_result_queue = queue.Queue()

def is_connected():
    """Check internet connectivity"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def recognize_google_online():
    """Online voice recognition using Google API"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening (Online)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            return recognizer.recognize_google(audio).lower()
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return ""

def recognize_vosk_offline():
    """Offline voice recognition using Vosk"""
    model = Model(r"D:\\Code\\Python_Project\\vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                     input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Listening (Offline)...")
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            text = json.loads(recognizer.Result()).get("text", "").lower()
            stream.stop_stream()
            stream.close()
            mic.terminate()
            return text

def recognize_speech():
    """Choose between online and offline speech recognition"""
    return recognize_google_online() if is_connected() else recognize_vosk_offline()

def search_wikipedia(query):
    """Search Wikipedia and return summary"""
    try:
        speak("Let me look that up for you...")
        wikipedia.set_lang("en")
        results = wikipedia.search(query)
        if not results:
            return "I couldn't find anything on that topic."
        summary = wikipedia.summary(results[0], sentences=2)
        return f"According to Wikipedia: {summary}"
    except wikipedia.DisambiguationError:
        return "There are multiple results. Please be more specific."
    except wikipedia.PageError:
        return "Page not found."
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return "An error occurred while searching."

def handle_app_operation(command):
    """Trigger app_launcher to open/close apps"""
    try:
        action = "open" if "open" in command else "close"
        app_name = command.replace("open", "").replace("close", "").strip()

        if not app_name:
            return "Please specify an application name."

        result = app_launcher.handle_application(command)
        return result or f"Successfully {action}ed {app_name}"
    except Exception as e:
        print(f"App operation error: {e}")
        return f"Sorry, I couldn't {action} the application."

def open_or_close_application(command):
    """Launch application logic in a separate thread"""
    
    openingApp()

    def app_worker(q, cmd):
        q.put(handle_app_operation(cmd))

    operation_thread = threading.Thread(target=app_worker, args=(app_result_queue, command), daemon=True)
    operation_thread.start()

    result = app_result_queue.get()
    operation_thread.join()
   
def open_application(command):
    """Handles opening application in a separate thread"""
    openingApp()  # Only used for opening
    def app_worker(q, cmd):
        q.put(handle_app_operation(cmd))

    operation_thread = threading.Thread(target=app_worker, args=(app_result_queue, command), daemon=True)
    operation_thread.start()

    result = app_result_queue.get()
    operation_thread.join()
    speak(result)


def close_application(command):
    """Handles closing application in a separate thread"""
    def app_worker(q, cmd):
        q.put(handle_app_operation(cmd))

    operation_thread = threading.Thread(target=app_worker, args=(app_result_queue, command), daemon=True)
    operation_thread.start()

    result = app_result_queue.get()
    operation_thread.join()
    speak(result)


def fuzzy_match(command, phrases):
    """Match command using fuzzy logic"""
    for phrase in phrases:
        if fuzz.partial_ratio(command, phrase) > 80:  # Match threshold
            return True
    return False

def handle_greetings(command):
    """Handle common greeting variations using fuzzy matching."""
    greetings = ["how are you", "how r u", "how's it going", "how are you doing", "hey", "hi", "hello"]
    if fuzzy_match(command, greetings):
        speak("I'm doing great, thank you! How about you?")
        return True
    return False

def handle_jokes(command):
    """Handle jokes command."""
    if "joke" in command:
        speak("Why don't scientists trust atoms? Because they make up everything!")
        return True
    return False

def handle_thank_you(command):
    """Handle thank you response."""
    if "thank you" in command:
        speak("You're very welcome! Let me know if there's anything else.")
        return True
    return False

def run_app():
    """Main assistant loop"""
    initialize_greeting()
    time.sleep(1.0)
    speak("Hello! I'm ready to help. How can I assist you today?")

    while True:
        command = recognize_speech()
        if not command:
            continue

        command = command.lower().strip()
        print(f"Command received: {command}")

        if any(word in command for word in ["stop", "exit", "quit", "shutdown"]):
            speak("Goodbye! Have a great day.")
            break

        # Handle specific commands using functions
        if handle_greetings(command):
            continue

        if handle_jokes(command):
            continue

        if handle_thank_you(command):
            continue

        if "search wikipedia" in command:
            query = command.replace("search wikipedia", "").strip()
            speak(search_wikipedia(query) if query else "What should I search for?")

        elif any(cmd in command for cmd in ["who is", "what is"]):
            query = command.replace("who is", "").replace("what is", "").strip()
            speak(search_wikipedia(query) if query else "Please specify what you'd like to know.")

        elif "open" in command:
            open_application(command)

        elif "close" in command:
            close_application(command)

            

        else:
            speak("I'm not sure I understand. Could you try rephrasing that?")

if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        speak("Shutting down.")
    except Exception as e:
        print(f"Fatal error: {e}")
        speak("An error occurred. Restarting might help.")
