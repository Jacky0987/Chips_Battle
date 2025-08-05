from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    
    id = Column(Integer, primary_key=True)
    headline = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
    source = Column(String)
    impact_tags = Column(JSON) 