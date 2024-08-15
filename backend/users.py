import os
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from database import get_db
from models import LocationUpdate, Token, TokenData, User, UserCreate, UserUpdate

router = APIRouter()

# Load secret key from environment variable, use a default for development
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a new access token.

    Args:
        data (dict): Payload to encode in the token.
        expires_delta (timedelta, optional): Token expiration time.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # Add expiration time to payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Decode and validate the access token, then return the current user.

    Args:
        token (str): The access token.
        db (Session): Database session.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return an access token.

    Args:
        user (UserCreate): User creation data.
        db (Session): Database session.

    Returns:
        dict: Access token and token type.

    Raises:
        HTTPException: If the username is already registered.
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = User.get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username and password.
        db (Session): Database session.

    Returns:
        dict: Access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not User.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/update-location")
def update_location(
    location: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the location of the current user.

    Args:
        location (LocationUpdate): New location data.
        current_user (User): The authenticated user.
        db (Session): Database session.

    Returns:
        dict: A message indicating successful update.
    """
    current_user.last_login = func.now()  # Update last login time
    current_user.last_login_lat = location.latitude
    current_user.last_login_lon = location.longitude
    db.commit()  # Commit changes to the database
    return {"message": "Location updated successfully"}


@router.post("/update-feeling")
def update_feeling(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """dupate the feeling score of the current user"""
    current_user.feeling_score = user_update.feeling_score
    db.commit()
    return {"message": "feeling score updated successfully"}


@router.get("/nearby-scores")
def get_nearby_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """get feeling scores for nearby users"""

    if current_user.last_login_lat is None or current_user.last_login_lon is None:
        raise HTTPException(status_code=400, detail="User location not available")

    # define maximum distance (in degrees) to consider nearby
    max_distance = 0.1

    nearby_users = (
        db.query(User)
        .filter(
            User.id != current_user.id,
            User.feeling_score.isnot(None),
            func.abs(User.last_login_lat - current_user.last_login_lat) <= max_distance,
            func.abs(User.last_login_lon - current_user.last_login_lon) <= max_distance,
        )
        .all()
    )
    return [
        {
            "feeling_score": user.feeling_score,
            "distance": (
                (user.last_login_lat - current_user.last_login_lat) ** 2
                + (user.last_login_lon - current_user.last_login_lon) ** 2
            )
            ** 0.5,
        }
        for user in nearby_users
    ]
