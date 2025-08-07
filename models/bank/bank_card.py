from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import random
import string

from dal.database import Base


class BankCard(Base):
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
    
    # 关系
    user = relationship("User", back_populates="bank_cards")
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
    
    def get_display_info(self) -> dict:
        """获取显示信息"""
        bank_info = self.get_bank_info()
        
        return {
            'card_id': self.card_id,
            'bank_name': bank_info['name'],
            'bank_code': self.bank_code,
            'card_number': self.get_masked_card_number(),
            'card_type': self.card_type,
            'status': 'active' if self.can_use() else 'inactive',
            'expiry_date': self.expiry_date.strftime('%m/%y'),
            'issued_date': self.issued_date.strftime('%Y-%m-%d')
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
        return f"<BankCard(card_id='{self.card_id}', bank='{self.bank_code}', number='{self.get_masked_card_number()}')>"