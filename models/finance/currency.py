# -*- coding: utf-8 -*-
"""
货币模型

定义游戏中的货币系统，包括不同类型的货币和汇率管理。
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from models.base import BaseModel, SoftDeleteMixin


class Currency(BaseModel, SoftDeleteMixin):
    """货币模型
    
    管理游戏中的各种货币类型，如筹码、积分、代币等。
    """
    
    __tablename__ = 'currencies'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='货币ID')
    
    # 基本信息
    code = Column(String(10), unique=True, nullable=False, comment='货币代码')
    name = Column(String(50), nullable=False, comment='货币名称')
    symbol = Column(String(10), nullable=False, comment='货币符号')
    
    # 货币属性
    decimal_places = Column(Integer, default=2, comment='小数位数')
    exchange_rate = Column(Float, default=1.0, comment='对基础货币的汇率')
    
    # 状态
    is_active = Column(Boolean, default=True, comment='是否启用')
    is_base_currency = Column(Boolean, default=False, comment='是否为基础货币')
    
    # 描述
    description = Column(Text, comment='货币描述')
    
    def __repr__(self):
        return f"<Currency(code='{self.code}', name='{self.name}', symbol='{self.symbol}')>"
    
    def format_amount(self, amount: float) -> str:
        """格式化金额显示
        
        Args:
            amount: 金额
            
        Returns:
            格式化后的金额字符串
        """
        formatted = f"{amount:.{self.decimal_places}f}"
        return f"{self.symbol}{formatted}"
    
    @classmethod
    def get_base_currency(cls, session):
        """获取基础货币
        
        Args:
            session: 数据库会话
            
        Returns:
            基础货币对象
        """
        return session.query(cls).filter_by(is_base_currency=True, is_active=True).first()
    
    @classmethod
    def get_by_code(cls, session, code: str):
        """根据货币代码获取货币
        
        Args:
            session: 数据库会话
            code: 货币代码
            
        Returns:
            货币对象
        """
        return session.query(cls).filter_by(code=code, is_active=True).first()