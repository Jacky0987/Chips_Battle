# -*- coding: utf-8 -*-
"""
股票模型

定义股票的数据结构和业务逻辑
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric
from sqlalchemy.sql import func
from models.base import Base


class Stock(Base):
    """股票模型
    
    表示股票信息
    """
    __tablename__ = 'stocks'
    
    id = Column(String(36), primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False, comment='股票代码')
    name = Column(String(100), nullable=False, comment='股票名称')
    company_name = Column(String(200), comment='公司名称')
    description = Column(Text, comment='公司描述')
    sector = Column(String(50), comment='行业')
    market_cap = Column(Numeric(20, 2), comment='市值')
    current_price = Column(Numeric(10, 2), comment='当前价格')
    opening_price = Column(Numeric(10, 2), comment='开盘价')
    closing_price = Column(Numeric(10, 2), comment='收盘价')
    high_price = Column(Numeric(10, 2), comment='最高价')
    low_price = Column(Numeric(10, 2), comment='最低价')
    volume = Column(Numeric(20, 0), comment='成交量')
    is_active = Column(Boolean, default=True, comment='是否激活')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def __repr__(self):
        return f"<Stock(id='{self.id}', symbol='{self.symbol}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'company_name': self.company_name,
            'description': self.description,
            'sector': self.sector,
            'market_cap': float(self.market_cap) if self.market_cap else 0,
            'current_price': float(self.current_price) if self.current_price else 0,
            'opening_price': float(self.opening_price) if self.opening_price else 0,
            'closing_price': float(self.closing_price) if self.closing_price else 0,
            'high_price': float(self.high_price) if self.high_price else 0,
            'low_price': float(self.low_price) if self.low_price else 0,
            'volume': int(self.volume) if self.volume else 0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }