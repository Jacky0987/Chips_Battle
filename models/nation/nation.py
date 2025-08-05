from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Nation(Base):
    __tablename__ = 'nations'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    government_type = Column(String)
    policies = Column(JSON)
    stability = Column(Float)
    relations = Column(JSON)
    player_influence = Column(Float) 