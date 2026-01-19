from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import WeatherRecord, City

def get_daily_average_temperature(db: Session, city_id: int, days: int = None):
    """
    Get daily average temperature for a city.

    Args:
        db: database session
        city_id: ID of the City
        days: number of days to look back (None = all days)
    
    Returns:
        List of dictionaries with date and average temperature
    """

    # Build base query
    query = db.query(
        func.date(WeatherRecord.recorded_at).label("date"),
        func.avg(WeatherRecord.temperature).label("average_temperature"),
        func.count(WeatherRecord.id).label("record_count")
    ).filter(
        WeatherRecord.city_id == city_id
    )

    # If days specified, filter by date range
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(WeatherRecord.recorded_at >= start_date)

    # Group by date and order
    results = query.group_by(
        func.date(WeatherRecord.recorded_at)
    ).order_by(
        func.date(WeatherRecord.recorded_at).desc()
    ).all()

    # Format results
    return [
        {
            "date": str(result.date),
            "avg_temperature": round(float(result.average_temperature), 2),
            "record_count": result.record_count
        }
        for result in results
    ]
    
    
def get_weather_trend(db: Session, city_id: int, days: int = 7):
    """
    Analyzes weather trends over specified days.
    
    Args:
        db: Database session
        city_id: ID of the city
        days: Number of days to analyze (default: 7)
    
    Returns:
        Dictionary with trend analysis
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get all records in date range
    records = db.query(WeatherRecord).filter(
        WeatherRecord.city_id == city_id,
        WeatherRecord.recorded_at >= start_date,
        WeatherRecord.recorded_at <= end_date
    ).order_by(WeatherRecord.recorded_at).all()
    
    if not records:
        return None
    
    # Extract temperatures
    temperatures = [record.temperature for record in records]
    
    # Calculate statistics
    avg_temp = sum(temperatures) / len(temperatures)
    min_temp = min(temperatures)
    max_temp = max(temperatures)
    
    # Determine trend direction
    first_half = temperatures[:len(temperatures)//2]
    second_half = temperatures[len(temperatures)//2:]
    
    first_avg = sum(first_half) / len(first_half) if first_half else 0
    second_avg = sum(second_half) / len(second_half) if second_half else 0
    
    temp_change = second_avg - first_avg
    
    if temp_change > 0.5:
        trend_direction = "increasing"
    elif temp_change < -0.5:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"
    
    # Format daily data
    daily_data = [
        {
            "date": record.recorded_at.strftime("%Y-%m-%d"),
            "temperature": record.temperature,
            "humidity": record.humidity,
            "pressure": record.pressure
        }
        for record in records
    ]
    
    return {
        "avg_temperature": round(avg_temp, 2),
        "min_temperature": round(min_temp, 2),
        "max_temperature": round(max_temp, 2),
        "temperature_change": round(temp_change, 2),
        "trend_direction": trend_direction,
        "record_count": len(records),
        "daily_data": daily_data
    }

def get_humidity_pressure_patterns(db: Session, city_id: int):
    """
    Analyzes humidity and pressure patterns for a city.
    
    Args:
        db: Database session
        city_id: ID of the city
    
    Returns:
        Dictionary with humidity, pressure, and weather condition statistics
    """
    # Get all records for the city
    records = db.query(WeatherRecord).filter(
        WeatherRecord.city_id == city_id
    ).all()
    
    if not records:
        return None
    
    # Extract values
    humidities = [record.humidity for record in records if record.humidity]
    pressures = [record.pressure for record in records if record.pressure]
    weather_conditions = [record.weather_main for record in records if record.weather_main]
    
    # Calculate humidity statistics
    humidity_stats = {
        "average": round(sum(humidities) / len(humidities), 2) if humidities else 0,
        "min": min(humidities) if humidities else 0,
        "max": max(humidities) if humidities else 0
    }
    
    # Calculate pressure statistics
    pressure_stats = {
        "average": round(sum(pressures) / len(pressures), 2) if pressures else 0,
        "min": min(pressures) if pressures else 0,
        "max": max(pressures) if pressures else 0
    }
    
    # Count weather conditions
    condition_counts = {}
    for condition in weather_conditions:
        condition_counts[condition] = condition_counts.get(condition, 0) + 1
    
    return {
        "humidity": humidity_stats,
        "pressure": pressure_stats,
        "weather_conditions": condition_counts,
        "total_records": len(records)
    }


def get_weekly_average_temperature(db: Session, city_id: int, weeks: int = 4):
    """
    Calculates weekly average temperature for a city.
    
    Args:
        db: Database session
        city_id: ID of the city
        weeks: Number of weeks to look back (default: 4)
    
    Returns:
        List of dictionaries with week and average temperature
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(weeks=weeks)
    
    # Query: Group by week (year-week)
    results = db.query(
        func.date_trunc('week', WeatherRecord.recorded_at).label('week_start'),
        func.avg(WeatherRecord.temperature).label('avg_temperature'),
        func.min(WeatherRecord.temperature).label('min_temperature'),
        func.max(WeatherRecord.temperature).label('max_temperature'),
        func.count(WeatherRecord.id).label('record_count')
    ).filter(
        WeatherRecord.city_id == city_id,
        WeatherRecord.recorded_at >= start_date
    ).group_by(
        func.date_trunc('week', WeatherRecord.recorded_at)
    ).order_by(
        func.date_trunc('week', WeatherRecord.recorded_at).desc()
    ).all()
    
    return [
        {
            "week_start": result.week_start.strftime("%Y-%m-%d"),
            "avg_temperature": round(float(result.avg_temperature), 2),
            "min_temperature": round(float(result.min_temperature), 2),
            "max_temperature": round(float(result.max_temperature), 2),
            "record_count": result.record_count
        }
        for result in results
    ]


def get_monthly_average_temperature(db: Session, city_id: int, months: int = 12):
    """
    Calculates monthly average temperature for a city.
    
    Args:
        db: Database session
        city_id: ID of the city
        months: Number of months to look back (default: 12)
    
    Returns:
        List of dictionaries with month and average temperature
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)  # Approximate months
    
    # Query: Group by year-month
    results = db.query(
        func.date_trunc('month', WeatherRecord.recorded_at).label('month_start'),
        func.avg(WeatherRecord.temperature).label('avg_temperature'),
        func.min(WeatherRecord.temperature).label('min_temperature'),
        func.max(WeatherRecord.temperature).label('max_temperature'),
        func.count(WeatherRecord.id).label('record_count')
    ).filter(
        WeatherRecord.city_id == city_id,
        WeatherRecord.recorded_at >= start_date
    ).group_by(
        func.date_trunc('month', WeatherRecord.recorded_at)
    ).order_by(
        func.date_trunc('month', WeatherRecord.recorded_at).desc()
    ).all()
    
    return [
        {
            "month_start": result.month_start.strftime("%Y-%m"),
            "avg_temperature": round(float(result.avg_temperature), 2),
            "min_temperature": round(float(result.min_temperature), 2),
            "max_temperature": round(float(result.max_temperature), 2),
            "record_count": result.record_count
        }
        for result in results
    ]


def compare_cities(db: Session, city_names: list[str]):
    """
    Compares weather statistics between multiple cities.
    
    Args:
        db: Database session
        city_names: List of city names to compare
    
    Returns:
        Dictionary with comparison data for each city
    """
    comparison_data = {}
    
    for city_name in city_names:
        city_obj = db.query(City).filter(City.name == city_name).first()
        if not city_obj:
            continue
        
        # Get all records for the city
        records = db.query(WeatherRecord).filter(
            WeatherRecord.city_id == city_obj.id
        ).all()
        
        if not records:
            continue
        
        # Calculate statistics
        temperatures = [r.temperature for r in records if r.temperature]
        humidities = [r.humidity for r in records if r.humidity]
        pressures = [r.pressure for r in records if r.pressure]
        
        comparison_data[city_name] = {
            "city_id": city_obj.id,
            "country": city_obj.country,
            "temperature": {
                "average": round(sum(temperatures) / len(temperatures), 2) if temperatures else 0,
                "min": round(min(temperatures), 2) if temperatures else 0,
                "max": round(max(temperatures), 2) if temperatures else 0
            },
            "humidity": {
                "average": round(sum(humidities) / len(humidities), 2) if humidities else 0,
                "min": min(humidities) if humidities else 0,
                "max": max(humidities) if humidities else 0
            },
            "pressure": {
                "average": round(sum(pressures) / len(pressures), 2) if pressures else 0,
                "min": min(pressures) if pressures else 0,
                "max": max(pressures) if pressures else 0
            },
            "total_records": len(records),
            "latest_record": records[-1].recorded_at.strftime("%Y-%m-%d %H:%M:%S") if records else None
        }
    
    return comparison_data


def export_historical_data(db: Session, city_id: int, start_date: datetime = None, end_date: datetime = None):
    """
    Exports historical weather data for a city.
    
    Args:
        db: Database session
        city_id: ID of the city
        start_date: Start date for export (None = all records)
        end_date: End date for export (None = all records)
    
    Returns:
        List of dictionaries with all weather record data
    """
    query = db.query(WeatherRecord).filter(WeatherRecord.city_id == city_id)
    
    if start_date:
        query = query.filter(WeatherRecord.recorded_at >= start_date)
    if end_date:
        query = query.filter(WeatherRecord.recorded_at <= end_date)
    
    records = query.order_by(WeatherRecord.recorded_at).all()
    
    return [
        {
            "id": record.id,
            "recorded_at": record.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": record.temperature,
            "humidity": record.humidity,
            "pressure": record.pressure,
            "weather_main": record.weather_main
        }
        for record in records
    ]