import speech_recognition as sr

from tars import config


def listen():
    """Listen for a voice command via microphone. Returns lowercase string or None."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening... Please speak clearly.")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=config.LISTEN_TIMEOUT)
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
    except OSError as e:
        print(f"Microphone error: {e}")
        return None
