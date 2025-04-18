import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import socket
import wikipedia
import app_launcher
import threading
import queue
import time
from greeting import initialize_greeting, openingApp
from fuzzywuzzy import fuzz
from play_music import play_on_youtube, play_first_youtube_video
import customtkinter as ctk
from PIL import Image
import os
import sys
from text_to_speech import speak
import platform
import random
from wake_word import HybridWakeWordDetector
from task_manager import TaskManager
from filenavigator import open_folder, search_files, open_file_picker
import subprocess
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from datetime import datetime
import pyautogui
from screenshot import take_screenshot



# Set modern theme
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Queues for async handling
app_result_queue = queue.Queue()
command_queue = queue.Queue()

# Enhanced conversation responses with more variety
CONVERSATION_RESPONSES = {
    "greetings": [
        "Hey there! How can I help you today?",
        "Hello! Nice to hear from you.",
        "Hi! What can I do for you?",
        "Greetings! I'm here to assist.",
        "Hi there! Ready when you are."
    ],
    "how_are_you": [
        "I'm just a program, but running smoothly! How about you?",
        "Doing great, thanks for asking! And yourself?",
        "I'm functioning perfectly! How are you today?",
        "No complaints in my code! How are things with you?"
    ],
    "compliments": [
        "You're too kind! I'm just doing my job.",
        "Thanks! My developers will be happy to hear that.",
        "I appreciate that! I aim to please.",
        "You're making my algorithms happy!"
    ],
    "jokes": [
        "Why don't programmers like nature? It has too many bugs!",
        "How do you comfort a JavaScript bug? You console it!",
        "Why did the developer go broke? Because he used up all his cache!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the computer keep freezing? It left its Windows open!"
    ],
    "farewell": [
        "Goodbye! Don't hesitate to call if you need me.",
        "See you later! I'm always here to help.",
        "Bye for now! It was nice talking with you.",
        "Take care! Come back anytime."
    ],
    "positive_feelings": [
        "That's wonderful to hear!",
        "I'm glad you're doing well!",
        "Fantastic! What can I help you with?",
        "Great! How can I assist you today?"
    ],
    "negative_feelings": [
        "I'm sorry to hear that. Maybe I can help?",
        "That doesn't sound good. Can I assist with something?",
        "I hope things get better. What can I do for you?",
        "Let me know if I can help improve your day."
    ]
}

# Context-aware conversation handler
class ConversationHandler:
    def __init__(self):
        self.context = {
            "last_question": None,
            "user_name": None,
            "last_topic": None
        }
    
    def handle(self, command):
        """Main conversation handling with context awareness"""
        command = command.lower()
        response = None
        
        # Check for name introduction
        if "my name is" in command:
            name = command.split("my name is")[-1].strip()
            self.context["user_name"] = name
            return f"Nice to meet you, {name}! How can I help you today?"
        
        # Personalized responses if we know the name
        if self.context.get("user_name"):
            if any(word in command for word in ["hi", "hello", "hey"]):
                return f"Hello {self.context['user_name']}! What can I do for you?"
        
        # Handle follow-up to "how are you"
        if self.context.get("last_question") == "asked_about_day":
            if any(word in command for word in ["good", "great", "fine", "well", "awesome"]):
                self.context["last_question"] = None
                return random.choice(CONVERSATION_RESPONSES["positive_feelings"])
            elif any(word in command for word in ["bad", "not good", "terrible", "awful"]):
                self.context["last_question"] = None
                return random.choice(CONVERSATION_RESPONSES["negative_feelings"])
        
        # Greetings detection
        if any(word in command for word in ["hi", "hello", "hey"]):
            return random.choice(CONVERSATION_RESPONSES["greetings"])
        
        # How are you detection
        if any(phrase in command for phrase in ["how are you", "how's it going", "how do you do"]):
            self.context["last_question"] = "asked_about_day"
            return random.choice(CONVERSATION_RESPONSES["how_are_you"])
        
        # Compliment detection
        if any(word in command for word in ["good", "great", "awesome", "smart", "cool", "amazing"]):
            return random.choice(CONVERSATION_RESPONSES["compliments"])
        
        # Joke detection
        if any(word in command for word in ["joke", "funny", "laugh", "make me smile"]):
            return random.choice(CONVERSATION_RESPONSES["jokes"])
        
        # Farewell detection
        if any(word in command for word in ["bye", "goodbye", "see you", "later"]):
            return random.choice(CONVERSATION_RESPONSES["farewell"])
        
        return None

# Initialize conversation handler
conversation_handler = ConversationHandler()

def handle_conversation(command):
    """Wrapper for conversation handler"""
    return conversation_handler.handle(command)

def handle_thank_you(command):
    """Handle thank you with variations"""
    if "thank you" in command or "thanks" in command:
        responses = [
            "You're very welcome!",
            "Happy to help!",
            "My pleasure!",
            "Anytime!",
            "Glad I could assist!"
        ]
        speak(random.choice(responses))
        return True
    return False

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Set volume to a specific level: 0.0 (min) to 1.0 (max)
def set_volume(level):  
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level, None)

# Handle common volume commands
def change_volume(command):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    current_volume = volume.GetMasterVolumeLevelScalar()

    if "volume up" in command:
        new_volume = min(current_volume + 0.1, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume increased.")
    
    elif "volume down" in command:
        new_volume = max(current_volume - 0.1, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume decreased.")
    
    elif "mute" in command:
        volume.SetMute(1, None)
        speak("Volume muted.")
    
    elif "unmute" in command:
        volume.SetMute(0, None)
        speak("Volume unmuted.")

class VoskWakeWordDetector:
    def __init__(self, wake_word):
        self.wake_word = wake_word
        self.wake_word_detected = False
        self.model = Model(r"D:\\Code\\Python_Project\\vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.mic = pyaudio.PyAudio()

    def start_detection(self):
        self.stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                                    input=True, frames_per_buffer=8192)
        self.stream.start_stream()

    def check_wake_word(self):
        data = self.stream.read(4096, exception_on_overflow=False)
        if self.recognizer.AcceptWaveform(data):
            text = json.loads(self.recognizer.Result()).get("text", "").lower()
            if self.wake_word in text:
                self.wake_word_detected = True
                return True
        return False

    def stop_detection(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()

class VoiceAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.task_manager = TaskManager()
        self.title("Jarvis Voice Assistant")
        self.geometry("600x500")
        self.resizable(False, False)

        self.recognizer = sr.Recognizer()
        self.active_listening = False
        self.waiting_for_wake_word = True
        self.command_timeout_seconds = 10
        self.last_command_time = None

        self.create_widgets()

        # Wake word detector for both online and offline
        self.wake_detector_online = HybridWakeWordDetector(wake_word="hey jarvis")
        self.wake_detector_offline = VoskWakeWordDetector(wake_word="hey jarvis")

        # Start threads for both wake word detectors
        self.wake_thread_online = threading.Thread(target=self.listen_for_online_wake_word, daemon=True)
        self.wake_thread_offline = threading.Thread(target=self.listen_for_offline_wake_word, daemon=True)
        self.wake_thread_online.start()
        self.wake_thread_offline.start()

        # Queue processor
        self.after(100, self.process_queue)

    def create_widgets(self):
        self.title_label = ctk.CTkLabel(self, text="Jarvis Voice Assistant", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)

        self.output_text = ctk.CTkTextbox(self, height=350, width=550, font=("Courier", 14))
        self.output_text.pack(pady=10)
        self.output_text.insert("end", "Waiting for wake word: 'Hey Jarvis'...\n")

        self.mic_button = ctk.CTkButton(self, text="Start Listening", command=self.manual_start_listening, fg_color="#4ecdc4")
        self.mic_button.pack(pady=10)

    def log_message(self, message, tag=None):
        self.output_text.insert("end", f"{message}\n")
        self.output_text.see("end")

    def process_queue(self):
        try:
            if not command_queue.empty():
                command = command_queue.get()
                self.process_command(command)
        except Exception as e:
            self.log_message(f"Queue Error: {str(e)}", "error")
        self.after(100, self.process_queue)

    def manual_start_listening(self):
        if not self.active_listening:
            self.begin_active_listening()

    def listen_for_online_wake_word(self):
        while True:
            if self.waiting_for_wake_word:
                self.wake_detector_online.start_detection()
                while self.waiting_for_wake_word:
                    if self.wake_detector_online.check_wake_word():
                        self.wake_detector_online.wake_word_detected = False
                        self.begin_active_listening()
                    time.sleep(0.1)
                self.wake_detector_online.stop_detection()
            time.sleep(0.1)

    def listen_for_offline_wake_word(self):
        while True:
            if self.waiting_for_wake_word:
                self.wake_detector_offline.start_detection()
                while self.waiting_for_wake_word:
                    if self.wake_detector_offline.check_wake_word():
                        self.wake_detector_offline.wake_word_detected = False
                        self.begin_active_listening()
                    time.sleep(0.1)
                self.wake_detector_offline.stop_detection()
            time.sleep(0.1)

    def begin_active_listening(self):
        self.active_listening = True
        self.waiting_for_wake_word = False
        self.last_command_time = time.time()

        self.mic_button.configure(text="Listening...", fg_color="#ffa500")
        self.log_message("Listening for commands...", "system")
        speak("Yes? How can I help?")

        threading.Thread(target=self.listen_for_commands_loop, daemon=True).start()

    def listen_for_commands_loop(self):
        while self.active_listening:
            if time.time() - self.last_command_time > self.command_timeout_seconds:
                self.log_message("No command received. Going to sleep.", "system")
                self.stop_listening()
                return

            try:
                command = ""
                if is_connected():  # Use Google if online
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source)
                        audio = self.recognizer.listen(source, timeout=3)
                        command = self.recognizer.recognize_google(audio).lower()
                else:  # Offline fallback: Use Vosk
                    command = recognize_vosk_offline()

                if command:
                    self.last_command_time = time.time()
                    self.log_message(f"You: {command}", "command")
                    command_queue.put(command)

            except (sr.UnknownValueError, sr.WaitTimeoutError):
                continue
            except Exception as e:
                self.log_message(f"Error: {str(e)}", "error")
                time.sleep(1)

    def stop_listening(self):
        self.active_listening = False
        self.waiting_for_wake_word = True
        self.mic_button.configure(text="Start Listening", fg_color="#4ecdc4")
        self.log_message("Waiting for wake word...", "system")

 
        



    
    
    def process_command(self, command):
        """Process a single command with enhanced conversation"""
        try:
            command = command.lower().strip()
            
            # First try conversation handler
            conversation_response = handle_conversation(command)
            if conversation_response:
                self.log_message(f"Assistant: {conversation_response}", "info")
                speak(conversation_response)
                return
                
            # Then handle thank you separately
            if handle_thank_you(command):
                return
                
            # Functional commands
            if any(word in command for word in ["stop", "exit", "quit", "shutdown"]):
                self.log_message("Shutting down assistant...", "system")
                self.stop_listening()
                speak(random.choice(CONVERSATION_RESPONSES["farewell"]))
                return
                
            if  "who is" in command or "what is" in command:
                query = command.replace("search wikipedia", "").strip()
                if query:
                    result = search_wikipedia(query)
                    self.log_message(f"Wikipedia: {result}", "info")
                    speak(result)
                else:
                    speak("What should I search for?")
                return
                
            if any(cmd in command for cmd in ["who is", "what is"]):
                query = command.replace("who is", "").replace("what is", "").strip()
                if query:
                    result = search_wikipedia(query)
                    self.log_message(f"Wikipedia: {result}", "info")
                    speak(result)
                else:
                    speak("Please specify what you'd like to know.")
                return
            if "open my downloads" in command:
                return open_folder("downloads")

            if "open my documents" in command:
                return open_folder("documents")

            if "open my desktop" in command:
                return open_folder("desktop")

            if "search for files named" in command:
                keyword = command.split("named")[-1].strip()
                return search_files(keyword)

            elif "open file picker" in command or "browse file" in command:
                return open_file_picker()    
            if "open" in command:
                self.log_message(f"Opening application: {command}", "info")
                open_application(command)
                return
                
            if "close" in command:
                self.log_message
                (f"Closing application: {command}", "info")
                close_application(command)
                return
            elif "volume" in command:
                change_volume(command)
                return None  # Prevents repeating response

            if "screenshot" in command or "take a screenshot" in command:
                path = take_screenshot()
                speak(f"Screenshot taken and saved")
                return
            if "play" in command:
                song = command.replace("play", "").strip()
                if song:
                    self.log_message(f"Playing: {song}", "info")
                    speak(f"Playing {song} on YouTube.")
                    play_first_youtube_video(song)
                else:
                    speak("Please tell me the song name to play.")
                return
            elif "youtube" in command:
                query = command.replace("youtube", "").strip()
                if query:
                    self.log_message(f"Searching YouTube for: {query}", "info")
                    speak(f"Searching YouTube for {query}")
                    play_on_youtube(query)
                else:
                    speak("What would you like to search on YouTube?")
                return
            # If nothing matched
            if "add task" in command:
                task = command.replace("add task", "").strip()
                self.task_manager.add_task(task)
                speak(f"Task added: {task}")

            elif "list tasks" in command or "what are my tasks" in command:
                tasks = self.task_manager.list_tasks()
                if not tasks:
                    speak("You have no tasks.")
                else:
                    for i, task in enumerate(tasks, 1):
                        status = "done" if task["done"] else "pending"
                        speak(f"{i}. {task['description']} - {status}")

            elif "remove task" in command or "delete task" in command:
                task = command.replace("remove task", "").replace("delete task", "").strip()
                self.task_manager.delete_task(task)
                speak(f"Task removed: {task}")
                return
            if "mark" in command and "done" in command:
                task = command.replace("mark", "").replace("as done", "").strip()
                self.task_manager.mark_done(task)
                speak(f"Marked {task} as done.")
                return
            elif "time" in command:
                current_time = datetime.now().strftime("%I:%M %p")
                speak(f"The current time is {current_time}.")
                return
            elif "date" in command:
                    current_date = datetime.now().strftime("%A, %B %d, %Y")
                    speak(f"Today is {current_date}.")
                    return
            if "turn off wifi" in command:
                subprocess.run("netsh interface set interface name=\"Wi-Fi\" admin=disable", shell=True)
                speak("Wi-Fi turned off.")
            elif "turn on wifi" in command:
                subprocess.run("netsh interface set interface name=\"Wi-Fi\" admin=enable", shell=True)
                speak("Wi-Fi turned on.")
            fallback_responses = [
                "I'm not sure I caught that. Could you rephrase?",
                "I didn't quite understand. Try asking differently?",
                "I might need more context to help with that."
            ]
            response = random.choice(fallback_responses)
            self.log_message(f"Assistant: {response}", "info")
            speak(response)
            
        except Exception as e:
            self.log_message(f"Error processing command: {str(e)}", "error")
    
        
    def open_settings(self):
        """Open settings dialog"""
        self.log_message("Opening settings...", "system")
        # Implement your settings dialog here
        pass
    
    def show_ar_visuals(self, command):
        if not self.ar_visualizer:
            self.ar_visualizer = ARVisualizer()
    
        if "weather" in command:
        # Extract weather condition from API
            if self.weather_api:
                condition = self.weather_api.get_current_condition()
                if condition:
                    self.ar_visualizer.display_weather_animation(condition)
                    self.log_message(f"Displaying {condition} weather in AR.", "info")
                else:
                    self.log_message("No weather condition available.", "error")
            else:
                self.log_message("Weather API not initialized.", "error")

        elif "navigate" in command or "direction" in command:
        # Get navigation data
            if self.navigation:
                direction = self.navigation.get_next_step()
                if direction:
                    self.ar_visualizer.show_3d_arrows(direction)
                    self.log_message(f"Displaying navigation arrow: {direction}.", "info")
                else:
                    self.log_message("No direction received from navigation system.", "error")
        else:
            self.log_message("Navigation system not initialized.", "error")

    def quit_app(self):
        """Clean up and quit application"""
        self.stop_listening()
        self.running = False
        self.log_message("Shutting down application...", "system")
        self.after(500, self.destroy)

# Speech recognition functions
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def recognize_google_online():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            return recognizer.recognize_google(audio).lower()
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return ""

def recognize_vosk_offline():
    model = Model(r"D:\\Code\\Python_Project\\vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                     input=True, frames_per_buffer=8192)
    stream.start_stream()

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            text = json.loads(recognizer.Result()).get("text", "").lower()
            stream.stop_stream()
            stream.close()
            mic.terminate()
            return text

def fuzzy_match(command, phrases):
    for phrase in phrases:
        if fuzz.partial_ratio(command, phrase) > 80:
            return True
    return False

# Application functions
def search_wikipedia(query):
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

def open_application(command):
    openingApp()
    def app_worker(q, cmd):
        q.put(handle_app_operation(cmd))

    operation_thread = threading.Thread(target=app_worker, args=(app_result_queue, command), daemon=True)
    operation_thread.start()

    result = app_result_queue.get()
    operation_thread.join()
    speak(result)

def close_application(command):
    def app_worker(q, cmd):
        q.put(handle_app_operation(cmd))

    operation_thread = threading.Thread(target=app_worker, args=(app_result_queue, command), daemon=True)
    operation_thread.start()

    result = app_result_queue.get()
    operation_thread.join()
    speak(result)


if __name__ == "__main__":
    # Initialize assistant
    initialize_greeting()
    
    # Create and run application
    app = VoiceAssistantApp()
    app.log_message("Neon Voice Assistant initialized", "system")
    app.log_message("Type 'exit' or say 'stop' to quit", "info")
    app.log_message("Say 'hello' to start interacting", "info")
    
    # Start the main loop
    app.mainloop()