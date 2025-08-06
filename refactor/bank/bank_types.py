from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
import random

class BankCategory(Enum):
    """银行业务类别"""
    COMMERCIAL = "commercial"  # 商业银行
    INVESTMENT = "investment"  # 投资银行
    CENTRAL = "central"       # 央行
    CRYPTO = "crypto"         # 加密货币银行
    TRADING = "trading"       # 交易银行
    WEALTH = "wealth"         # 财富管理银行

@dataclass
class BankType:
    """银行类型定义"""
    bank_id: str
    name: str
    category: BankCategory
    description: str
    logo: str
    base_loan_rate: float
    base_deposit_rate: float
    max_loan_multiplier: float
    specialties: List[str]
    unlock_level: int
    unlock_requirements: Dict
    
    def __post_init__(self):
        self.current_loan_rate = self.base_loan_rate
        self.current_deposit_rate = self.base_deposit_rate
        self.reputation = 0.0  # 银行声誉值
        self.trust_level = "普通"  # 信任等级

# 定义所有银行类型
BANK_TYPES = {
    "JC_CENTRAL": BankType(
        bank_id="JC_CENTRAL",
        name="JackyCoin 央行",
        category=BankCategory.CENTRAL,
        description="JackyCoin经济体系的中央银行，负责货币政策和金融稳定",
        logo="🏛️",
        base_loan_rate=0.025,
        base_deposit_rate=0.015,
        max_loan_multiplier=10.0,
        specialties=["货币政策", "金融监管", "紧急救助"],
        unlock_level=1,
        unlock_requirements={}
    ),
    
    "JC_COMMERCIAL": BankType(
        bank_id="JC_COMMERCIAL",
        name="JackyCoin 商业银行",
        category=BankCategory.COMMERCIAL,
        description="面向普通用户的综合性商业银行，提供基础金融服务",
        logo="🏦",
        base_loan_rate=0.06,
        base_deposit_rate=0.025,
        max_loan_multiplier=5.0,
        specialties=["个人贷款", "储蓄存款", "基础理财"],
        unlock_level=1,
        unlock_requirements={}
    ),
    
    "JC_INVESTMENT": BankType(
        bank_id="JC_INVESTMENT",
        name="JackyCoin 投资银行",
        category=BankCategory.INVESTMENT,
        description="专注于投资业务和资本市场的投资银行",
        logo="📈",
        base_loan_rate=0.04,
        base_deposit_rate=0.03,
        max_loan_multiplier=8.0,
        specialties=["IPO承销", "企业融资", "投资咨询"],
        unlock_level=5,
        unlock_requirements={"total_trades": 50, "portfolio_value": 200000}
    ),
    
    "JC_CRYPTO": BankType(
        bank_id="JC_CRYPTO",
        name="JackyCoin 数字银行",
        category=BankCategory.CRYPTO,
        description="专门处理数字货币和区块链相关业务的创新银行",
        logo="🪙",
        base_loan_rate=0.08,
        base_deposit_rate=0.04,
        max_loan_multiplier=3.0,
        specialties=["数字货币", "DeFi服务", "智能合约"],
        unlock_level=10,
        unlock_requirements={"crypto_trades": 20, "tech_achievements": 3}
    ),
    
    "JC_TRADING": BankType(
        bank_id="JC_TRADING",
        name="JackyCoin 交易银行",
        category=BankCategory.TRADING,
        description="专为活跃交易者提供服务的专业交易银行",
        logo="⚡",
        base_loan_rate=0.05,
        base_deposit_rate=0.02,
        max_loan_multiplier=15.0,
        specialties=["保证金交易", "高频交易", "衍生品"],
        unlock_level=8,
        unlock_requirements={"daily_trades": 10, "profit_rate": 0.15}
    ),
    
    "JC_WEALTH": BankType(
        bank_id="JC_WEALTH",
        name="JackyCoin 私人银行",
        category=BankCategory.WEALTH,
        description="为高净值客户提供专属财富管理服务的私人银行",
        logo="💎",
        base_loan_rate=0.03,
        base_deposit_rate=0.05,
        max_loan_multiplier=20.0,
        specialties=["财富管理", "私人定制", "家族信托"],
        unlock_level=15,
        unlock_requirements={"net_worth": 1000000, "vip_status": True}
    )
}

class BankRelationship:
    """银行关系管理"""
    
    def __init__(self, bank_id, user_data):
        self.bank_id = bank_id
        self.bank = BANK_TYPES[bank_id]
        self.relationship_level = 1  # 关系等级 1-10
        self.trust_score = 50.0      # 信任度 0-100
        self.total_business = 0.0    # 累计业务量
        self.last_interaction = None
        self.special_privileges = []
        
    def update_relationship(self, business_amount, interaction_type):
        """更新银行关系"""
        self.total_business += business_amount
        
        # 根据业务类型调整信任度
        trust_changes = {
            'loan_repaid_on_time': +5,
            'loan_defaulted': -15,
            'large_deposit': +3,
            'frequent_trading': +2,
            'task_completed': +4,
            'referral': +6
        }
        
        trust_change = trust_changes.get(interaction_type, 0)
        self.trust_score = max(0, min(100, self.trust_score + trust_change))
        
        # 根据累计业务量和信任度更新关系等级
        new_level = min(10, 1 + int(self.total_business / 50000) + int(self.trust_score / 20))
        if new_level > self.relationship_level:
            self.relationship_level = new_level
            return True  # 关系等级提升
        return False
        
    def get_rate_discount(self):
        """获取利率折扣"""
        # 关系等级越高，折扣越多
        return (self.relationship_level - 1) * 0.002  # 每级0.2%折扣
        
    def get_loan_limit_bonus(self):
        """获取贷款额度加成"""
        return 1.0 + (self.relationship_level - 1) * 0.1  # 每级10%加成
        
    def can_access_special_services(self):
        """是否可以访问特殊服务"""
        return self.relationship_level >= 5 and self.trust_score >= 70
        
    def get_status_display(self):
        """获取状态显示"""
        level_names = {
            1: "新客户", 2: "普通客户", 3: "优质客户", 4: "重要客户", 5: "VIP客户",
            6: "白金客户", 7: "钻石客户", 8: "黑卡客户", 9: "私人客户", 10: "尊享客户"
        }
        
        trust_levels = {
            (0, 20): "信任度低", (20, 40): "信任度一般", (40, 60): "信任度良好",
            (60, 80): "信任度优秀", (80, 100): "信任度卓越"
        }
        
        trust_level = next(level for (low, high), level in trust_levels.items() 
                          if low <= self.trust_score < high)
        
        return {
            'level_name': level_names[self.relationship_level],
            'level': self.relationship_level,
            'trust_score': self.trust_score,
            'trust_level': trust_level,
            'total_business': self.total_business,
            'rate_discount': self.get_rate_discount(),
            'loan_bonus': self.get_loan_limit_bonus()
        } 