from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PersonalAsset(Base):
    __tablename__ = 'personal_assets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    purchase_price = Column(Float)
    current_market_value = Column(Float)
    owner_id = Column(Integer, ForeignKey('users.id')) 