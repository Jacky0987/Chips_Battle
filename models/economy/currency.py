from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Currency(Base):
    __tablename__ = 'currencies'
    
    code = Column(String, primary_key=True)
    name = Column(String)
    symbol = Column(String)
    base_rate = Column(Float)
    current_rate = Column(Float)
    volatility = Column(Float) 