from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GlobalStock(Base):
    __tablename__ = 'global_stocks'
    
    symbol = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float) 