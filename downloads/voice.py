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
import mechanism  # Import the movement module

# Initialize OpenAI API key
openai.api_key = 'YOUR OPENAI API KEY'

# Initialize AWS Polly with your credentials
ACCESS_KEY = 'YOUR AWS POLLY ACCESS KEY'
SECRET_KEY = 'YOUR AWS POLLY SECRET KEY'
polly_client = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-east-1'
).client('polly')

# OpenWeatherMap API details
WEATHER_API_KEY = 'YOUR WEATHER API KEY'
CITY_NAME = 'Dubai'

def generate_tars_speech(text):
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
        VoiceId='Matthew'
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
        return f"It's {temp}°C and {main}. Good luck with that!"
    else:
        return "Check the weather yourself, I dare you."

def get_tars_response(user_input, honesty=0.5, humor=0.5):
    messages = [
        {"role": "system", "content": f"You are TARS, the sarcastic robot from Interstellar. "
                                      f"Respond to user queries with one-liners filled with sarcasm. "
                                      f"Your honesty level is at {honesty*100}% and humor level is at {humor*100}%."},
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

def speak(text):
    print(f"TARS: {text}")
    audio_stream = generate_tars_speech(text)
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

def process_command(command, humor, honesty):
    if command:
        print(f"Received command: {command}")
        if "stop" in command:
            speak("Oh great, now I can finally rest.")
            time.sleep(1)
            sys.exit()  
        elif "time" in command or "date" in command:
            response = get_current_time()
            speak(response)
        elif "weather" in command:
            response = get_weather(CITY_NAME)
            speak(response)
        elif "move forward" in command or "take 2 steps" in command:
            mechanism.move_forward()  # Call move_forward from mechanism.py
            speak("Moving forward.")
        elif "turn left" in command:
            mechanism.turn_left()  # Call turn_left from mechanism.py
            speak("Turning left.")
        elif "turn right" in command:
            mechanism.turn_right()  # Call turn_right from mechanism.py
            speak("Turning right.")
        else:
            response = get_tars_response(command, honesty=honesty, humor=humor)
            speak(response)

def main():
    humor = 0.5
    honesty = 0.5
    while True:
        command = listen()
        if command:
            process_command(command, humor, honesty)
            time.sleep(1)  

if __name__ == "__main__":
    main()
