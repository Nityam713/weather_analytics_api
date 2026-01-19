from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models 
from app.routers import weather, analytics
from app.utils.exceptions import (
    ValidationError,
    CityNotFoundError,
    WeatherDataNotFoundError,
    ExternalAPIError
)

app = FastAPI(title="Weather Analytics API")

# Include routers
app.include_router(weather.router, prefix="/weather", tags=["weather"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(CityNotFoundError)
async def city_not_found_handler(request: Request, exc: CityNotFoundError):
    """Handle city not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "City Not Found", "detail": str(exc)}
    )


@app.exception_handler(WeatherDataNotFoundError)
async def weather_data_not_found_handler(request: Request, exc: WeatherDataNotFoundError):
    """Handle weather data not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Weather Data Not Found", "detail": str(exc)}
    )


@app.exception_handler(ExternalAPIError)
async def external_api_error_handler(request: Request, exc: ExternalAPIError):
    """Handle external API errors."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "External API Error", "detail": str(exc)}
    )


@app.on_event("startup")
def startup():
    # This creates tables
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok", "db": "connected"}

