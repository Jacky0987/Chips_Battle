from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Industry(Base):
    __tablename__ = 'industries'
    
    code = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String) 