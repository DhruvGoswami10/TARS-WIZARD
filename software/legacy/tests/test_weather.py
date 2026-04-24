"""Tests for tars/commands/info.py — time and weather commands."""

from unittest.mock import MagicMock, patch

from tars.commands.info import get_current_time, get_weather


def test_get_current_time_contains_time():
    """get_current_time() returns a string with the current time."""
    result = get_current_time()
    assert isinstance(result, str)
    assert ":" in result  # contains time separator
    assert "M" in result  # AM or PM


@patch("tars.commands.info.config")
def test_get_weather_no_city(mock_config):
    """Returns helpful message when no city is configured."""
    mock_config.CITY_NAME = ""
    mock_config.WEATHER_API_KEY = "test"
    result = get_weather()
    assert "CITY_NAME" in result


@patch("tars.commands.info.config")
def test_get_weather_no_api_key(mock_config):
    """Returns helpful message when no API key is configured."""
    mock_config.CITY_NAME = "London"
    mock_config.WEATHER_API_KEY = ""
    result = get_weather()
    assert "WEATHER_API_KEY" in result


@patch("tars.commands.info.requests.get")
@patch("tars.commands.info.config")
def test_get_weather_success(mock_config, mock_get):
    """Parses successful weather API response."""
    mock_config.CITY_NAME = "London"
    mock_config.WEATHER_API_KEY = "testkey"
    mock_config.WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    mock_config.WEATHER_UNITS = "metric"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "weather": [{"description": "clear sky"}],
        "main": {"temp": 22},
    }
    mock_get.return_value = mock_response

    result = get_weather()
    assert "22" in result
    assert "clear sky" in result


@patch("tars.commands.info.requests.get")
@patch("tars.commands.info.config")
def test_get_weather_empty_weather_list(mock_config, mock_get):
    """Handles empty weather list in API response."""
    mock_config.CITY_NAME = "London"
    mock_config.WEATHER_API_KEY = "testkey"
    mock_config.WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    mock_config.WEATHER_UNITS = "metric"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"weather": [], "main": {"temp": 22}}
    mock_get.return_value = mock_response

    result = get_weather()
    assert "weird" in result


@patch("tars.commands.info.requests.get")
@patch("tars.commands.info.config")
def test_get_weather_api_error(mock_config, mock_get):
    """Handles non-200 API responses."""
    mock_config.CITY_NAME = "London"
    mock_config.WEATHER_API_KEY = "testkey"
    mock_config.WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    mock_config.WEATHER_UNITS = "metric"

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_weather()
    assert "yourself" in result.lower() or "dare" in result.lower()


@patch("tars.commands.info.requests.get")
@patch("tars.commands.info.config")
def test_get_weather_network_error(mock_config, mock_get):
    """Handles network errors gracefully."""
    import requests

    mock_config.CITY_NAME = "London"
    mock_config.WEATHER_API_KEY = "testkey"
    mock_config.WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    mock_config.WEATHER_UNITS = "metric"

    mock_get.side_effect = requests.RequestException("Connection failed")

    result = get_weather()
    assert "down" in result.lower() or "window" in result.lower()
