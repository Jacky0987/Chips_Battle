from sqlalchemy import Column, Integer, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CreditProfile(Base):
    __tablename__ = 'credit_profiles'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    credit_score = Column(Float)
    history = Column(JSON) 