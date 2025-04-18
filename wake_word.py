import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import threading
import json
import socket

class HybridWakeWordDetector:
    def __init__(self, wake_word="hey jarvis"):
        self.wake_word = wake_word.lower()
        self.listening = False
        self.wake_word_detected = False
        self.lock = threading.Lock()
        
        # Initialize both recognizers
        self.init_online_recognizer()
        self.init_offline_recognizer()
        
    def init_online_recognizer(self):
        """Initialize Google Speech Recognition (online)"""
        self.online_recognizer = sr.Recognizer()
        
    def init_offline_recognizer(self):
        """Initialize Vosk (offline)"""
        self.audio_interface = pyaudio.PyAudio()
        model_path = "./vosk-model-small-en-us-0.15"  # Update path
        self.offline_model = Model(model_path)
        self.offline_recognizer = KaldiRecognizer(self.offline_model, 16000)
        self.offline_stream = None
        
    def is_online(self):
        """Check internet connection"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False
            
    def online_callback(self, recognizer, audio):
        """Google Speech Recognition callback"""
        try:
            text = recognizer.recognize_google(audio).lower()
            print(f"(Online) Heard: {text}")
            if self.wake_word in text:
                with self.lock:
                    self.wake_word_detected = True
        except Exception as e:
            print(f"Online recognition error: {e}")

    def offline_listen_loop(self):
        """Vosk background listening thread"""
        self.offline_stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )
        
        while self.listening:
            data = self.offline_stream.read(4096, exception_on_overflow=False)
            if self.offline_recognizer.AcceptWaveform(data):
                result = json.loads(self.offline_recognizer.Result())
                text = result.get("text", "").lower()
                print(f"(Offline) Heard: {text}")
                if self.wake_word in text:
                    with self.lock:
                        self.wake_word_detected = True

    def start_detection(self):
        """Start detection with automatic mode selection"""
        if not self.listening:
            with self.lock:
                self.listening = True
                self.wake_word_detected = False
                
            if self.is_online():
                print("Using online recognition")
                with sr.Microphone() as source:
                    self.online_recognizer.adjust_for_ambient_noise(source)
                self.stop_listening = self.online_recognizer.listen_in_background(
                    sr.Microphone(), 
                    self.online_callback
                )
            else:
                print("Using offline recognition")
                self.offline_thread = threading.Thread(
                    target=self.offline_listen_loop,
                    daemon=True
                )
                self.offline_thread.start()

    def stop_detection(self):
        """Stop detection"""
        if self.listening:
            with self.lock:
                self.listening = False
                
            if hasattr(self, 'stop_listening'):
                self.stop_listening(wait_for_stop=False)
            if self.offline_stream:
                self.offline_stream.stop_stream()
                self.offline_stream.close()

    def check_wake_word(self):
        """Check if wake word was detected"""
        with self.lock:
            detected = self.wake_word_detected
            self.wake_word_detected = False  # Reset after checking
            return detected
