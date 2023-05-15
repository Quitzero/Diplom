from sqlalchemy import Column, Integer, String, Float, Date, VARCHAR
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

class Poly(Base):
    __tablename__ = 'poly'
    id = Column(Integer, primary_key=True)
    Data_Collection = Column(VARCHAR(10))
    Cloud_Cover = Column(Integer)
    Time_Range = Column(Date)
    CORNER_UL_LAT_PRODUCT = Column(Float)
    CORNER_UL_LON_PRODUCT = Column(Float)
    CORNER_LL_LAT_PRODUCT = Column(Float)
    CORNER_LL_LON_PRODUCT = Column(Float)
    CORNER_LR_LAT_PRODUCT = Column(Float)
    CORNER_LR_LON_PRODUCT = Column(Float)
    CORNER_UR_LAT_PRODUCT = Column(Float)
    CORNER_UR_LON_PRODUCT = Column(Float)