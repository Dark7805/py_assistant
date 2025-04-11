import os
import subprocess
import psutil
import pyttsx3  # For voice feedback
import threading  # To prevent concurrent speech issues
import time

# Initialize the Text-to-Speech engine
engine = pyttsx3.init()
speak_lock = threading.Lock()

# Dictionary mapping user-friendly names to actual application paths
APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calculator.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
    "explorer":"C:\\Windows\\explorer.exe"
}

# Dictionary mapping user-friendly names to actual process names for closing apps
APP_PROCESSES = {
    "notepad": "notepad.exe",
    "calculator": "calculator.exe",
    "chrome": "chrome.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "vlc": "vlc.exe",
    "explorer":"explorer.exe"
}

# Function to make the assistant speak (Thread-Safe)
def speak(text):
    with speak_lock:
        engine.say(text)
        engine.runAndWait()

# Function to start an application
def start_application(app_name):
    for key, path in APP_PATHS.items():
        if key in app_name.lower():
            try:
                subprocess.Popen(path, shell=True)
                speak(f"Opening {key}.")
                print(f"{key} started.")
                return
            except Exception as e:
                speak(f"Error starting {key}.")
                print(f"Error starting {key}: {e}")
                return
    speak(f"Application '{app_name}' not found.")
    print(f"Application '{app_name}' not found.")

# Function to close an application
def close_application(app_name):
    if app_name.lower() in APP_PROCESSES:
        process_name = APP_PROCESSES[app_name.lower()]
        try:
            result = subprocess.run(["taskkill", "/F", "/IM", process_name], shell=True, capture_output=True, text=True)
            if "SUCCESS" in result.stdout:
                speak(f"{app_name} has been closed.")
                print(f"✅ {app_name} closed successfully.")
            else:
                speak(f"Failed to close {app_name}.")
                print(f"⚠️ Failed to close {app_name}: {result.stderr}")
        except Exception as e:
            speak(f"Error closing {app_name}.")
            print(f"⚠️ Error closing {app_name}: {e}")
    else:
        speak(f"Application '{app_name}' not recognized.")
        print(f"❓ Application '{app_name}' not recognized.")

# Function to handle opening or closing an application based on the command
def handle_application(command):
    command = command.lower().strip()
    
    if "start" in command or "open" in command:
        app_name = command.replace("start", "").replace("open", "").strip()
        if app_name:
            start_application(app_name)
        else:
            speak("Please specify the application to start.")
            print("Please specify the application to start.")
    
    elif "close" in command or "stop" in command:
        app_name = command.replace("close", "").replace("stop", "").strip()
        if app_name:
            close_application(app_name)
        else:
            speak("Please specify the application to close.")
            print("Please specify the application to close.")
    
    else:
        speak("Invalid command. Say 'start app_name' or 'close app_name'.")
        print("Invalid command. Say 'start app_name' or 'close app_name'.")
