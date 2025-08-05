from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AICorporation(Base):
    __tablename__ = 'ai_corporations'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    strategy = Column(String)
    capital = Column(Float)
    tech_reserve = Column(JSON) 