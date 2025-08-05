from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserAppOwnership(Base):
    __tablename__ = 'user_app_ownership'
    
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    app_id = Column(String, ForeignKey('apps.id'), primary_key=True)
    install_date = Column(DateTime) 