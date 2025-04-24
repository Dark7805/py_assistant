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