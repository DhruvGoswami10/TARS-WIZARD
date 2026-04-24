from datetime import datetime

import requests

from tars import config


def get_current_time():
    """Get current time in TARS style."""
    now = datetime.now()
    return now.strftime("It's about time you asked! It's %I:%M %p.")


def get_weather(city_name=None):
    """Get weather for a city using OpenWeatherMap API."""
    city = city_name or config.CITY_NAME
    if not city:
        return "You haven't told me where you live. Set CITY_NAME in your .env file."
    if not config.WEATHER_API_KEY:
        return "No weather API key configured. Set WEATHER_API_KEY in your .env file."

    url = f"{config.WEATHER_API_URL}?q={city}&appid={config.WEATHER_API_KEY}&units={config.WEATHER_UNITS}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather_list = data.get("weather", [])
            if not weather_list:
                return "The weather data looks weird. Try again later."
            description = weather_list[0].get("description", "unknown")
            temp = data.get("main", {}).get("temp", "?")
            return f"It's {temp}C and {description}. Good luck with that!"
        else:
            return "Check the weather yourself, I dare you."
    except requests.RequestException as e:
        print(f"Weather API error: {e}")
        return "My weather service is down. Look out the window."
