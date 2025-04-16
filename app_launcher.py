import os
import subprocess
import psutil
from text_to_speech import speak

# Mapping of app names to executable paths
APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "word": "C:\\Program Files\\Microsoft Office\\Office15\\WINWORD.EXE",
    "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
    "explorer": "C:\\Windows\\explorer.exe"
}

# Mapping of app names to process names
APP_PROCESSES = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "vlc": "vlc.exe",
    "explorer": "explorer.exe"
}


def start_application(app_name):
    """Launch an application and provide feedback."""
    for key, path in APP_PATHS.items():
        if key in app_name.lower():
            try:
                subprocess.Popen(path, shell=True)
                message = f"Opened {key}."
                
                return message
            except Exception as e:
                error_msg = f"Error starting {key}: {str(e)}"
                speak(error_msg)
                return error_msg
    not_found = f"Application '{app_name}' not found."
    speak(not_found)
    return not_found


def close_application(app_name):
    """Kill the application process and provide feedback."""
    app_key = app_name.lower()
    if app_key in APP_PROCESSES:
        process_name = APP_PROCESSES[app_key]
        try:
            found = False
            for proc in psutil.process_iter():
                if proc.name().lower() == process_name.lower():
                    proc.kill()
                    found = True
            if found:
                msg = f"Closed {app_key}."
            else:
                msg = f"{app_key} is not currently running."
            
            return msg
        except Exception as e:
            error_msg = f"Error closing {app_key}: {str(e)}"
            speak(error_msg)
            return error_msg
    else:
        msg = f"Application '{app_name}' not recognized."
        speak(msg)
        return msg


def handle_application(command):
    """Parse and handle app-related commands."""
    command = command.lower().strip()

    if "open" in command or "start" in command:
        app_name = command.replace("open", "").replace("start", "").strip()
        if app_name:
            return start_application(app_name)
        else:
            response = "Please specify the application to open."
            speak(response)
            return response

    elif "close" in command or "stop" in command:
        app_name = command.replace("close", "").replace("stop", "").strip()
        if app_name:
            return close_application(app_name)
        else:
            response = "Please specify the application to close."
            speak(response)
            return response

    invalid = "Invalid command. Say 'start app_name' or 'close app_name'."
    speak(invalid)
    return invalid
