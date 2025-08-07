from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional

from models.base import BaseModel


class BankAccount(BaseModel):
    """银行账户模型"""
    __tablename__ = 'bank_accounts'
    
    # 基本信息
    account_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    card_id = Column(String(36), ForeignKey('bank_cards.card_id'), nullable=False)
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    
    # 账户信息
    account_number = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(20), default='savings')  # savings, checking, investment
    
    # 余额信息
    balance = Column(Numeric(20, 8), default=0)  # 总余额
    available_balance = Column(Numeric(20, 8), default=0)  # 可用余额
    frozen_balance = Column(Numeric(20, 8), default=0)  # 冻结余额
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # 限额设置
    daily_transfer_limit = Column(Numeric(20, 8), default=100000)  # 日转账限额
    monthly_transfer_limit = Column(Numeric(20, 8), default=1000000)  # 月转账限额
    
    # 利率信息
    interest_rate = Column(Numeric(8, 6), default=0.015)  # 年利率
    last_interest_date = Column(DateTime, default=datetime.utcnow)  # 上次计息日期
    
    # 时间信息
    opened_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 额外信息
    description = Column(Text)
    
    # 关系
    user = relationship("User", back_populates="bank_accounts")
    card = relationship("BankCard", back_populates="accounts")
    currency = relationship("Currency")
    
    def __init__(self, user_id: str, card_id: str, currency_id: str, 
                 account_name: str, account_type: str = 'savings', **kwargs):
        import uuid
        
        self.account_id = str(uuid.uuid4())
        self.user_id = user_id
        self.card_id = card_id
        self.currency_id = currency_id
        self.account_name = account_name
        self.account_type = account_type
        
        # 生成账户号码
        self.account_number = self._generate_account_number()
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_account_number(self) -> str:
        """生成账户号码"""
        import random
        
        # 账户类型前缀
        type_prefixes = {
            'savings': '01',
            'checking': '02',
            'investment': '03'
        }
        
        prefix = type_prefixes.get(self.account_type, '01')
        
        # 生成16位随机数字
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        
        return prefix + random_digits
    
    def get_total_balance(self) -> Decimal:
        """获取总余额"""
        return Decimal(str(self.balance or 0))
    
    def get_available_balance(self) -> Decimal:
        """获取可用余额"""
        return Decimal(str(self.available_balance or 0))
    
    def get_frozen_balance(self) -> Decimal:
        """获取冻结余额"""
        return Decimal(str(self.frozen_balance or 0))
    
    def can_withdraw(self, amount: Decimal) -> bool:
        """检查是否可以提取指定金额
        
        Args:
            amount: 提取金额
            
        Returns:
            是否可以提取
        """
        if not self.is_active:
            return False
        
        return self.get_available_balance() >= amount
    
    def deposit(self, amount: Decimal, description: str = None) -> bool:
        """存款
        
        Args:
            amount: 存款金额
            description: 描述
            
        Returns:
            是否成功
        """
        if amount <= 0:
            return False
        
        self.balance = (self.balance or 0) + amount
        self.available_balance = (self.available_balance or 0) + amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def withdraw(self, amount: Decimal, description: str = None) -> bool:
        """取款
        
        Args:
            amount: 取款金额
            description: 描述
            
        Returns:
            是否成功
        """
        if not self.can_withdraw(amount):
            return False
        
        self.balance = (self.balance or 0) - amount
        self.available_balance = (self.available_balance or 0) - amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def freeze_amount(self, amount: Decimal, reason: str = None) -> bool:
        """冻结金额
        
        Args:
            amount: 冻结金额
            reason: 冻结原因
            
        Returns:
            是否成功
        """
        if self.get_available_balance() < amount:
            return False
        
        self.available_balance = (self.available_balance or 0) - amount
        self.frozen_balance = (self.frozen_balance or 0) + amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def unfreeze_amount(self, amount: Decimal, reason: str = None) -> bool:
        """解冻金额
        
        Args:
            amount: 解冻金额
            reason: 解冻原因
            
        Returns:
            是否成功
        """
        if self.get_frozen_balance() < amount:
            return False
        
        self.frozen_balance = (self.frozen_balance or 0) - amount
        self.available_balance = (self.available_balance or 0) + amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def calculate_interest(self) -> Decimal:
        """计算利息
        
        Returns:
            应得利息
        """
        if not self.last_interest_date:
            return Decimal('0')
        
        # 计算天数
        days = (datetime.utcnow() - self.last_interest_date).days
        if days <= 0:
            return Decimal('0')
        
        # 计算日利率
        daily_rate = Decimal(str(self.interest_rate or 0)) / 365
        
        # 计算利息
        interest = self.get_total_balance() * daily_rate * days
        
        return interest
    
    def apply_interest(self) -> Decimal:
        """应用利息
        
        Returns:
            实际获得的利息
        """
        interest = self.calculate_interest()
        
        if interest > 0:
            self.deposit(interest, "利息收入")
            self.last_interest_date = datetime.utcnow()
        
        return interest
    
    def set_as_default(self):
        """设置为默认账户"""
        self.is_default = True
        self.updated_at = datetime.utcnow()
    
    def unset_as_default(self):
        """取消默认账户"""
        self.is_default = False
        self.updated_at = datetime.utcnow()
    
    def close_account(self, reason: str = None):
        """关闭账户"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def get_account_summary(self) -> dict:
        """获取账户摘要
        
        Returns:
            账户摘要信息
        """
        return {
            'account_id': self.account_id,
            'account_number': self.account_number,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'currency_code': self.currency.code if self.currency else 'Unknown',
            'balance': float(self.get_total_balance()),
            'available_balance': float(self.get_available_balance()),
            'frozen_balance': float(self.get_frozen_balance()),
            'is_active': self.is_active,
            'is_default': self.is_default,
            'interest_rate': float(self.interest_rate or 0),
            'opened_date': self.opened_date.strftime('%Y-%m-%d'),
            'bank_name': self.card.get_bank_info()['name'] if self.card else 'Unknown'
        }
    
    @classmethod
    def get_user_accounts(cls, uow, user_id: str) -> list:
        """获取用户所有账户
        
        Args:
            uow: 工作单元
            user_id: 用户ID
            
        Returns:
            用户账户列表
        """
        try:
            return uow.query(cls).filter_by(
                user_id=user_id, is_active=True
            ).all()
        except Exception:
            return []
    
    @classmethod
    def get_user_default_account(cls, uow, user_id: str, currency_code: str = 'JCY') -> Optional['BankAccount']:
        """获取用户默认账户
        
        Args:
            uow: 工作单元
            user_id: 用户ID
            currency_code: 货币代码
            
        Returns:
            默认账户或None
        """
        try:
            # 先查找指定货币的默认账户
            account = uow.query(cls).join(cls.currency).filter(
                cls.user_id == user_id,
                cls.is_active == True,
                cls.is_default == True,
                cls.currency.has(code=currency_code)
            ).first()
            
            if account:
                return account
            
            # 如果没有默认账户，返回第一个指定货币的账户
            return uow.query(cls).join(cls.currency).filter(
                cls.user_id == user_id,
                cls.is_active == True,
                cls.currency.has(code=currency_code)
            ).first()
            
        except Exception:
            return None
    
    def __repr__(self):
        return f"<BankAccount(account_id='{self.account_id}', number='{self.account_number}', balance={self.balance})>"