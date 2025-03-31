import spacy
import wikipediaapi
from commands.time_date import get_time, get_date
from commands.browser import open_website
from commands.system import play_music, exit_program
from text_to_speech import speak

# Load NLP Model
nlp_model = spacy.load("en_core_web_sm")

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia('python-requests/2.32.3')

def get_wikipedia_summary(query):
    """Fetches summary from Wikipedia for a given query."""
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary[:500]  # Return first 500 characters of the summary
    return "Sorry, I couldn't find relevant information."

def process_command(command):
    """Processes user commands."""
    
    # Handle Time and Date
    if "time" in command:
        time_info = get_time()  # Ensure get_time() returns a string for TTS
        speak(f"The current time is {time_info}")
    elif "date" in command:
        date_info = get_date()  # Ensure get_date() returns a string for TTS
        speak(f"Today's date is {date_info}")
    
    # Handle opening websites
    elif "open youtube" in command:
        open_website("youtube")
    elif "open google" in command:
        open_website("google")
    
    # Handle music
    elif "play music" in command:
        play_music()
    
    # Handle exiting the program
    elif "exit" in command or "stop" in command:
        exit_program()
    
    # Wikipedia search for general knowledge
    elif "who is" in command or "what is" in command:
        query = command.replace("who is", "").replace("what is", "").strip()
        if query:
            response = get_wikipedia_summary(query)
            speak(response)
        else:
            speak("Please provide a valid name or topic.")
    
    # Unrecognized commands
    else:
        speak("I'm not sure how to help with that. Can you please clarify?")
