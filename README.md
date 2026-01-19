# 🌦️ Weather Analytics API

A FastAPI-based backend service that collects live weather data from the OpenWeather API, stores historical weather snapshots in PostgreSQL, and provides analytics-ready REST APIs for trend analysis and insights.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Database Schema](#database-schema)

## ✨ Features

### Phase 1: Data Collection
- ✅ Fetch live weather data from OpenWeather API
- ✅ Auto-create cities in database
- ✅ Store historical weather snapshots with timestamps
- ✅ RESTful API endpoints

### Phase 2: Analytics APIs
- ✅ Daily average temperature
- ✅ Weekly and monthly averages
- ✅ Weather trend analysis
- ✅ Humidity & pressure patterns
- ✅ City comparison
- ✅ Historical data export

### Additional Features
- ✅ Input validation and error handling
- ✅ Comprehensive error messages
- ✅ API documentation (Swagger UI)

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.128.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.45
- **Validation**: Pydantic 2.12.5
- **HTTP Client**: requests 2.32.5
- **Server**: Uvicorn 0.40.0

## 📁 Project Structure

```
weather_analytics_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── weather.py          # Weather endpoints
│   │   └── analytics.py        # Analytics endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_service.py  # OpenWeather API logic
│   │   └── analytics_service.py # Analytics business logic
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py      # Custom exceptions
│       └── validation.py      # Input validation
├── .env                        # Environment variables (not in git)
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.13+
- PostgreSQL 12+
- OpenWeather API key ([Get one here](https://openweathermap.org/api))

### Step 1: Clone and Navigate

```bash
cd weather_analytics_api
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup PostgreSQL Database

```bash
# Create database and user
sudo -u postgres psql

# In psql:
CREATE USER weather_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE weather_db OWNER weather_user;
GRANT ALL PRIVILEGES ON DATABASE weather_db TO weather_user;
\q
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://weather_user:your_password@localhost:5432/weather_db
OPENWEATHER_API_KEY=your_api_key_here
```

### Step 6: Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Step 7: Access API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENWEATHER_API_KEY` | OpenWeather API key | Yes |

Example `.env` file:
```env
DATABASE_URL=postgresql://weather_user:your_password@localhost:5432/weather_db
OPENWEATHER_API_KEY=your_api_key_here
```

## 📡 API Endpoints

### Health Check

**GET** `/health`
- Check API and database connectivity
- Response: `{"status": "ok", "db": "connected"}`

### Weather Endpoints

#### Get Current Weather
**GET** `/weather/current?city={city_name}`
- Fetches current weather from OpenWeather API and saves to database
- **Parameters**: `city` (required) - City name (e.g., "Tokyo", "New York")
- **Example**: `/weather/current?city=Tokyo`

#### Get Latest Weather
**GET** `/weather/latest?city={city_name}`
- Gets the latest weather record from database
- **Parameters**: `city` (required) - City name
- **Example**: `/weather/latest?city=Tokyo`

#### List All Cities
**GET** `/weather/cities`
- Get a list of all cities in the database
- **Parameters**: None
- **Example**: `/weather/cities`
- **Response**: Returns total count and list of all cities with their details

### Analytics Endpoints

#### Daily Average Temperature
**GET** `/analytics/daily-average?city={city_name}&days={days}`
- Get daily average temperature for a city
- **Parameters**: 
  - `city` (required) - City name
  - `days` (optional) - Number of days to look back (default: all days, max: 365)
- **Example**: `/analytics/daily-average?city=Tokyo&days=7`

#### Weather Trend Analysis
**GET** `/analytics/trend?city={city_name}&days={days}`
- Analyze weather trends over specified days
- **Parameters**:
  - `city` (required) - City name
  - `days` (optional) - Number of days (default: 7, max: 365)
- **Example**: `/analytics/trend?city=Tokyo&days=7`

#### Humidity & Pressure Patterns
**GET** `/analytics/patterns?city={city_name}`
- Get humidity and pressure patterns
- **Parameters**: `city` (required) - City name
- **Example**: `/analytics/patterns?city=Tokyo`

#### Weekly Average Temperature
**GET** `/analytics/weekly-average?city={city_name}&weeks={weeks}`
- Get weekly average temperature
- **Parameters**:
  - `city` (required) - City name
  - `weeks` (optional) - Number of weeks (default: 4, max: 52)
- **Example**: `/analytics/weekly-average?city=Tokyo&weeks=4`

#### Monthly Average Temperature
**GET** `/analytics/monthly-average?city={city_name}&months={months}`
- Get monthly average temperature
- **Parameters**:
  - `city` (required) - City name
  - `months` (optional) - Number of months (default: 12, max: 24)
- **Example**: `/analytics/monthly-average?city=Tokyo&months=12`

#### City Comparison
**GET** `/analytics/compare?cities={city1,city2,city3}`
- Compare weather statistics between multiple cities
- **Parameters**: `cities` (required) - Comma-separated city names (max: 10)
- **Example**: `/analytics/compare?cities=Tokyo,New York,London`

#### Historical Data Export
**GET** `/analytics/export?city={city_name}&start_date={date}&end_date={date}`
- Export historical weather data
- **Parameters**:
  - `city` (required) - City name
  - `start_date` (optional) - Start date (YYYY-MM-DD)
  - `end_date` (optional) - End date (YYYY-MM-DD)
- **Example**: `/analytics/export?city=Tokyo&start_date=2026-01-01&end_date=2026-01-19`

## 💡 Usage Examples

### Using cURL

```bash
# Get current weather for Tokyo
curl "http://127.0.0.1:8000/weather/current?city=Tokyo"

# List all cities
curl "http://127.0.0.1:8000/weather/cities"

# Get daily averages for last 7 days
curl "http://127.0.0.1:8000/analytics/daily-average?city=Tokyo&days=7"

# Compare cities
curl "http://127.0.0.1:8000/analytics/compare?cities=Tokyo,New York,London"

# Export historical data
curl "http://127.0.0.1:8000/analytics/export?city=Tokyo&start_date=2026-01-01&end_date=2026-01-19"
```

### Using Python requests

```python
import requests

base_url = "http://127.0.0.1:8000"

# Get current weather
response = requests.get(f"{base_url}/weather/current?city=Tokyo")
print(response.json())

# List all cities
response = requests.get(f"{base_url}/weather/cities")
print(response.json())

# Get trend analysis
response = requests.get(f"{base_url}/analytics/trend?city=Tokyo&days=7")
print(response.json())
```

## 🗄️ Database Schema

### Cities Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR | City name |
| country | VARCHAR | Country code |
| lat | FLOAT | Latitude |
| lon | FLOAT | Longitude |
| created_at | TIMESTAMP | Record creation time |

### Weather Records Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| city_id | INTEGER | Foreign key to cities |
| temperature | FLOAT | Temperature in Celsius |
| humidity | INTEGER | Humidity percentage |
| pressure | INTEGER | Atmospheric pressure |
| weather_main | VARCHAR | Weather condition (Clear, Rain, etc.) |
| recorded_at | TIMESTAMP | When weather was recorded |

## 🔒 Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Validation errors (invalid input)
- **404 Not Found**: City or data not found
- **503 Service Unavailable**: External API errors
- **500 Internal Server Error**: Unexpected errors

All errors return JSON with `error` and `detail` fields.

## 📝 Notes

- The API automatically creates database tables on startup
- Cities are auto-created when weather is fetched
- All weather fetches are stored with timestamps for historical analysis
- Input validation ensures data quality
- API keys and secrets are stored in `.env` (not committed to git)

## 🚧 Future Enhancements (Phase 3)

- Temperature prediction using ML
- Anomaly detection (heatwaves, storms)
- Seasonal pattern recognition
- Weather alerts and notifications

## 📄 License

This project is for educational purposes.

---

**Built with FastAPI, PostgreSQL, and OpenWeather API**

