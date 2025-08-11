# -*- coding: utf-8 -*-
"""
股票模型

定义股票的数据结构和业务逻辑
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric
from sqlalchemy.sql import func
from models.base import Base
import uuid


class Stock(Base):
    """股票模型
    
    表示股票信息
    """
    __tablename__ = 'stocks'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(10), unique=True, nullable=False, comment='股票代码')
    name = Column(String(100), nullable=False, comment='股票名称')
    company_name = Column(String(200), comment='公司名称')
    description = Column(Text, comment='公司描述')
    sector = Column(String(50), comment='行业')
    market_cap = Column(Numeric(20, 2), comment='市值')
    ipo_price = Column(Numeric(10, 2), comment='IPO价格')
    volatility = Column(Numeric(10, 4), comment='波动率')
    current_price = Column(Numeric(10, 2), comment='当前价格')
    opening_price = Column(Numeric(10, 2), comment='开盘价')
    closing_price = Column(Numeric(10, 2), comment='收盘价')
    previous_close = Column(Numeric(10, 2), comment='昨日收盘价')
    high_price = Column(Numeric(10, 2), comment='最高价')
    low_price = Column(Numeric(10, 2), comment='最低价')
    day_high = Column(Numeric(10, 2), comment='今日最高价')
    day_low = Column(Numeric(10, 2), comment='今日最低价')
    volume = Column(Numeric(20, 0), comment='成交量')
    total_shares = Column(Numeric(20, 0), comment='总股本')
    
    # 财务指标
    pe_ratio = Column(Numeric(10, 2), comment='市盈率 (P/E Ratio)')
    beta = Column(Numeric(10, 4), comment='贝塔系数 (Beta)')
    dividend_yield = Column(Numeric(10, 4), comment='股息收益率 (Dividend Yield)')
    eps = Column(Numeric(10, 2), comment='每股收益 (Earnings Per Share)')
    book_value = Column(Numeric(10, 2), comment='每股净资产 (Book Value Per Share)')
    debt_to_equity = Column(Numeric(10, 4), comment='负债权益比 (Debt-to-Equity Ratio)')
    
    # 技术指标
    rsi = Column(Numeric(10, 2), comment='相对强弱指数 (RSI)')
    moving_avg_50 = Column(Numeric(10, 2), comment='50日移动平均线')
    moving_avg_200 = Column(Numeric(10, 2), comment='200日移动平均线')
    
    # 市场表现
    year_high = Column(Numeric(10, 2), comment='52周最高价')
    year_low = Column(Numeric(10, 2), comment='52周最低价')
    ytd_return = Column(Numeric(10, 4), comment='年初至今回报率')
    
    is_active = Column(Boolean, default=True, comment='是否激活')
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), comment='最后更新时间')
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
            'previous_close': float(self.previous_close) if self.previous_close else 0,
            'high_price': float(self.high_price) if self.high_price else 0,
            'low_price': float(self.low_price) if self.low_price else 0,
            'day_high': float(self.day_high) if self.day_high else 0,
            'day_low': float(self.day_low) if self.day_low else 0,
            'volume': int(self.volume) if self.volume else 0,
            'total_shares': int(self.total_shares) if self.total_shares else 0,
            
            # 财务指标
            'pe_ratio': float(self.pe_ratio) if self.pe_ratio else 0,
            'beta': float(self.beta) if self.beta else 0,
            'dividend_yield': float(self.dividend_yield) if self.dividend_yield else 0,
            'eps': float(self.eps) if self.eps else 0,
            'book_value': float(self.book_value) if self.book_value else 0,
            'debt_to_equity': float(self.debt_to_equity) if self.debt_to_equity else 0,
            
            # 技术指标
            'rsi': float(self.rsi) if self.rsi else 0,
            'moving_avg_50': float(self.moving_avg_50) if self.moving_avg_50 else 0,
            'moving_avg_200': float(self.moving_avg_200) if self.moving_avg_200 else 0,
            
            # 市场表现
            'year_high': float(self.year_high) if self.year_high else 0,
            'year_low': float(self.year_low) if self.year_low else 0,
            'ytd_return': float(self.ytd_return) if self.ytd_return else 0,
            
            'is_active': self.is_active,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }