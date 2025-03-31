import os
import subprocess
import psutil

# Function to check if an application is already running
def is_app_running(app_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if app_name.lower() in proc.info['name'].lower():
            return True
    return False

# Function to start an application
def start_application(app_name):
    try:
        # For Windows applications, you can use subprocess to start the app
        if app_name == "notepad":
            subprocess.Popen(["notepad.exe"])
        elif app_name == "calculator":
            subprocess.Popen(["calc.exe"])
        else:
            print(f"Unsupported application: {app_name}")
            return
        print(f"{app_name} started.")
    except Exception as e:
        print(f"Error starting {app_name}: {e}")

# Function to close an application
def close_application(app_name):
    try:
        # Iterate through running processes and terminate the matching one
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.terminate()  # Close the application
                print(f"{app_name} closed.")
                return
        print(f"{app_name} is not running.")
    except Exception as e:
        print(f"Error closing {app_name}: {e}")

# Function to handle opening or closing an application based on the command
def handle_application(command):
    if "start" in  command or "open" in command:
        app_name = command.replace("start", "").replace("open","").strip()
        if app_name:
            start_application(app_name)
        else:
            print("Please specify the application to start.")
    elif "close" in command:
        app_name = command.replace("close", "").strip()
        if app_name:
            close_application(app_name)
        else:
            print("Please specify the application to close.")
    else:
        print("Invalid command. Say 'start <app_name>' or 'close <app_name>'.")
