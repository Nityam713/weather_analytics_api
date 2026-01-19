from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import City
from app.services.analytics_service import (
    get_daily_average_temperature,
    get_weather_trend,
    get_humidity_pressure_patterns,
    get_weekly_average_temperature,
    get_monthly_average_temperature,
    compare_cities,
    export_historical_data
)
from app.schemas import (
    DailyAverageResponse,
    TrendResponse,
    PatternsResponse,
    DailyAverageItem,
    DailyTrendData,
    WeeklyAverageResponse,
    WeeklyAverageItem,
    MonthlyAverageResponse,
    MonthlyAverageItem,
    CityComparisonResponse,
    HistoricalDataResponse,
    HistoricalRecord
)
from app.utils.validation import (
    validate_city_name,
    validate_date_format,
    validate_days,
    validate_weeks,
    validate_months
)
from app.utils.exceptions import ValidationError, CityNotFoundError, WeatherDataNotFoundError
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/daily-average", response_model=DailyAverageResponse)
def get_daily_average(city: str, days: int = None, db: Session = Depends(get_db)):
    """
    Get daily average temperature for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    - **days**: Number of days to look back (optional, None = all days, max: 365)
    """
    try:
        # Validate inputs
        city = validate_city_name(city)
        days = validate_days(days, max_days=365) if days else None
        
        # Find city by name
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found")
        
        # Get daily averages from service
        daily_averages = get_daily_average_temperature(db, city_obj.id, days)
        
        # Format response
        return DailyAverageResponse(
            city=city_obj.name,
            daily_averages=[
                DailyAverageItem(
                    date=item["date"],
                    avg_temperature=item["avg_temperature"],
                    record_count=item["record_count"]
                )
                for item in daily_averages
            ]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/trend", response_model=TrendResponse)
def get_trend(city: str, days: int = 7, db: Session = Depends(get_db)):
    """
    Get weather trend analysis for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    - **days**: Number of days to analyze (default: 7, max: 365)
    """
    try:
        # Validate inputs
        city = validate_city_name(city)
        days = validate_days(days, max_days=365)
        
        # Find city by name
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found")
        
        # Get trend analysis from service
        trend_data = get_weather_trend(db, city_obj.id, days)
        
        if not trend_data:
            raise WeatherDataNotFoundError(
                f"No weather records found for '{city}' in the last {days} days"
            )
        
        # Format response
        return TrendResponse(
            city=city_obj.name,
            period_days=days,
            avg_temperature=trend_data["avg_temperature"],
            min_temperature=trend_data["min_temperature"],
            max_temperature=trend_data["max_temperature"],
            temperature_change=trend_data["temperature_change"],
            trend_direction=trend_data["trend_direction"],
            record_count=trend_data["record_count"],
            daily_data=[
                DailyTrendData(
                    date=item["date"],
                    temperature=item["temperature"],
                    humidity=item["humidity"],
                    pressure=item["pressure"]
                )
                for item in trend_data["daily_data"]
            ]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (CityNotFoundError, WeatherDataNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/patterns", response_model=PatternsResponse)
def get_patterns(city: str, db: Session = Depends(get_db)):
    """
    Get humidity and pressure patterns for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    """
    try:
        # Validate inputs
        city = validate_city_name(city)
        
        # Find city by name
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found")
        
        # Get patterns from service
        patterns_data = get_humidity_pressure_patterns(db, city_obj.id)
        
        if not patterns_data:
            raise WeatherDataNotFoundError(f"No weather records found for '{city}'")
        
        # Format response
        return PatternsResponse(
            city=city_obj.name,
            humidity=patterns_data["humidity"],
            pressure=patterns_data["pressure"],
            weather_conditions=patterns_data["weather_conditions"],
            total_records=patterns_data["total_records"]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (CityNotFoundError, WeatherDataNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/weekly-average", response_model=WeeklyAverageResponse)
def get_weekly_average(city: str, weeks: int = 4, db: Session = Depends(get_db)):
    """
    Get weekly average temperature for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    - **weeks**: Number of weeks to look back (default: 4, max: 52)
    """
    try:
        # Validate inputs
        city = validate_city_name(city)
        weeks = validate_weeks(weeks, max_weeks=52)
        
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found")
        
        weekly_averages = get_weekly_average_temperature(db, city_obj.id, weeks)
        
        return WeeklyAverageResponse(
            city=city_obj.name,
            weekly_averages=[
                WeeklyAverageItem(
                    week_start=item["week_start"],
                    avg_temperature=item["avg_temperature"],
                    min_temperature=item["min_temperature"],
                    max_temperature=item["max_temperature"],
                    record_count=item["record_count"]
                )
                for item in weekly_averages
            ]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/monthly-average", response_model=MonthlyAverageResponse)
def get_monthly_average(city: str, months: int = 12, db: Session = Depends(get_db)):
    """
    Get monthly average temperature for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    - **months**: Number of months to look back (default: 12, max: 24)
    """
    try:
        # Validate inputs
        city = validate_city_name(city)
        months = validate_months(months, max_months=24)
        
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found")
        
        monthly_averages = get_monthly_average_temperature(db, city_obj.id, months)
        
        return MonthlyAverageResponse(
            city=city_obj.name,
            monthly_averages=[
                MonthlyAverageItem(
                    month_start=item["month_start"],
                    avg_temperature=item["avg_temperature"],
                    min_temperature=item["min_temperature"],
                    max_temperature=item["max_temperature"],
                    record_count=item["record_count"]
                )
                for item in monthly_averages
            ]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/compare", response_model=CityComparisonResponse)
def compare_cities_endpoint(cities: str, db: Session = Depends(get_db)):
    """
    Compare weather statistics between multiple cities.
    
    - **cities**: Comma-separated list of city names (e.g., "Tokyo,New York,London")
    """
    try:
        if not cities or not cities.strip():
            raise ValidationError("At least one city must be provided")
        
        # Parse and validate city names
        city_names = [city.strip() for city in cities.split(",") if city.strip()]
        
        if not city_names:
            raise ValidationError("At least one valid city must be provided")
        
        if len(city_names) > 10:
            raise ValidationError("Maximum 10 cities can be compared at once")
        
        # Validate each city name
        validated_cities = []
        for city in city_names:
            try:
                validated_cities.append(validate_city_name(city))
            except ValueError as e:
                raise ValidationError(f"Invalid city name '{city}': {str(e)}")
        
        comparison_data = compare_cities(db, validated_cities)
        
        if not comparison_data:
            raise CityNotFoundError("No valid cities found for comparison")
        
        return CityComparisonResponse(cities=comparison_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/export", response_model=HistoricalDataResponse)
def export_historical(
    city: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Export historical weather data for a city.
    
    - **city**: Name of the city (e.g., "Tokyo", "New York")
    - **start_date**: Start date in format YYYY-MM-DD (optional)
    - **end_date**: End date in format YYYY-MM-DD (optional)
    """
    try:
        # Validate inputs
        city = validate_city_name(city)
        
        # Parse and validate dates if provided
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = validate_date_format(start_date)
        if end_date:
            end_dt = validate_date_format(end_date)
        
        # Validate date range
        if start_dt and end_dt and start_dt > end_dt:
            raise ValidationError("start_date must be before or equal to end_date")
        
        # Find city
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise CityNotFoundError(f"City '{city}' not found")
        
        # Export data
        records = export_historical_data(db, city_obj.id, start_dt, end_dt)
        
        if not records:
            raise WeatherDataNotFoundError(
                f"No weather records found for '{city}'" +
                (f" between {start_date} and {end_date}" if start_date or end_date else "")
            )
        
        return HistoricalDataResponse(
            city=city_obj.name,
            total_records=len(records),
            start_date=start_date,
            end_date=end_date,
            records=[
                HistoricalRecord(
                    id=record["id"],
                    recorded_at=record["recorded_at"],
                    temperature=record["temperature"],
                    humidity=record["humidity"],
                    pressure=record["pressure"],
                    weather_main=record["weather_main"]
                )
                for record in records
            ]
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (CityNotFoundError, WeatherDataNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")