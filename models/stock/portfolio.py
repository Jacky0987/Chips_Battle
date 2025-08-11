# -*- coding: utf-8 -*-
"""
投资组合模型

定义用户的股票投资组合
"""

from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class Portfolio(Base):
    """投资组合模型
    
    表示用户的投资组合
    """
    __tablename__ = 'portfolios'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, comment='用户ID')
    name = Column(String(100), nullable=False, comment='组合名称')
    description = Column(String(500), comment='组合描述')
    total_value = Column(Numeric(20, 2), default=0, comment='总价值')
    total_cost = Column(Numeric(20, 2), default=0, comment='总成本')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    user = relationship("User")
    items = relationship("PortfolioItem", back_populates="portfolio")
    
    def __repr__(self):
        return f"<Portfolio(id='{self.id}', user_id='{self.user_id}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'total_value': float(self.total_value) if self.total_value else 0,
            'total_cost': float(self.total_cost) if self.total_cost else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PortfolioItem(Base):
    """投资组合项目模型
    
    表示投资组合中的具体股票持仓
    """
    __tablename__ = 'portfolio_items'
    
    id = Column(String(36), primary_key=True)
    portfolio_id = Column(String(36), ForeignKey('portfolios.id'), nullable=False, comment='投资组合ID')
    stock_id = Column(String(36), ForeignKey('stocks.id'), nullable=False, comment='股票ID')
    quantity = Column(Integer, nullable=False, comment='持有数量')
    average_cost = Column(Numeric(10, 2), comment='平均成本')
    current_value = Column(Numeric(20, 2), comment='当前价值')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    portfolio = relationship("Portfolio", back_populates="items")
    stock = relationship("Stock")
    
    def __repr__(self):
        return f"<PortfolioItem(id='{self.id}', portfolio_id='{self.portfolio_id}', stock_id='{self.stock_id}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'stock_id': self.stock_id,
            'quantity': self.quantity,
            'average_cost': float(self.average_cost) if self.average_cost else 0,
            'current_value': float(self.current_value) if self.current_value else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }