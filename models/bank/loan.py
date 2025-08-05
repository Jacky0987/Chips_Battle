from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Loan(Base):
    __tablename__ = 'loans'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    bank_id = Column(String)
    amount = Column(Float)
    interest_rate = Column(Float)
    issue_date = Column(DateTime)
    due_date = Column(DateTime)
    status = Column(String) 