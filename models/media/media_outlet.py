from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MediaOutlet(Base):
    __tablename__ = 'media_outlets'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    reach = Column(Integer)
    credibility = Column(Float)
    bias = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id')) 