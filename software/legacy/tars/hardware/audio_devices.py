"""Audio device detection for TARS — mic and speaker info."""


def list_microphones():
    """List available microphone names.

    Returns:
        List of microphone name strings.
    """
    try:
        import speech_recognition as sr
        return sr.Microphone.list_microphone_names()
    except Exception:
        return []


def get_default_microphone():
    """Get the default microphone name.

    Returns:
        Microphone name string or None.
    """
    try:
        import speech_recognition as sr
        mic = sr.Microphone()
        names = sr.Microphone.list_microphone_names()
        return names[mic.device_index] if mic.device_index < len(names) else None
    except Exception:
        return None


def list_speakers():
    """List available audio output devices.

    Returns:
        List of speaker name strings.
    """
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        speakers = []
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info.get("maxOutputChannels", 0) > 0:
                speakers.append(info["name"])
        pa.terminate()
        return speakers
    except Exception:
        return []
