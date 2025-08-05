from sqlalchemy import Column, JSON, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Federation(Base):
    __tablename__ = 'federation'
    
    id = Column(String, primary_key=True)
    member_nations = Column(JSON)
    total_gdp = Column(Float)
    integration_progress = Column(Float)
    status = Column(String) 