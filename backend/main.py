import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Weather

load_dotenv()
app = FastAPI()

TOMORROW_API = os.getenv("TOMORROW_API")


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


@app.get("/weather/{city}")
async def get_weather(city: str):
    """simple get weather"""
    url = "https://api.tomorrow.io/v4/weather/realtime"

    # query params
    params = {"location": city, "apikey": TOMORROW_API, "units": "imperial"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            weather_data = response.json()

            # extract relevant wather info
            temperature = weather_data["data"]["values"]["temperature"]
            humidity = weather_data["data"]["values"]["humidity"]
            return {"city": city, "temperature": temperature, "humidity": humidity}

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except KeyError as e:
            raise HTTPException(
                status_code=500, detail=f"unexected response format: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"an error occured: {str(3)}")


# this fastapi app sets up a web server that connects to pstgres
# it uses sqlAlchemy orm to itneract w that database allwoing us to work with python objects instead of writing raw sql queries
