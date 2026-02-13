# TARS Master Control — All-in-One Desktop Mode
# Launches Tkinter GUI console, voice assistant, and controller listener
# For headless Raspberry Pi deployment, see bundle/ directory instead

import speech_recognition as sr
import openai
import boto3
import requests
from pydub import AudioSegment, effects
import io
import re
from datetime import datetime
from pydub.playback import play
import threading
import sys
import time
import os
import tkinter as tk
from tkinter import scrolledtext, ttk
from tkinter.font import Font

# Try to import hardware-related modules, fallback if unavailable
try:
    import busio
    from board import SCL, SDA
    from adafruit_pca9685 import PCA9685
    HARDWARE_AVAILABLE = True
except ImportError:
    print("Hardware libraries (busio, board, adafruit_pca9685) not found. Running in software-only mode.")
    HARDWARE_AVAILABLE = False

# Try to import controller-related modules
try:
    from evdev import InputDevice, categorize, ecodes
    CONTROLLER_AVAILABLE = True
except ImportError:
    print("Controller library (evdev) not found. Controller support disabled.")
    CONTROLLER_AVAILABLE = False

# ─── API KEYS ────────────────────────────────────────────────
# See docs/api-keys.md for setup instructions
openai.api_key = 'YOUR OPENAI API KEY HERE'
OPENAI_AVAILABLE = openai.api_key != 'YOUR OPENAI API KEY HERE'
if not OPENAI_AVAILABLE:
    print("WARNING: OpenAI API key not set. AI responses will be limited.")

ACCESS_KEY = 'YOUR AWS ACCESS KEY HERE'
SECRET_KEY = 'YOUR AWS SECRET KEY HERE'
AWS_AVAILABLE = ACCESS_KEY != 'YOUR AWS ACCESS KEY HERE' and SECRET_KEY != 'YOUR AWS SECRET KEY HERE'
polly_client = None

if AWS_AVAILABLE:
    try:
        polly_client = boto3.Session(
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name='us-east-1'
        ).client('polly')
        print("AWS Polly initialized successfully")
    except Exception as e:
        print(f"Error initializing AWS Polly: {e}")
        AWS_AVAILABLE = False
else:
    print("WARNING: AWS credentials not set. Voice synthesis will use fallback method.")

WEATHER_API_KEY = 'WEATHER API KEY HERE'
CITY_NAME = 'YOUR CITY NAME HERE'

# ─── CONTROLLER ──────────────────────────────────────────────
controller = None
if CONTROLLER_AVAILABLE:
    try:
        devices = [InputDevice(path) for path in os.listdir('/dev/input') if path.startswith('event')]
        for device in devices:
            if 'controller' in device.name.lower() or 'gamepad' in device.name.lower() or 'joystick' in device.name.lower():
                controller = device
                print(f"Controller found: {device.name}")
                break
        if not controller:
            print("Controller not found. Voice commands will still work.")
    except Exception as e:
        print(f"Error initializing controller: {e}")
        print("Voice commands will still work.")
else:
    print("Controller support not available. Voice commands will still work.")

# ─── LANGUAGE CONFIG ─────────────────────────────────────────
LANGUAGE_VOICES = {
    'english': 'Matthew',
    'spanish': 'Miguel',
    'french': 'Mathieu',
    'german': 'Hans',
    'italian': 'Giorgio',
    'portuguese': 'Cristiano',
    'japanese': 'Takumi',
}

MOVEMENT_MESSAGES = {
    'english': {
        'forward': "Moving forward",
        'left': "Turning left",
        'right': "Turning right",
        'neutral': "Returning to neutral position"
    },
    'spanish': {
        'forward': "Moviendo hacia adelante",
        'left': "Girando a la izquierda",
        'right': "Girando a la derecha",
        'neutral': "Volviendo a posicion neutral"
    },
    'french': {
        'forward': "Avancer",
        'left': "Tourner a gauche",
        'right': "Tourner a droite",
        'neutral': "Retour a la position neutre"
    },
    'german': {
        'forward': "Vorwarts bewegen",
        'left': "Nach links drehen",
        'right': "Nach rechts drehen",
        'neutral': "Zuruck zur neutralen Position"
    },
    'italian': {
        'forward': "Movimento in avanti",
        'left': "Girando a sinistra",
        'right': "Girando a destra",
        'neutral': "Ritorno alla posizione neutra"
    },
    'portuguese': {
        'forward': "Movendo para frente",
        'left': "Virando a esquerda",
        'right': "Virando a direita",
        'neutral': "Retornando a posicao neutra"
    },
    'japanese': {
        'forward': "前進します",
        'left': "左に曲がります",
        'right': "右に曲がります",
        'neutral': "中立位置に戻ります"
    }
}

# ─── SERVO SETUP ─────────────────────────────────────────────
pca = None
servo_initialized = False
if HARDWARE_AVAILABLE:
    try:
        i2c = busio.I2C(SCL, SDA)
        pca = PCA9685(i2c)
        pca.frequency = 50
        servo_initialized = True
        print("Servo controller initialized successfully")
    except Exception as e:
        print(f"Error initializing servo controller: {e}")
        servo_initialized = False
else:
    print("Hardware support not available. Running in simulation mode.")

CHANNEL_TORSO = 0
CHANNEL_LEFT_ARM = 3
CHANNEL_RIGHT_ARM = 4

UP_HEIGHT = 130
NEUTRAL_HEIGHT = 0
DOWN_HEIGHT = -130
FORWARD_POS = 130
NEUTRAL_POS = 0
BACKWARD_POS = -130
LEFT_ARM_NEUTRAL_POS = -28
RIGHT_ARM_NEUTRAL_POS = 28

class LanguageState:
    def __init__(self):
        self.current_language = 'english'
        self.humor = 0.5
        self.honesty = 0.5

# ─── SERVO MOVEMENT ─────────────────────────────────────────
def angle_to_pulse(angle):
    min_pulse = 1000
    max_pulse = 2000
    pulse_width = min_pulse + (max_pulse - min_pulse) * ((angle + 180) / 360)
    return int(pulse_width * 65535 / 20000)

def set_servo_angle(channel, angle):
    if not servo_initialized:
        print(f"Would set servo on channel {channel} to {angle} (Servo controller not initialized)")
        return
    pulse_length = angle_to_pulse(angle)
    pca.channels[channel].duty_cycle = pulse_length
    print(f"Servo on channel {channel} set to {angle}")

def get_movement_message(movement_type, language='english'):
    messages = MOVEMENT_MESSAGES.get(language, MOVEMENT_MESSAGES['english'])
    return messages.get(movement_type, "Moving")

def move_forward(language='english'):
    print(get_movement_message('forward', language))
    set_servo_angle(CHANNEL_TORSO, BACKWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, -130)
    set_servo_angle(CHANNEL_RIGHT_ARM, 130)
    time.sleep(0.3)
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)

def turn_left(language='english'):
    print(get_movement_message('left', language))
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, 130)
    set_servo_angle(CHANNEL_RIGHT_ARM, 130)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

def turn_right(language='english'):
    print(get_movement_message('right', language))
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, -130)
    set_servo_angle(CHANNEL_RIGHT_ARM, -130)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

def neutral(language='english'):
    print(get_movement_message('neutral', language))
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

# ─── VOICE FUNCTIONS ────────────────────────────────────────
def generate_tars_speech(text, language='english'):
    voice_id = LANGUAGE_VOICES.get(language, 'Matthew')
    ssml_text = f"""
    <speak>
        <prosody rate="85%" pitch="-2%">
            {text}
        </prosody>
    </speak>
    """
    response = polly_client.synthesize_speech(
        Text=ssml_text,
        TextType='ssml',
        OutputFormat='mp3',
        VoiceId=voice_id
    )
    audio_stream = response['AudioStream'].read()
    return io.BytesIO(audio_stream)

def modify_voice(audio_stream):
    sound = AudioSegment.from_file(audio_stream, format="mp3")
    sound = effects.speedup(sound, playback_speed=1.35)
    sound = effects.low_pass_filter(sound, 2000)
    sound = sound - 2.5
    sound = sound + 6
    return sound

def play_audio(sound):
    play(sound)

def get_current_time():
    now = datetime.now()
    return now.strftime("It's about time you asked! It's %I:%M %p.")

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        main = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"It's {temp}C and {main}. Good luck with that!"
    else:
        return "Check the weather yourself, I dare you."

def get_tars_response(user_input, honesty=0.5, humor=0.5, target_language='english'):
    messages = [
        {"role": "system", "content": f"You are TARS, the sarcastic robot from Interstellar. "
                                      f"Respond to user queries with one-liners filled with sarcasm. "
                                      f"Your honesty level is at {honesty*100}% and humor level is at {humor*100}%. "
                                      f"Respond in {target_language}. Keep the sarcastic tone regardless of language."},
        {"role": "user", "content": user_input}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=50,
            temperature=0.9
        )
        content = response.choices[0].message['content'].strip()
        return content if content else "Oh, come on, say something meaningful!"
    except Exception as e:
        return f"Oops! I think I broke something: {e}"

def speak(text, language='english'):
    print(f"TARS: {text}")
    audio_stream = generate_tars_speech(text, language)
    modified_sound = modify_voice(audio_stream)
    play_audio(modified_sound)

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please speak clearly.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=3)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.WaitTimeoutError:
            print("Timeout waiting for a command. Speak up!")
            return None
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return None

def process_command(command, state):
    if command:
        print(f"Received command: {command}")
        if "speak" in command and any(lang in command for lang in LANGUAGE_VOICES.keys()):
            for lang in LANGUAGE_VOICES.keys():
                if lang in command:
                    state.current_language = lang
                    response = get_tars_response("Confirm language change",
                                              honesty=state.honesty,
                                              humor=state.humor,
                                              target_language=state.current_language)
                    speak(response, state.current_language)
                    return state
        elif "move forward" in command or "take 2 steps" in command:
            move_forward(state.current_language)
            response = get_tars_response("Moving forward",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        elif "turn left" in command:
            turn_left(state.current_language)
            response = get_tars_response("Turning left",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        elif "turn right" in command:
            turn_right(state.current_language)
            response = get_tars_response("Turning right",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        elif "stop" in command or "exit" in command:
            response = get_tars_response("Goodbye",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
            time.sleep(1)
            return "stop"
        elif "time" in command or "date" in command:
            response = get_current_time()
            speak(response, state.current_language)
        elif "weather" in command:
            response = get_weather(CITY_NAME)
            speak(response, state.current_language)
        else:
            response = get_tars_response(command,
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        return state

# ─── CONTROLLER INPUT ────────────────────────────────────────
def read_controller_input():
    if not CONTROLLER_AVAILABLE or not controller:
        return None
    try:
        event = controller.read_one()
        if event and event.type == ecodes.EV_KEY and event.value == 1:
            if event.code == ecodes.BTN_A:
                return "move_forward"
            elif event.code == ecodes.BTN_B:
                return "turn_right"
            elif event.code == ecodes.BTN_X:
                return "turn_left"
            elif event.code == ecodes.BTN_Y:
                return "neutral"
            elif event.code == ecodes.BTN_START:
                return "stop"
        return None
    except Exception as e:
        print(f"Error reading controller: {e}")
        return None

def process_controller_command(command, state):
    if command == "move_forward":
        move_forward(state.current_language)
        response = get_tars_response("Moving forward",
                                 honesty=state.honesty,
                                 humor=state.humor,
                                 target_language=state.current_language)
        speak(response, state.current_language)
    elif command == "turn_left":
        turn_left(state.current_language)
        response = get_tars_response("Turning left",
                                 honesty=state.honesty,
                                 humor=state.humor,
                                 target_language=state.current_language)
        speak(response, state.current_language)
    elif command == "turn_right":
        turn_right(state.current_language)
        response = get_tars_response("Turning right",
                                 honesty=state.honesty,
                                 humor=state.humor,
                                 target_language=state.current_language)
        speak(response, state.current_language)
    elif command == "neutral":
        neutral(state.current_language)
        response = get_tars_response("Neutral position",
                                 honesty=state.honesty,
                                 humor=state.humor,
                                 target_language=state.current_language)
        speak(response, state.current_language)
    elif command == "stop":
        response = get_tars_response("Goodbye",
                                 honesty=state.honesty,
                                 humor=state.humor,
                                 target_language=state.current_language)
        speak(response, state.current_language)
        time.sleep(1)
        return "stop"
    return state

def controller_thread_function(state):
    while True:
        command = read_controller_input()
        if command:
            new_state = process_controller_command(command, state)
            if new_state == "stop":
                sys.exit()
            else:
                state = new_state
        time.sleep(0.01)

# ─── TKINTER UI ──────────────────────────────────────────────
class TARSTerminalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TARS Terminal Interface")
        self.root.configure(bg='black')
        self.root.geometry("800x600")
        self.terminal_font = Font(family="Courier New", size=10)

        self.main_frame = tk.Frame(root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.terminal_output = scrolledtext.ScrolledText(
            self.main_frame,
            bg='black',
            fg='#00ff00',
            insertbackground='#00ff00',
            selectbackground='#005500',
            font=self.terminal_font,
            wrap=tk.WORD
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.terminal_output.config(state=tk.DISABLED)

        self.input_frame = tk.Frame(self.main_frame, bg='black')
        self.input_frame.pack(fill=tk.X, expand=False)

        self.prompt_label = tk.Label(
            self.input_frame, text="TARS> ",
            bg='black', fg='#00ff00', font=self.terminal_font
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            self.input_frame,
            bg='black', fg='#00ff00',
            insertbackground='#00ff00',
            font=self.terminal_font,
            relief=tk.FLAT,
            highlightbackground='#00ff00',
            highlightthickness=1
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.focus_set()
        self.input_entry.bind("<Return>", self.process_input)

        self.status_var = tk.StringVar()
        self.status_var.set("TARS ready")
        self.status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            bg='black', fg='#888888',
            font=("Courier New", 9), anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.state = LanguageState()
        self.command_history = []
        self.history_index = 0
        self.listening = False

        self.write_to_terminal("TARS Terminal Interface Initialized\n")
        self.write_to_terminal("Type a command or speak to interact\n")
        self.write_to_terminal("-" * 50 + "\n")
        self.root.after(1000, self.initialize_robot)

    def write_to_terminal(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)

    def initialize_robot(self):
        self.write_to_terminal("Initializing robot to neutral position...\n")
        neutral()
        self.write_to_terminal("Robot initialized. Ready for commands.\n")
        if CONTROLLER_AVAILABLE and controller:
            self.start_controller_thread()
            self.write_to_terminal(f"Controller found: {controller.name}\n")
        else:
            self.write_to_terminal("No controller found.\n")

    def start_controller_thread(self):
        self.controller_thread = threading.Thread(
            target=controller_thread_function,
            args=(self.state,)
        )
        self.controller_thread.daemon = True
        self.controller_thread.start()
        self.write_to_terminal("Controller thread started\n")

    def process_input(self, event=None):
        command = self.input_entry.get().strip()
        if not command:
            return
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        self.input_entry.delete(0, tk.END)
        self.write_to_terminal(f"You: {command}\n")
        threading.Thread(target=self.execute_command, args=(command,), daemon=True).start()

    def execute_command(self, command):
        self.root.after(0, lambda: self.status_var.set("Processing command..."))
        result = process_command(command, self.state)
        if result == "stop":
            self.root.after(1000, self.root.destroy)
            return
        self.state = result
        self.root.after(0, lambda: self.status_var.set("Ready"))

    def send_command(self, command):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, command)
        self.process_input()

# ─── MAIN ────────────────────────────────────────────────────
original_print = print
global ui_instance
ui_instance = None

def print_override(message):
    if ui_instance:
        ui_instance.write_to_terminal(message + "\n")
    original_print(message)

def speak_override(text, language='english'):
    if ui_instance:
        ui_instance.write_to_terminal(f"TARS: {text}\n")
    if AWS_AVAILABLE and polly_client:
        try:
            audio_stream = generate_tars_speech(text, language)
            modified_sound = modify_voice(audio_stream)
            play_audio(modified_sound)
        except Exception as e:
            original_print(f"Error during speech synthesis or playback: {e}")
            if ui_instance:
                ui_instance.write_to_terminal(f"Speech Error: {e}\n")
    else:
        original_print(f"TARS (voice synthesis unavailable): {text}")

def continuous_listening():
    global ui_instance
    while True:
        command = listen()
        if command:
            if ui_instance:
                ui_instance.write_to_terminal(f"You: {command}\n")
                ui_instance.execute_command(command)
        time.sleep(0.1)

def main():
    global ui_instance, print, speak
    original_speak = speak
    print = print_override
    speak = speak_override

    root = tk.Tk()
    ui = TARSTerminalUI(root)
    ui_instance = ui

    try:
        threading.Thread(target=continuous_listening, daemon=True).start()
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        print = original_print
        speak = original_speak

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)
