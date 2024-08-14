from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from database import Base

Base = declarative_base()


class Weather(Base):
    __tablename__ = "weather"  # defines the table name in posgres
    # column definitions. these will be creatd as columns in postgres table

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)  # index 4 faster queries on this column
    temperature = Column(Float)
    humidity = Column(Float)
    feels_like = Column(Float)
    wind_speed = Column(Float)
    data_source = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # this class defines the strucutre of our weather table in postgresql
    # sqlalchemy orm will use this to create the table and interact with it
