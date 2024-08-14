import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Weather

load_dotenv()


TOMORROW_API = os.getenv("TOMORROW_API")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)

app = FastAPI()


@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    """for testing"""
    try:
        # Use text() to wrap the SQL string
        result = db.execute(text("SELECT 1")).fetchone()
        if result[0] == 1:
            return {"message": "Successfully connected to the database!"}
        else:
            raise HTTPException(
                status_code=500, detail="Unexpected result from database"
            )
    except SQLAlchemyError as e:
        # If there's an error, return the details
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )


def clean_numeric_string(s: str) -> float:
    """'remove non numerics"""
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

        # Convert timestamp to datetime if it's a string
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

        # Convert timestamp to datetime
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

        # store tomorrows io data
        tomorrow_db_entry = Weather(
            city=city,
            temperature=clean_numeric_string(tomorrow_weather["temperature"]),
            humidity=clean_numeric_string(tomorrow_weather["humidity"]),
            data_source="tomorrow.io",
        )
        db.add(tomorrow_db_entry)

        # store openweather data
        openweather_db_entry = Weather(
            city=city,
            temperature=clean_numeric_string(tomorrow_weather["temperature"]),
            humidity=clean_numeric_string(tomorrow_weather["humidity"]),
            data_source="Openweather",
        )
        db.add(openweather_db_entry)
        db.commit()

        return {
            "city": city,
            "tomorrow_io": tomorrow_weather,
            "openweather": openweather_weather,
            "message": "Weather data stored in database",
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected response format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# this fastapi app sets up a web server that connects to pstgres
# it uses sqlAlchemy orm to itneract w that database allwoing us to work with python objects instead of writing raw sql queries
