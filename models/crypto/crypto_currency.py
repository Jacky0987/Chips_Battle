from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CryptoCurrency(Base):
    __tablename__ = 'crypto_currencies'
    
    symbol = Column(String, primary_key=True)
    name = Column(String)
    current_price = Column(Float)
    total_supply = Column(Float)
    circulating_supply = Column(Float)
    hash_rate = Column(Float)
    algorithm = Column(String) 