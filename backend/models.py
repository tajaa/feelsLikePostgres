from datetime import datetime

from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from database import Base

# Create a password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    SQLAlchemy model for the users table.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)  # Ensure usernames are unique
    hashed_password = Column(String)  # Store hashed passwords, never plain text
    last_login = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Auto-set to current time on creation
    last_login_lat = Column(Float)  # Store latitude of last login
    last_login_lon = Column(Float)  # Store longitude of last login
    feeling_score = Column(Integer)  # new column for storing users feeeling

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        """
        Generate a hash from a plain password.
        """
        return pwd_context.hash(password)


class Weather(Base):
    """
    SQLAlchemy model for the weather table.
    """

    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)  # Index for faster queries on city
    temperature = Column(Float)
    humidity = Column(Float)
    feels_like = Column(Float)
    wind_speed = Column(Float)
    data_source = Column(String)
    timestamp = Column(
        DateTime, default=datetime.utcnow
    )  # Auto-set to current time on creation
    is_average = Column(
        Boolean, default=False
    )  # Flag to indicate if this is an average record


# Pydantic models for request/response schemas


class UserCreate(BaseModel):
    """
    Pydantic model for user creation requests.
    """

    username: str
    password: str


class Token(BaseModel):
    """
    Pydantic model for token responses.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Pydantic model for token payload data.
    """

    username: str | None = None


class LocationUpdate(BaseModel):
    """
    Pydantic model for location update requests.
    """

    latitude: float
    longitude: float


class UserUpdate(BaseModel):
    """pydantic model for user update requests"""

    feeling_score: int
