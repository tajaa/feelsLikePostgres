from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Weather

app = FastAPI()


@app.get("/")
def read_root():
    # a simple root endpoint
    return {"hello": "world"}


@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
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
def read_weather(city: str, db: Session = Depends(get_db)):
    # FastAPI route to get weather for a city
    # 'db: Session = Depends(get_db)' injects a database session into this function

    # Query the PostgreSQL database for weather data
    # This is equivalent to: SELECT * FROM weather WHERE city = {city} LIMIT 1
    weather = db.query(Weather).filter(Weather.city == city).first()

    if weather:
        # If found, return the weather data
        # FastAPI will automatically convert this SQLAlchemy model to JSON
        return weather
    return {"error": "City not found"}


# this fastapi app sets up a web server that connects to pstgres
# it uses sqlAlchemy orm to itneract w that database allwoing us to work with python objects instead of writing raw sql queries
