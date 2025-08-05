from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    bank_id = Column(String)
    balance = Column(Float) 