import requests
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import City, WeatherRecord
from app.config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL
from app.utils.exceptions import ExternalAPIError, ValidationError


def fetch_weather_from_api(city_name: str) -> dict:
    """
    Calls OpenWeather API to get current weather for a city.
    
    Raises:
        ExternalAPIError: If API call fails
        ValidationError: If city not found by API
    """
    if not OPENWEATHER_API_KEY:
        raise ExternalAPIError("OpenWeather API key is not configured")
    
    url = OPENWEATHER_BASE_URL
    params = {
        "q": city_name,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 404:
            raise ValidationError(f"City '{city_name}' not found. Please check the city name.")
        
        if response.status_code == 401:
            raise ExternalAPIError("Invalid OpenWeather API key")
        
        response.raise_for_status()
        data = response.json()
        
        # Validate response has required data
        if "main" not in data or "weather" not in data:
            raise ExternalAPIError("Invalid response from weather API")
        
        return data
        
    except requests.exceptions.Timeout:
        raise ExternalAPIError("Weather API request timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        raise ExternalAPIError("Failed to connect to weather API. Please check your internet connection.")
    except ValidationError:
        raise  # Re-raise validation errors
    except requests.exceptions.RequestException as e:
        raise ExternalAPIError(f"Failed to fetch weather data: {str(e)}")


def get_or_create_city(db: Session, city_name: str, lat: float, lon: float, country: str) -> City:
    """
    Checks if city exists in database. If not, creates it.
    """
    city = db.query(City).filter(City.name == city_name).first()
    
    if city:
        return city
    else:
        new_city = City(
            name=city_name,
            country=country,
            lat=lat,
            lon=lon,
            created_at=datetime.utcnow()
        )
        db.add(new_city)
        db.commit()
        db.refresh(new_city)
        return new_city


def save_weather_record(db: Session, city_id: int, weather_data: dict) -> WeatherRecord:
    """
    Saves a weather snapshot to the database.
    """
    main_data = weather_data.get("main", {})
    weather_info = weather_data.get("weather", [{}])[0]
    
    weather_record = WeatherRecord(
        city_id=city_id,
        temperature=main_data.get("temp"),
        humidity=main_data.get("humidity"),
        pressure=main_data.get("pressure"),
        weather_main=weather_info.get("main"),
        recorded_at=datetime.utcnow()
    )
    
    db.add(weather_record)
    db.commit()
    db.refresh(weather_record)
    return weather_record


def fetch_and_save_weather(db: Session, city_name: str) -> WeatherRecord:
    """
    Main function: Fetches weather from API and saves to database.
    
    Raises:
        ExternalAPIError: If API call fails
        ValidationError: If city not found
    """
    try:
        # Step 1: Fetch from API
        weather_data = fetch_weather_from_api(city_name)
        
        # Step 2: Extract city info
        city_name_from_api = weather_data.get("name")
        coord = weather_data.get("coord", {})
        lat = coord.get("lat")
        lon = coord.get("lon")
        country = weather_data.get("sys", {}).get("country")
        
        # Validate extracted data
        if not city_name_from_api or lat is None or lon is None:
            raise ExternalAPIError("Invalid weather data received from API")
        
        # Step 3: Get or create city
        city = get_or_create_city(db, city_name_from_api, lat, lon, country)
        
        # Step 4: Save weather record
        weather_record = save_weather_record(db, city.id, weather_data)
        
        return weather_record
    except (ExternalAPIError, ValidationError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise ExternalAPIError(f"Unexpected error while fetching weather: {str(e)}")