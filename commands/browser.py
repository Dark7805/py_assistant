import webbrowser
from text_to_speech import speak

def open_website(site):
    urls = {"youtube": "https://www.youtube.com", "google": "https://www.google.com"}
    if site in urls:
        webbrowser.open(urls[site])
        speak(f"Opening {site}")
    else:
        speak("Website not recognized.")
