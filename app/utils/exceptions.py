"""
Custom exceptions for the application.
"""


class WeatherAPIError(Exception):
    """Base exception for weather API errors."""
    pass


class CityNotFoundError(WeatherAPIError):
    """Raised when a city is not found."""
    pass


class WeatherDataNotFoundError(WeatherAPIError):
    """Raised when weather data is not found."""
    pass


class ExternalAPIError(WeatherAPIError):
    """Raised when external API (OpenWeather) fails."""
    pass


class ValidationError(WeatherAPIError):
    """Raised when input validation fails."""
    pass

