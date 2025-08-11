# -*- coding: utf-8 -*-
"""
股票价格模型

定义股票价格历史记录
"""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class StockPrice(Base):
    """股票价格模型
    
    表示股票价格历史记录
    """
    __tablename__ = 'stock_prices'
    
    id = Column(String(36), primary_key=True)
    stock_id = Column(String(36), ForeignKey('stocks.id'), nullable=False, comment='股票ID')
    price = Column(Numeric(10, 2), nullable=False, comment='价格')
    opening_price = Column(Numeric(10, 2), comment='开盘价')
    closing_price = Column(Numeric(10, 2), comment='收盘价')
    high_price = Column(Numeric(10, 2), comment='最高价')
    low_price = Column(Numeric(10, 2), comment='最低价')
    volume = Column(Numeric(20, 0), comment='成交量')
    timestamp = Column(DateTime, default=func.now(), comment='时间戳')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    
    # 关系
    stock = relationship("Stock")
    
    def __repr__(self):
        return f"<StockPrice(id='{self.id}', stock_id='{self.stock_id}', price='{self.price}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'price': float(self.price) if self.price else 0,
            'opening_price': float(self.opening_price) if self.opening_price else 0,
            'closing_price': float(self.closing_price) if self.closing_price else 0,
            'high_price': float(self.high_price) if self.high_price else 0,
            'low_price': float(self.low_price) if self.low_price else 0,
            'volume': int(self.volume) if self.volume else 0,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }