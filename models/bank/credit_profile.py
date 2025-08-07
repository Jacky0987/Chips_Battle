from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer, JSON, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum

from models.base import BaseModel


class CreditRating(Enum):
    """信用等级枚举"""
    EXCELLENT = "excellent"  # 优秀 (750+)
    VERY_GOOD = "very_good"  # 很好 (700-749)
    GOOD = "good"  # 良好 (650-699)
    FAIR = "fair"  # 一般 (600-649)
    POOR = "poor"  # 较差 (550-599)
    VERY_POOR = "very_poor"  # 很差 (<550)


class CreditProfile(BaseModel):
    """信用档案模型"""
    __tablename__ = 'credit_profiles'
    
    # 基本信息
    profile_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, unique=True)
    
    # 信用分数
    credit_score = Column(Integer, default=600)  # 信用分数 (300-850)
    credit_rating = Column(String(20), default=CreditRating.FAIR.value)  # 信用等级
    
    # 信用历史
    credit_history_length = Column(Integer, default=0)  # 信用历史长度(月)
    oldest_account_date = Column(DateTime)  # 最早账户开立日期
    
    # 账户信息
    total_accounts = Column(Integer, default=0)  # 总账户数
    open_accounts = Column(Integer, default=0)  # 开放账户数
    closed_accounts = Column(Integer, default=0)  # 关闭账户数
    
    # 贷款信息
    total_loans = Column(Integer, default=0)  # 总贷款数
    active_loans = Column(Integer, default=0)  # 活跃贷款数
    completed_loans = Column(Integer, default=0)  # 已完成贷款数
    defaulted_loans = Column(Integer, default=0)  # 违约贷款数
    
    # 债务信息
    total_debt = Column(Numeric(20, 8), default=0)  # 总债务
    available_credit = Column(Numeric(20, 8), default=0)  # 可用信用额度
    credit_utilization = Column(Numeric(5, 4), default=0)  # 信用利用率
    
    # 还款历史
    on_time_payments = Column(Integer, default=0)  # 按时还款次数
    late_payments = Column(Integer, default=0)  # 逾期还款次数
    missed_payments = Column(Integer, default=0)  # 错过还款次数
    
    # 查询记录
    hard_inquiries = Column(Integer, default=0)  # 硬查询次数
    soft_inquiries = Column(Integer, default=0)  # 软查询次数
    last_inquiry_date = Column(DateTime)  # 最后查询日期
    
    # 负面记录
    bankruptcies = Column(Integer, default=0)  # 破产次数
    foreclosures = Column(Integer, default=0)  # 止赎次数
    collections = Column(Integer, default=0)  # 催收次数
    
    # 收入信息
    annual_income = Column(Numeric(20, 8))  # 年收入
    employment_length = Column(Integer)  # 就业时长(月)
    debt_to_income_ratio = Column(Numeric(5, 4))  # 债务收入比
    
    # 资产信息
    total_assets = Column(Numeric(20, 8), default=0)  # 总资产
    liquid_assets = Column(Numeric(20, 8), default=0)  # 流动资产
    
    # 评分因子权重
    payment_history_score = Column(Integer, default=0)  # 还款历史评分 (35%)
    credit_utilization_score = Column(Integer, default=0)  # 信用利用率评分 (30%)
    credit_history_score = Column(Integer, default=0)  # 信用历史评分 (15%)
    credit_mix_score = Column(Integer, default=0)  # 信用组合评分 (10%)
    new_credit_score = Column(Integer, default=0)  # 新信用评分 (10%)
    
    # 时间信息
    last_updated = Column(DateTime, default=datetime.utcnow)
    next_review_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 额外数据
    risk_factors = Column(JSON)  # 风险因素
    improvement_suggestions = Column(JSON)  # 改进建议
    notes = Column(Text)  # 备注
    
    # 关系
    user = relationship("User", back_populates="credit_profile")
    
    def __init__(self, user_id: str, **kwargs):
        import uuid
        
        self.profile_id = str(uuid.uuid4())
        self.user_id = user_id
        
        # Initialize fields with defaults
        self.credit_score = 600
        self.credit_rating = CreditRating.FAIR.value
        self.credit_history_length = 0
        self.oldest_account_date = None
        self.total_accounts = 0
        self.open_accounts = 0
        self.closed_accounts = 0
        self.total_loans = 0
        self.active_loans = 0
        self.completed_loans = 0
        self.defaulted_loans = 0
        self.total_debt = Decimal('0')
        self.available_credit = Decimal('0')
        self.credit_utilization = Decimal('0')
        self.on_time_payments = 0
        self.late_payments = 0
        self.missed_payments = 0
        self.hard_inquiries = 0
        self.soft_inquiries = 0
        self.last_inquiry_date = None
        self.bankruptcies = 0
        self.foreclosures = 0
        self.collections = 0
        self.annual_income = None
        self.employment_length = None
        self.debt_to_income_ratio = None
        self.total_assets = Decimal('0')
        self.liquid_assets = Decimal('0')
        self.payment_history_score = 0
        self.credit_utilization_score = 0
        self.credit_history_score = 0
        self.credit_mix_score = 0
        self.new_credit_score = 0
        self.risk_factors = None
        self.improvement_suggestions = None
        self.notes = None

        self.next_review_date = datetime.utcnow() + timedelta(days=30)
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 初始化信用评分
        self._calculate_credit_score()
    
    def _calculate_credit_score(self) -> int:
        """计算信用分数
        
        Returns:
            计算后的信用分数
        """
        # 基础分数
        base_score = 300
        
        # 1. 还款历史 (35%权重)
        payment_score = self._calculate_payment_history_score()
        self.payment_history_score = payment_score
        
        # 2. 信用利用率 (30%权重)
        utilization_score = self._calculate_utilization_score()
        self.credit_utilization_score = utilization_score
        
        # 3. 信用历史长度 (15%权重)
        history_score = self._calculate_history_score()
        self.credit_history_score = history_score
        
        # 4. 信用组合 (10%权重)
        mix_score = self._calculate_credit_mix_score()
        self.credit_mix_score = mix_score
        
        # 5. 新信用查询 (10%权重)
        inquiry_score = self._calculate_new_credit_score()
        self.new_credit_score = inquiry_score
        
        # 计算总分
        total_score = (
            payment_score * 0.35 +
            utilization_score * 0.30 +
            history_score * 0.15 +
            mix_score * 0.10 +
            inquiry_score * 0.10
        )
        
        # 负面记录扣分
        penalty = (
            self.bankruptcies * 100 +
            self.foreclosures * 80 +
            self.collections * 50 +
            self.defaulted_loans * 60
        )
        
        final_score = int(base_score + total_score - penalty)
        
        # 确保分数在合理范围内
        self.credit_score = max(300, min(850, final_score))
        
        # 更新信用等级
        self._update_credit_rating()
        
        return self.credit_score
    
    def _calculate_payment_history_score(self) -> int:
        """计算还款历史评分"""
        total_payments = self.on_time_payments + self.late_payments + self.missed_payments
        
        if total_payments == 0:
            return 100  # 新用户给予中等分数
        
        on_time_ratio = self.on_time_payments / total_payments
        late_penalty = (self.late_payments / total_payments) * 50
        missed_penalty = (self.missed_payments / total_payments) * 100
        
        score = (on_time_ratio * 200) - late_penalty - missed_penalty
        return max(0, min(200, int(score)))
    
    def _calculate_utilization_score(self) -> int:
        """计算信用利用率评分"""
        if self.available_credit <= 0:
            return 100  # 无信用额度时给予中等分数
        
        utilization = float(self.credit_utilization or 0)
        
        if utilization <= 0.1:  # 10%以下
            return 180
        elif utilization <= 0.3:  # 30%以下
            return 150
        elif utilization <= 0.5:  # 50%以下
            return 120
        elif utilization <= 0.7:  # 70%以下
            return 80
        else:  # 70%以上
            return 40
    
    def _calculate_history_score(self) -> int:
        """计算信用历史评分"""
        if self.credit_history_length <= 0:
            return 50  # 新用户
        
        # 信用历史越长分数越高
        if self.credit_history_length >= 120:  # 10年以上
            return 120
        elif self.credit_history_length >= 60:  # 5年以上
            return 100
        elif self.credit_history_length >= 24:  # 2年以上
            return 80
        elif self.credit_history_length >= 12:  # 1年以上
            return 60
        else:
            return 40
    
    def _calculate_credit_mix_score(self) -> int:
        """计算信用组合评分"""
        # 多样化的信用类型得分更高
        mix_score = 0
        
        if self.total_accounts > 0:
            mix_score += 30
        
        if self.total_loans > 0:
            mix_score += 30
        
        if self.total_accounts >= 3:
            mix_score += 20
        
        if self.completed_loans > 0:
            mix_score += 20
        
        return min(100, mix_score)
    
    def _calculate_new_credit_score(self) -> int:
        """计算新信用查询评分"""
        # 最近的硬查询会降低分数
        recent_inquiries = 0
        
        if self.last_inquiry_date:
            days_since_inquiry = (datetime.utcnow() - self.last_inquiry_date).days
            if days_since_inquiry <= 30:
                recent_inquiries = self.hard_inquiries
        
        penalty = recent_inquiries * 10
        score = 100 - penalty
        
        return max(0, score)
    
    def _update_credit_rating(self):
        """更新信用等级"""
        if self.credit_score >= 750:
            self.credit_rating = CreditRating.EXCELLENT.value
        elif self.credit_score >= 700:
            self.credit_rating = CreditRating.VERY_GOOD.value
        elif self.credit_score >= 650:
            self.credit_rating = CreditRating.GOOD.value
        elif self.credit_score >= 600:
            self.credit_rating = CreditRating.FAIR.value
        elif self.credit_score >= 550:
            self.credit_rating = CreditRating.POOR.value
        else:
            self.credit_rating = CreditRating.VERY_POOR.value
    
    def update_payment_history(self, on_time: bool, amount: Decimal = None):
        """更新还款历史
        
        Args:
            on_time: 是否按时还款
            amount: 还款金额
        """
        if on_time:
            self.on_time_payments += 1
        else:
            self.late_payments += 1
        
        self._calculate_credit_score()
        self.last_updated = datetime.utcnow()
    
    def add_missed_payment(self):
        """添加错过还款记录"""
        self.missed_payments += 1
        self._calculate_credit_score()
        self.last_updated = datetime.utcnow()
    
    def update_debt_info(self, total_debt: Decimal, available_credit: Decimal):
        """更新债务信息
        
        Args:
            total_debt: 总债务
            available_credit: 可用信用额度
        """
        self.total_debt = total_debt
        self.available_credit = available_credit
        
        if available_credit > 0:
            self.credit_utilization = total_debt / available_credit
        else:
            self.credit_utilization = Decimal('0')
        
        self._calculate_credit_score()
        self.last_updated = datetime.utcnow()
    
    def add_hard_inquiry(self, reason: str = None):
        """添加硬查询记录
        
        Args:
            reason: 查询原因
        """
        self.hard_inquiries += 1
        self.last_inquiry_date = datetime.utcnow()
        self._calculate_credit_score()
        self.last_updated = datetime.utcnow()
    
    def add_soft_inquiry(self, reason: str = None):
        """添加软查询记录
        
        Args:
            reason: 查询原因
        """
        self.soft_inquiries += 1
        # 软查询不影响信用分数
        self.last_updated = datetime.utcnow()
    
    def update_account_info(self, total_accounts: int, open_accounts: int):
        """更新账户信息
        
        Args:
            total_accounts: 总账户数
            open_accounts: 开放账户数
        """
        self.total_accounts = total_accounts
        self.open_accounts = open_accounts
        self.closed_accounts = total_accounts - open_accounts
        
        self._calculate_credit_score()
        self.last_updated = datetime.utcnow()
    
    def update_loan_info(self, total_loans: int, active_loans: int, 
                        completed_loans: int, defaulted_loans: int):
        """更新贷款信息
        
        Args:
            total_loans: 总贷款数
            active_loans: 活跃贷款数
            completed_loans: 已完成贷款数
            defaulted_loans: 违约贷款数
        """
        self.total_loans = total_loans
        self.active_loans = active_loans
        self.completed_loans = completed_loans
        self.defaulted_loans = defaulted_loans
        
        self._calculate_credit_score()
        self.last_updated = datetime.utcnow()
    
    def get_credit_limit_recommendation(self, loan_amount: Decimal) -> dict:
        """获取信贷额度建议
        
        Args:
            loan_amount: 申请贷款金额
            
        Returns:
            建议信息
        """
        # 基于信用分数的基础额度
        if self.credit_score >= 750:
            base_multiplier = 10
            risk_level = "低风险"
        elif self.credit_score >= 700:
            base_multiplier = 8
            risk_level = "较低风险"
        elif self.credit_score >= 650:
            base_multiplier = 6
            risk_level = "中等风险"
        elif self.credit_score >= 600:
            base_multiplier = 4
            risk_level = "较高风险"
        else:
            base_multiplier = 2
            risk_level = "高风险"
        
        # 基于收入的额度计算
        if self.annual_income:
            income_based_limit = self.annual_income * base_multiplier
        else:
            income_based_limit = Decimal('50000')  # 默认额度
        
        # 考虑现有债务
        if self.debt_to_income_ratio and self.debt_to_income_ratio > Decimal('0.4'):
            income_based_limit *= Decimal('0.7')  # 债务比过高时降低额度
        
        recommended_limit = min(income_based_limit, loan_amount * Decimal('1.2'))
        
        return {
            'recommended_limit': float(recommended_limit),
            'risk_level': risk_level,
            'approval_probability': self._calculate_approval_probability(),
            'suggested_interest_rate': self._suggest_interest_rate(),
            'conditions': self._get_loan_conditions()
        }
    
    def _calculate_approval_probability(self) -> float:
        """计算贷款批准概率"""
        if self.credit_score >= 750:
            return 0.95
        elif self.credit_score >= 700:
            return 0.85
        elif self.credit_score >= 650:
            return 0.70
        elif self.credit_score >= 600:
            return 0.50
        elif self.credit_score >= 550:
            return 0.30
        else:
            return 0.10
    
    def _suggest_interest_rate(self) -> float:
        """建议利率"""
        base_rate = 0.05  # 基准利率5%
        
        if self.credit_score >= 750:
            return base_rate + 0.01  # 6%
        elif self.credit_score >= 700:
            return base_rate + 0.02  # 7%
        elif self.credit_score >= 650:
            return base_rate + 0.04  # 9%
        elif self.credit_score >= 600:
            return base_rate + 0.06  # 11%
        elif self.credit_score >= 550:
            return base_rate + 0.08  # 13%
        else:
            return base_rate + 0.12  # 17%
    
    def _get_loan_conditions(self) -> List[str]:
        """获取贷款条件"""
        conditions = []
        
        if self.credit_score < 650:
            conditions.append("需要提供担保人")
        
        if self.credit_score < 600:
            conditions.append("需要抵押品")
            conditions.append("贷款期限不超过3年")
        
        if self.debt_to_income_ratio and self.debt_to_income_ratio > Decimal('0.4'):
            conditions.append("需要降低现有债务")
        
        if self.defaulted_loans > 0:
            conditions.append("需要清偿违约贷款")
        
        return conditions
    
    def get_improvement_suggestions(self) -> List[str]:
        """获取信用改进建议"""
        suggestions = []
        
        if self.credit_utilization > Decimal('0.3'):
            suggestions.append("降低信用卡使用率至30%以下")
        
        if self.late_payments > 0:
            suggestions.append("保持按时还款记录")
        
        if self.credit_history_length < 24:
            suggestions.append("保持账户开放以延长信用历史")
        
        if self.total_accounts < 3:
            suggestions.append("适当增加信用账户类型")
        
        if self.hard_inquiries > 5:
            suggestions.append("减少信用查询申请")
        
        return suggestions
    
    def get_profile_summary(self) -> dict:
        """获取信用档案摘要
        
        Returns:
            信用档案摘要
        """
        return {
            'profile_id': self.profile_id,
            'user_id': self.user_id,
            'credit_score': self.credit_score,
            'credit_rating': self.credit_rating,
            'credit_history_length': self.credit_history_length,
            'total_accounts': self.total_accounts,
            'active_loans': self.active_loans,
            'total_debt': float(self.total_debt),
            'credit_utilization': float(self.credit_utilization * 100) if self.credit_utilization else 0,
            'on_time_payment_rate': (self.on_time_payments / max(1, self.on_time_payments + self.late_payments + self.missed_payments)) * 100,
            'risk_level': self._get_risk_level(),
            'last_updated': self.last_updated.strftime('%Y-%m-%d'),
            'improvement_suggestions': self.get_improvement_suggestions()
        }
    
    def _get_risk_level(self) -> str:
        """获取风险等级"""
        if self.credit_score >= 750:
            return "低风险"
        elif self.credit_score >= 650:
            return "中等风险"
        elif self.credit_score >= 550:
            return "较高风险"
        else:
            return "高风险"
    
    @classmethod
    async def get_or_create_profile(cls, session: AsyncSession, user_id: str) -> 'CreditProfile':
        """获取或创建信用档案
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            
        Returns:
            信用档案
        """
        try:
            stmt = select(cls).where(cls.user_id == user_id)
            result = await session.execute(stmt)
            profile = result.scalars().first()
            
            if not profile:
                profile = cls(user_id=user_id)
                session.add(profile)
            
            return profile
        except Exception as e:
            print(f"Error in get_or_create_profile: {e}")
            profile = cls(user_id=user_id)
            session.add(profile)
            return profile
    
    def __repr__(self):
        return f"<CreditProfile(profile_id='{self.profile_id}', score={self.credit_score}, rating='{self.credit_rating}')>"