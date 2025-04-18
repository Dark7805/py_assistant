# screenshot.py
import pyautogui
from datetime import datetime
import os

def take_screenshot():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"screenshot_{now}.png")
    
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    return file_path