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
        return page.summary[:500]  # Return first 500 characters
    return "Sorry, I couldn't find relevant information."

def process_command(command):
    """Processes user commands."""
    
    if "time" in command:
        get_time()
    elif "date" in command:
        get_date()
    elif "open youtube" in command:
        open_website("youtube")
    elif "open google" in command:
        open_website("google")
    elif "play music" in command:
        play_music()
    elif "exit" in command or "stop" in command:
        exit_program()
    
    # Wikipedia search for general knowledge
    elif "who is" in command or "what is" in command:
        query = command.replace("who is", "").replace("what is", "").strip()
        response = get_wikipedia_summary(query)
        speak(response)
    
    else:
        speak("I'm not sure how to help with that.")

