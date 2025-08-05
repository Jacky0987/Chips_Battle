from sqlalchemy import Column, String, JSON, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Alliance(Base):
    __tablename__ = 'alliances'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    members = Column(JSON)
    shared_treasury = Column(Float)
    alliance_tech_tree = Column(JSON)
    joint_ventures = Column(JSON) 