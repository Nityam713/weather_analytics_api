from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Request schemas (what users send TO your API)
class CityCreate(BaseModel):
    name: str
    country: str
    lat: float
    lon: float

# Response schemas (what your API sends BACK)
class CityResponse(BaseModel):
    id: int
    name: str
    country: str
    lat: float
    lon: float
    created_at: datetime

    class Config:
        from_attributes = True


class CitiesListResponse(BaseModel):
    """Response schema for listing all cities."""
    total: int
    cities: list[CityResponse]


# Weather Record Response Schema
class WeatherRecordResponse(BaseModel):
    id: int
    city_id: int
    temperature: float
    humidity: int
    pressure: int
    weather_main: str
    recorded_at: datetime

    class Config:
        from_attributes = True


# Combined response: City + Weather (for /weather/current endpoint)
class WeatherCurrentResponse(BaseModel):
    city: CityResponse
    weather: WeatherRecordResponse


# Daily Average Response Schema
class DailyAverageItem(BaseModel):
    date: str
    avg_temperature: float
    record_count: int


class DailyAverageResponse(BaseModel):
    city: str
    daily_averages: list[DailyAverageItem]


# Trend Analysis Response Schema
class DailyTrendData(BaseModel):
    date: str
    temperature: float
    humidity: int
    pressure: int


class TrendResponse(BaseModel):
    city: str
    period_days: int
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    temperature_change: float
    trend_direction: str
    record_count: int
    daily_data: list[DailyTrendData]


# Humidity & Pressure Patterns Response Schema
class HumidityStats(BaseModel):
    average: float
    min: int
    max: int


class PressureStats(BaseModel):
    average: float
    min: int
    max: int


class PatternsResponse(BaseModel):
    city: str
    humidity: HumidityStats
    pressure: PressureStats
    weather_conditions: dict[str, int]
    total_records: int


# Weekly Average Response Schema
class WeeklyAverageItem(BaseModel):
    week_start: str
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    record_count: int


class WeeklyAverageResponse(BaseModel):
    city: str
    weekly_averages: list[WeeklyAverageItem]


# Monthly Average Response Schema
class MonthlyAverageItem(BaseModel):
    month_start: str
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    record_count: int


class MonthlyAverageResponse(BaseModel):
    city: str
    monthly_averages: list[MonthlyAverageItem]


# City Comparison Response Schema
class CityTemperatureStats(BaseModel):
    average: float
    min: float
    max: float


class CityHumidityStats(BaseModel):
    average: float
    min: int
    max: int


class CityPressureStats(BaseModel):
    average: float
    min: int
    max: int


class CityComparisonData(BaseModel):
    city_id: int
    country: str
    temperature: CityTemperatureStats
    humidity: CityHumidityStats
    pressure: CityPressureStats
    total_records: int
    latest_record: Optional[str]


class CityComparisonResponse(BaseModel):
    cities: dict[str, CityComparisonData]


# Historical Data Export Response Schema
class HistoricalRecord(BaseModel):
    id: int
    recorded_at: str
    temperature: float
    humidity: int
    pressure: int
    weather_main: str


class HistoricalDataResponse(BaseModel):
    city: str
    total_records: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    records: list[HistoricalRecord]