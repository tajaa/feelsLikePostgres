import os
import sys
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Weather
from users import router as users_router

load_dotenv()

TOMORROW_API = os.getenv("TOMORROW_API")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router)


def setup_database(should_drop=False):
    if should_drop:
        Base.metadata.drop_all(bind=engine)
        print("dropped all tables")
    Base.metadata.create_all(bind=engine)
    print("created all tables")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--drop-and-create":
            setup_database(should_drop=True)
        elif sys.argv[1] == "--create":
            setup_database()
    else:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result[0] == 1:
            return {"message": "Successfully connected to the database!"}
        else:
            raise HTTPException(
                status_code=500, detail="Unexpected result from database"
            )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )


def clean_numeric_string(s: str) -> float:
    cleaned = "".join(char for char in s if char.isdigit() or char == ".")
    return float(cleaned)


async def get_tomorrow_weather(city: str):
    url = "https://api.tomorrow.io/v4/weather/realtime"
    params = {"location": city, "apikey": TOMORROW_API, "units": "imperial"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        values = weather_data["data"]["values"]
        timestamp = weather_data["data"]["time"]

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.rstrip("Z")).replace(
                tzinfo=timezone.utc
            )
        else:
            timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        return {
            "temperature": f"{values['temperature']}°F",
            "feels_like": f"{values['temperatureApparent']}°F",
            "humidity": f"{values['humidity']}%",
            "wind_speed": f"{values['windSpeed']} mph",
            "data_time": timestamp.isoformat(),
            "data_source": "Tomorrow.io API",
        }


async def get_openweather_weather(city: str):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHERMAP_API_KEY, "units": "imperial"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        timestamp = weather_data["dt"]
        timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        return {
            "temperature": f"{weather_data['main']['temp']}°F",
            "feels_like": f"{weather_data['main']['feels_like']}°F",
            "humidity": f"{weather_data['main']['humidity']}%",
            "wind_speed": f"{weather_data['wind']['speed']} mph",
            "data_time": timestamp.isoformat(),
            "data_source": "OpenWeather API",
        }


@app.get("/weather/compare/{city}")
async def compare_weather(city: str, db: Session = Depends(get_db)):
    try:
        tomorrow_weather = await get_tomorrow_weather(city)
        openweather_weather = await get_openweather_weather(city)

        def safe_clean_numeric(value):
            if value is None:
                return None
            try:
                return float(
                    "".join(
                        char for char in str(value) if char.isdigit() or char == "."
                    )
                )
            except ValueError:
                return None

        def safe_average(val1, val2):
            cleaned1, cleaned2 = safe_clean_numeric(val1), safe_clean_numeric(val2)
            if cleaned1 is not None and cleaned2 is not None:
                return (cleaned1 + cleaned2) / 2
            return cleaned1 or cleaned2

        avg_temperature = safe_average(
            tomorrow_weather.get("temperature"), openweather_weather.get("temperature")
        )

        weather_entries = [
            Weather(
                city=city,
                temperature=safe_clean_numeric(data.get("temperature")),
                humidity=safe_clean_numeric(data.get("humidity")),
                feels_like=safe_clean_numeric(data.get("feels_like")),
                wind_speed=safe_clean_numeric(data.get("wind_speed")),
                data_source=source,
                is_average=(source == "Average"),
            )
            for source, data in [
                ("tomorrow.io", tomorrow_weather),
                ("OpenWeather", openweather_weather),
                (
                    "Average",
                    {
                        "temperature": avg_temperature,
                        "humidity": safe_average(
                            tomorrow_weather.get("humidity"),
                            openweather_weather.get("humidity"),
                        ),
                        "feels_like": safe_average(
                            tomorrow_weather.get("feels_like"),
                            openweather_weather.get("feels_like"),
                        ),
                        "wind_speed": safe_average(
                            tomorrow_weather.get("wind_speed"),
                            openweather_weather.get("wind_speed"),
                        ),
                    },
                ),
            ]
        ]

        db.add_all(weather_entries)
        db.commit()

        def format_value(value, unit=""):
            return f"{value:.1f}{unit}" if value is not None else "N/A"

        return {
            "city": city,
            "tomorrow_io": tomorrow_weather,
            "openweather": openweather_weather,
            "average": {
                "temperature": format_value(avg_temperature, "°F"),
                "humidity": format_value(weather_entries[2].humidity, "%"),
                "feels_like": format_value(weather_entries[2].feels_like, "°F"),
                "wind_speed": format_value(weather_entries[2].wind_speed, " mph"),
            },
            "message": "Weather data and average stored in database",
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/initial-weather")
def get_initial_weather(db: Session = Depends(get_db)):
    try:
        latest_weather = db.query(Weather).order_by(Weather.timestamp.desc()).first()

        if latest_weather:
            return {
                "city": latest_weather.city,
                "average": {
                    "temperature": f"{latest_weather.temperature:.1f}°F",
                    "humidity": f"{latest_weather.humidity:.1f}%",
                    "feels_like": f"{latest_weather.feels_like:.1f}°F",
                    "wind_speed": f"{latest_weather.wind_speed:.1f} mph",
                },
            }
        else:
            raise HTTPException(status_code=404, detail="No weather data available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
