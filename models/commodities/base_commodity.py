from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseCommodity(Base):
    __tablename__ = 'commodities'
    
    symbol = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float)
    unit = Column(String)
    volatility = Column(Float) 