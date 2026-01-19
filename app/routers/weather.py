from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.weather_service import fetch_and_save_weather
from app.schemas import WeatherCurrentResponse, WeatherRecordResponse, CityResponse, CitiesListResponse
from app.models import City, WeatherRecord
from app.utils.validation import validate_city_name
from app.utils.exceptions import ExternalAPIError, ValidationError, CityNotFoundError, WeatherDataNotFoundError

router = APIRouter()


@router.get("/current", response_model=WeatherCurrentResponse)
def get_current_weather(city: str, db: Session = Depends(get_db)):
    """
    Fetches current weather data for a city and saves it to the database.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    """
    try:
        # Validate city name
        city = validate_city_name(city)
        
        # Call service to fetch from API and save to DB
        weather_record = fetch_and_save_weather(db, city)
        
        # Get the city object from the relationship
        city_obj = weather_record.city
        
        # Convert to response schemas
        city_response = CityResponse.from_orm(city_obj)
        weather_response = WeatherRecordResponse.from_orm(weather_record)
        
        # Return combined response
        return WeatherCurrentResponse(city=city_response, weather=weather_response)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/latest", response_model=WeatherRecordResponse)
def get_latest_weather(city: str, db: Session = Depends(get_db)):
    """
    Fetches the latest weather record for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    """
    try:
        # Validate city name
        city = validate_city_name(city)
        
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found in database")
        
        latest_record = (
            db.query(WeatherRecord)
            .filter(WeatherRecord.city_id == city_obj.id)
            .order_by(WeatherRecord.recorded_at.desc())
            .first()
        )
        
        if not latest_record:
            raise WeatherDataNotFoundError(f"No weather records found for '{city}'")
        
        return WeatherRecordResponse.from_orm(latest_record)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (CityNotFoundError, WeatherDataNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/cities", response_model=CitiesListResponse)
def list_cities(db: Session = Depends(get_db)):
    """
    Get a list of all cities in the database.
    
    Returns all cities that have been added to the database.
    """
    try:
        cities = db.query(City).order_by(City.name).all()
        
        return CitiesListResponse(
            total=len(cities),
            cities=[CityResponse.from_orm(city) for city in cities]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")