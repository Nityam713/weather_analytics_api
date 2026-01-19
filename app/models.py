from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    weather_records = relationship("WeatherRecord", back_populates="city")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    temperature = Column(Float)
    humidity = Column(Integer)
    pressure = Column(Integer)
    weather_main = Column(String)
    recorded_at = Column(DateTime)

    city = relationship("City", back_populates="weather_records")
