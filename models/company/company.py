from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ceo_id = Column(Integer, ForeignKey('users.id'))
    cash = Column(Float)
    industry_code = Column(String)
    is_on_jcmarket = Column(Boolean) 