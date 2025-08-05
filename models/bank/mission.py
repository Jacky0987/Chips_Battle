from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BankMission(Base):
    __tablename__ = 'bank_missions'
    
    id = Column(String, primary_key=True)
    bank_id = Column(String)
    title = Column(String)
    description = Column(String)
    requirements = Column(JSON)
    rewards = Column(JSON)
    deadline = Column(DateTime) 