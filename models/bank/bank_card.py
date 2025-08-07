from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string

from models.base import BaseModel
from models.finance.currency import Currency


class BankCard(BaseModel):
    """银行卡模型"""
    __tablename__ = 'bank_cards'
    
    # 基本信息
    card_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    bank_code = Column(String(10), nullable=False)  # 银行代码 (ICBJC, JCCB, etc.)
    card_number = Column(String(19), unique=True, nullable=False)  # 卡号
    card_type = Column(String(20), default='debit')  # 卡类型: debit, credit
    
    # 卡片状态
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # 安全信息
    pin_hash = Column(String(128))  # PIN码哈希
    cvv = Column(String(3))  # CVV码
    
    # 时间信息
    issued_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 额外信息
    description = Column(Text)
    
    # 账户信息（整合后的默认账户字段）
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False, default=1)
    account_name = Column(String(100), default='默认账户')
    account_type = Column(String(20), default='savings')  # savings, checking, investment
    account_number = Column(String(20), unique=True, nullable=False)
    
    # 余额信息
    balance = Column(Numeric(20, 8), default=0)  # 总余额
    available_balance = Column(Numeric(20, 8), default=0)  # 可用余额
    frozen_balance = Column(Numeric(20, 8), default=0)  # 冻结余额
    
    # 账户状态
    is_default = Column(Boolean, default=True)
    
    # 限额设置
    daily_transfer_limit = Column(Numeric(20, 8), default=100000)  # 日转账限额
    monthly_transfer_limit = Column(Numeric(20, 8), default=1000000)  # 月转账限额
    
    # 利率信息
    interest_rate = Column(Numeric(8, 6), default=0.015)  # 年利率
    last_interest_date = Column(DateTime, default=datetime.utcnow)  # 上次计息日期
    
    # 关系
    user = relationship("User", back_populates="bank_cards")
    currency = relationship("Currency")
    accounts = relationship("BankAccount", back_populates="card", cascade="all, delete-orphan")
    
    # 银行信息映射
    BANK_INFO = {
        'ICBJC': {
            'name': '杰克币工商银行',
            'full_name': 'Industrial and Commercial Bank of JC',
            'focus': '企业金融',
            'description': '为大型企业和工业项目提供贷款'
        },
        'JCCB': {
            'name': '杰克币建设银行',
            'full_name': 'JC Construction Bank',
            'focus': '基础设施与房地产',
            'description': '建筑和地产开发贷款的首选'
        },
        'ABJC': {
            'name': '杰克币农业银行',
            'full_name': 'Agricultural Bank of JC',
            'focus': '农业与商品',
            'description': '在农产品、矿产等大宗商品领域有优势'
        },
        'BJC': {
            'name': '杰克币银行',
            'full_name': 'Bank of JackyCoin',
            'focus': '国际业务与外汇',
            'description': '处理全球贸易和货币兑换的最佳选择'
        },
        'BCOJC': {
            'name': '杰克币交通银行',
            'full_name': 'Bank of Communications JC',
            'focus': '交通物流与贸易',
            'description': '专注于运输、物流和供应链融资'
        },
        'PSBJC': {
            'name': '杰克币邮政储蓄银行',
            'full_name': 'Postal Savings Bank of JC',
            'focus': '零售与个人业务',
            'description': '网点最广，面向个人和小微企业，是初期的主要银行'
        },
        'PBJC': {
            'name': '杰克币人民银行',
            'full_name': 'People\'s Bank of JackyCoin',
            'focus': '中央银行',
            'description': '货币政策制定者和金融监管机构'
        }
    }
    
    def __init__(self, user_id: str, bank_code: str, card_type: str = 'debit', **kwargs):
        import uuid
        import hashlib
        
        self.card_id = str(uuid.uuid4())
        self.user_id = user_id
        self.bank_code = bank_code.upper()
        self.card_type = card_type
        
        # 生成卡号
        self.card_number = self._generate_card_number()
        
        # 生成CVV
        self.cvv = f"{random.randint(100, 999):03d}"
        
        # 设置过期日期 (5年后)
        self.expiry_date = datetime.utcnow() + timedelta(days=365*5)
        
        # 生成账户号码
        self.account_number = self._generate_account_number()
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_card_number(self) -> str:
        """生成银行卡号"""
        # 银行标识码映射
        bank_prefixes = {
            'ICBJC': '6222',
            'JCCB': '6227',
            'ABJC': '6228',
            'BJC': '6225',
            'BCOJC': '6226',
            'PSBJC': '6221',
            'PBJC': '6220'
        }
        
        prefix = bank_prefixes.get(self.bank_code, '6200')
        
        # 生成12位随机数字
        middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        
        # 组合前15位
        partial_number = prefix + middle_digits
        
        # 使用Luhn算法计算校验位
        check_digit = self._calculate_luhn_check_digit(partial_number)
        
        return partial_number + str(check_digit)
    
    def _calculate_luhn_check_digit(self, number: str) -> int:
        """计算Luhn算法校验位"""
        digits = [int(d) for d in number]
        
        # 从右到左，每隔一位数字乘以2
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] = digits[i] // 10 + digits[i] % 10
        
        total = sum(digits)
        return (10 - (total % 10)) % 10
    
    def set_pin(self, pin: str) -> bool:
        """设置PIN码"""
        if len(pin) != 6 or not pin.isdigit():
            return False
        
        import hashlib
        self.pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return True
    
    def verify_pin(self, pin: str) -> bool:
        """验证PIN码"""
        if not self.pin_hash:
            return False
        
        import hashlib
        return self.pin_hash == hashlib.sha256(pin.encode()).hexdigest()
    
    def get_bank_info(self) -> dict:
        """获取银行信息"""
        return self.BANK_INFO.get(self.bank_code, {
            'name': '未知银行',
            'full_name': 'Unknown Bank',
            'focus': '未知',
            'description': '未知银行'
        })
    
    def get_masked_card_number(self) -> str:
        """获取掩码卡号"""
        if len(self.card_number) >= 4:
            return '*' * (len(self.card_number) - 4) + self.card_number[-4:]
        return self.card_number
    
    def is_expired(self) -> bool:
        """检查卡片是否过期"""
        return datetime.utcnow() > self.expiry_date
    
    def can_use(self) -> bool:
        """检查卡片是否可用"""
        return self.is_active and not self.is_locked and not self.is_expired()
    
    def lock_card(self, reason: str = None):
        """锁定卡片"""
        self.is_locked = True
        self.updated_at = datetime.utcnow()
    
    def unlock_card(self):
        """解锁卡片"""
        self.is_locked = False
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """停用卡片"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
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
        """检查是否可以提取指定金额"""
        if not self.is_active:
            return False
        return self.get_available_balance() >= amount
    
    def deposit(self, amount: Decimal, description: str = None) -> bool:
        """存款"""
        if amount <= 0:
            return False
        
        self.balance = (self.balance or 0) + amount
        self.available_balance = (self.available_balance or 0) + amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def withdraw(self, amount: Decimal, description: str = None) -> bool:
        """取款"""
        if not self.can_withdraw(amount):
            return False
        
        self.balance = (self.balance or 0) - amount
        self.available_balance = (self.available_balance or 0) - amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def freeze_amount(self, amount: Decimal, reason: str = None) -> bool:
        """冻结金额"""
        if self.get_available_balance() < amount:
            return False
        
        self.available_balance = (self.available_balance or 0) - amount
        self.frozen_balance = (self.frozen_balance or 0) + amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def unfreeze_amount(self, amount: Decimal, reason: str = None) -> bool:
        """解冻金额"""
        if self.get_frozen_balance() < amount:
            return False
        
        self.frozen_balance = (self.frozen_balance or 0) - amount
        self.available_balance = (self.available_balance or 0) + amount
        self.updated_at = datetime.utcnow()
        
        return True
    
    def calculate_interest(self) -> Decimal:
        """计算利息"""
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
        """应用利息"""
        interest = self.calculate_interest()
        
        if interest > 0:
            self.deposit(interest, "利息收入")
            self.last_interest_date = datetime.utcnow()
        
        return interest
    
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
    
    def get_display_info(self) -> dict:
        """获取显示信息"""
        bank_info = self.get_bank_info()
        
        return {
            'card_id': self.card_id,
            'bank_name': bank_info['name'],
            'bank_code': self.bank_code,
            'card_number': self.card_number,
            'card_type': self.card_type,
            'status': 'active' if self.can_use() else 'inactive',
            'is_active': self.is_active,
            'expiry_date': self.expiry_date.strftime('%m/%y'),
            'issued_date': self.issued_date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d'),
            'account_number': self.account_number,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'currency_code': self.currency.code if self.currency else 'JCY',
            'balance': float(self.get_total_balance()),
            'available_balance': float(self.get_available_balance()),
            'frozen_balance': float(self.get_frozen_balance()),
            'is_default': self.is_default,
            'interest_rate': float(self.interest_rate or 0)
        }
    
    @classmethod
    def get_available_banks(cls) -> list:
        """获取可用银行列表"""
        return [
            {
                'code': code,
                'name': info['name'],
                'full_name': info['full_name'],
                'focus': info['focus'],
                'description': info['description']
            }
            for code, info in cls.BANK_INFO.items()
            if code != 'PBJC'  # 中央银行不对个人开放
        ]
    
    def __repr__(self):
        return f"<BankCard(card_id='{self.card_id}', bank='{self.bank_code}', number='{self.card_number}')>"