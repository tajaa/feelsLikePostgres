from sqlalchemy import Column, Float, Integer, String

from database import Base


class Weather(Base):
    __tablename__ = "weather"  # defines the table name in posgres
    # column definitions. these will be creatd as columns in postgres table
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)  # index 4 faster queries on this column
    humidity = Column(Float)

    # this class defines the strucutre of our weather table in postgresql
    # sqlalchemy orm will use this to create the table and interact with it
