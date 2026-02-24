# TARS Voice Assistant — Speech recognition + AI conversation + TTS
# Runs headless on Raspberry Pi, controls servos via mechanism module

import speech_recognition as sr
import openai
import boto3
import requests
from pydub import AudioSegment, effects
import io
from datetime import datetime
from pydub.playback import play
import sys
import time
import mechanism

# ─── API KEYS ────────────────────────────────────────────────
# See docs/api-keys.md for setup instructions
openai.api_key = 'YOUR OPENAI API KEY HERE'

ACCESS_KEY = 'YOUR AWS ACCESS KEY HERE'
SECRET_KEY = 'YOUR AWS SECRET KEY HERE'
polly_client = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-east-1'
).client('polly')

WEATHER_API_KEY = 'WEATHER API KEY HERE'
CITY_NAME = 'YOUR CITY NAME HERE'

LANGUAGE_VOICES = {
    'english': 'Matthew',
    'spanish': 'Miguel',
    'french': 'Mathieu',
    'german': 'Hans',
    'italian': 'Giorgio',
    'portuguese': 'Cristiano',
    'japanese': 'Takumi',
}

class LanguageState:
    def __init__(self):
        self.current_language = 'english'
        self.humor = 0.5
        self.honesty = 0.5

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
            mechanism.move_forward()
            response = get_tars_response("Moving forward",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        elif "turn left" in command:
            mechanism.turn_left()
            response = get_tars_response("Turning left",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        elif "turn right" in command:
            mechanism.turn_right()
            response = get_tars_response("Turning right",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
        elif "stop" in command:
            response = get_tars_response("Goodbye",
                                     honesty=state.honesty,
                                     humor=state.humor,
                                     target_language=state.current_language)
            speak(response, state.current_language)
            time.sleep(1)
            sys.exit()
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

def main():
    state = LanguageState()
    while True:
        command = listen()
        if command:
            state = process_command(command, state)
            time.sleep(1)

if __name__ == "__main__":
    main()
