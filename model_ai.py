import speech_recognition as sr
import pyttsx3
import subprocess
import os
import sys
import json
from datetime import datetime
from auth_system import AuthenticationSystem

class VoiceControlAI:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        self.wake_word = 'melody'
        self.is_active = False
        
        # Initialize authentication system
        self.auth = AuthenticationSystem(default_user='Anbu')
        self.current_user = None
        
        self.command_map = {
            'open notepad': lambda: subprocess.Popen('notepad.exe'),
            'open calculator': lambda: subprocess.Popen('calc.exe'),
            'open file explorer': lambda: subprocess.Popen('explorer.exe'),
            'open command prompt': lambda: subprocess.Popen('cmd.exe'),
            'open chrome': lambda: subprocess.Popen('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'),
            'close application': lambda: os.system('taskkill /F /IM notepad.exe'),
            # 'shutdown': lambda: os.system('shutdown /s /t 30'),
            'restart': lambda: os.system('shutdown /r /t 30'),
            'lock screen': lambda: os.system('rundll32.exe user32.dll,LockWorkStation'),
            'mute': lambda: self._mute_volume(),
            'unmute': lambda: self._unmute_volume(),
        }
    
    def get_greeting(self):
        """Get greeting based on current time"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "Good morning! How can I help you?"
        elif 12 <= current_hour < 17:
            return "Good afternoon! What do you need?"
        elif 17 <= current_hour < 21:
            return "Good evening! What can I do for you?"
        else:
            return "Good night! How can I help?"
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"[AI]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Capture voice input and convert to text"""
        try:
            with sr.Microphone() as source:
                print("[Listening...] Speak now...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=10)
            
            text = self.recognizer.recognize_google(audio)
            print(f"[You]: {text}")
            return text.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError as e:
            self.speak(f"Error: {e}")
            return None
        except Exception as e:
            self.speak(f"Listening error: {e}")
            return None
    
    def _mute_volume(self):
        os.system('volume mute')
        self.speak("Muting volume")
    
    def _unmute_volume(self):
        os.system('volume unmute')
        self.speak("Unmuting volume")
    
    def execute_command(self, command):
        """Execute system command based on voice input"""
        command_lower = command.lower()
        
        # Direct command match
        for key, action in self.command_map.items():
            if key in command_lower:
                try:
                    action()
                    self.speak(f"Executing: {key}")
                    return True
                except Exception as e:
                    self.speak(f"Error executing command: {e}")
                    return False
        
        # Handle open file/folder commands
        if 'open' in command_lower:
            path = command_lower.replace('open', '').strip()
            try:
                os.startfile(path)
                self.speak(f"Opening {path}")
                return True
            except Exception as e:
                self.speak(f"Could not open {path}")
                return False
        
        # Handle web search
        if 'search' in command_lower:
            query = command_lower.replace('search', '').strip()
            try:
                search_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
                os.startfile(search_url)
                self.speak(f"Searching for {query}")
                return True
            except Exception as e:
                self.speak(f"Could not search: {e}")
                return False
        
        self.speak("Command not recognized. Please try again.")
        return False
    
    def process_command(self, text):
        """Process the recognized voice command"""
        if not text:
            return False
        
        # Handle stop/exit commands
        if any(word in text for word in ['stop', 'exit', 'quit','sleep', 'goodbye']):
            self.speak("Goodbye! Turning off voice control.")
            return False
        
        # Handle information requests
        if 'time' in text:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            return True
        
        if 'date' in text:
            current_date = datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            return True
        
        # Execute system commands
        self.execute_command(text)
        return True
    
    def save_log(self, text, result):
        """Save voice command logs"""
        log_file = 'voice_commands.log'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] User: {self.current_user} | Command: {text} | Success: {result}\n")
    
    def authenticate_user(self, name: str = 'Anbu', voice_param: str = None, passcode: str = None):
        """Authenticate user based on access level"""
        if name.lower() == 'anbu':
            success, msg = self.auth.authenticate_default_user(voice_param)
        else:
            success, msg = self.auth.authenticate_custom_user(name, voice_param, passcode)
        
        if success:
            self.current_user = name
            self.speak(msg)
        else:
            self.speak(f"Authentication failed: {msg}")
        
        return success
    
    def require_authentication(self):
        """Enforce authentication before executing sensitive commands"""
        if not self.current_user or not self.auth.is_authenticated:
            self.speak("Please authenticate first. Say your name.")
            return False
        return True
    
    def listen_for_wakeword(self):
        """Continuously listen for wake word"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5)
            
            text = self.recognizer.recognize_google(audio).lower()
            print(f"[Heard]: {text}")
            
            if self.wake_word in text:
                self.is_active = True
                greeting = self.get_greeting()
                self.speak(greeting)
                self.command_loop()
            
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass
        except Exception:
            pass
    
    def command_loop(self):
        """Main command listening loop after wake word detected"""
        while self.is_active:
            try:
                with sr.Microphone() as source:
                    print("[Listening for command...]")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=10)
                
                command = self.recognizer.recognize_google(audio).lower()
                print(f"[Command]: {command}")
                self.speak(f"You said: {command}")
                
                result = self.process_command(command)
                self.save_log(command, result)
                
                if not result:
                    self.is_active = False
                    break
                
            except sr.UnknownValueError:
                self.speak("Sorry, I did not understand. Please repeat.")
            except sr.RequestError as e:
                self.speak(f"Error with audio service: {e}")
            except KeyboardInterrupt:
                self.is_active = False
                self.speak("System shut down.")
                break
            except Exception as e:
                self.speak(f"Unexpected error: {e}")
                self.is_active = False
                break
    
    def start(self):
        """Start the voice control system"""
        try:
            # Authenticate default user first
            self.speak(f"Welcome to your personal assistant. Authenticating as {self.auth.default_user}...")
            self.authenticate_user()
            
            while True:
                self.listen_for_wakeword()
        except KeyboardInterrupt:
            self.speak("Voice control system turned off.")
            self.auth.logout()
            sys.exit(0)


def main():
    """Main entry point"""
    try:
        ai = VoiceControlAI()
        ai.start()
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
