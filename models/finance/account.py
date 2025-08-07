# -*- coding: utf-8 -*-
"""
账户模型

定义用户的金融账户，包括余额、交易记录等。
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import BaseModel, SoftDeleteMixin


class Account(BaseModel, SoftDeleteMixin):
    """账户模型
    
    管理用户的金融账户信息，包括不同货币的余额。
    """
    
    __tablename__ = 'accounts'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='账户ID')
    
    # 关联用户
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, comment='用户ID')
    
    # 账户信息
    account_number = Column(String(50), unique=True, nullable=False, comment='账户号码')
    account_name = Column(String(100), nullable=False, comment='账户名称')
    account_type = Column(String(20), nullable=False, default='TRADING', comment='账户类型')
    
    # 货币信息
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False, comment='货币ID')
    
    # 余额信息
    balance = Column(Float, default=0.0, nullable=False, comment='账户余额')
    available_balance = Column(Float, default=0.0, nullable=False, comment='可用余额')
    frozen_balance = Column(Float, default=0.0, nullable=False, comment='冻结余额')
    
    # 状态
    is_active = Column(Boolean, default=True, comment='是否启用')
    is_default = Column(Boolean, default=False, comment='是否为默认账户')
    
    # 限制
    daily_limit = Column(Float, comment='日交易限额')
    monthly_limit = Column(Float, comment='月交易限额')
    
    # 描述
    description = Column(Text, comment='账户描述')
    
    # 关系
    user = relationship("User", back_populates="accounts")
    currency = relationship("Currency")
    
    def __repr__(self):
        return f"<Account(number='{self.account_number}', balance={self.balance}, currency_id={self.currency_id})>"
    
    def get_total_balance(self) -> float:
        """获取总余额（可用+冻结）
        
        Returns:
            总余额
        """
        return self.available_balance + self.frozen_balance
    
    def can_withdraw(self, amount: float) -> bool:
        """检查是否可以提取指定金额
        
        Args:
            amount: 提取金额
            
        Returns:
            是否可以提取
        """
        return self.is_active and self.available_balance >= amount
    
    def freeze_amount(self, amount: float) -> bool:
        """冻结指定金额
        
        Args:
            amount: 冻结金额
            
        Returns:
            是否成功冻结
        """
        if self.available_balance >= amount:
            self.available_balance -= amount
            self.frozen_balance += amount
            return True
        return False
    
    def unfreeze_amount(self, amount: float) -> bool:
        """解冻指定金额
        
        Args:
            amount: 解冻金额
            
        Returns:
            是否成功解冻
        """
        if self.frozen_balance >= amount:
            self.frozen_balance -= amount
            self.available_balance += amount
            return True
        return False
    
    @classmethod
    def get_user_accounts(cls, session, user_id: int):
        """获取用户的所有账户
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            
        Returns:
            账户列表
        """
        return session.query(cls).filter_by(user_id=user_id, is_active=True).all()
    
    @classmethod
    def get_default_account(cls, session, user_id: int):
        """获取用户的默认账户
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            
        Returns:
            默认账户
        """
        return session.query(cls).filter_by(
            user_id=user_id, 
            is_default=True, 
            is_active=True
        ).first()