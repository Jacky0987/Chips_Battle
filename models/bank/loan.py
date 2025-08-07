from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer, select
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from models.base import BaseModel


class LoanStatus(Enum):
    """贷款状态枚举"""
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已批准
    ACTIVE = "active"  # 活跃中
    COMPLETED = "completed"  # 已完成
    DEFAULTED = "defaulted"  # 违约
    CANCELLED = "cancelled"  # 已取消


class LoanType(Enum):
    """贷款类型枚举"""
    PERSONAL = "personal"  # 个人贷款
    BUSINESS = "business"  # 企业贷款
    MORTGAGE = "mortgage"  # 抵押贷款
    AUTO = "auto"  # 汽车贷款
    EDUCATION = "education"  # 教育贷款
    CREDIT_LINE = "credit_line"  # 信用额度


class Loan(BaseModel):
    """贷款模型"""
    __tablename__ = 'loans'
    
    # 基本信息
    loan_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    bank_code = Column(String(10), nullable=False)  # 放贷银行
    currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    
    # 贷款信息
    loan_number = Column(String(20), unique=True, nullable=False)
    loan_type = Column(String(20), nullable=False)  # LoanType
    loan_amount = Column(Numeric(20, 8), nullable=False)  # 贷款金额
    outstanding_balance = Column(Numeric(20, 8), nullable=False)  # 未还余额
    
    # 利率和期限
    interest_rate = Column(Numeric(8, 6), nullable=False)  # 年利率
    term_months = Column(Integer, nullable=False)  # 贷款期限(月)
    monthly_payment = Column(Numeric(20, 8), nullable=False)  # 月还款额
    
    # 状态信息
    status = Column(String(20), default=LoanStatus.PENDING.value)
    
    # 时间信息
    application_date = Column(DateTime, default=datetime.utcnow)
    approval_date = Column(DateTime)
    disbursement_date = Column(DateTime)  # 放款日期
    maturity_date = Column(DateTime)  # 到期日期
    last_payment_date = Column(DateTime)
    next_payment_date = Column(DateTime)
    
    # 还款信息
    total_paid = Column(Numeric(20, 8), default=0)  # 已还总额
    principal_paid = Column(Numeric(20, 8), default=0)  # 已还本金
    interest_paid = Column(Numeric(20, 8), default=0)  # 已还利息
    late_fees = Column(Numeric(20, 8), default=0)  # 滞纳金
    
    # 违约信息
    days_overdue = Column(Integer, default=0)  # 逾期天数
    default_date = Column(DateTime)  # 违约日期
    
    # 抵押信息
    collateral_type = Column(String(50))  # 抵押品类型
    collateral_value = Column(Numeric(20, 8))  # 抵押品价值
    collateral_description = Column(Text)  # 抵押品描述
    
    # 审批信息
    credit_score_at_approval = Column(Integer)  # 批准时信用分
    approval_notes = Column(Text)  # 审批备注
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 额外信息
    purpose = Column(Text)  # 贷款用途
    notes = Column(Text)  # 备注
    
    # 关系
    user = relationship("User", back_populates="loans")
    currency = relationship("Currency")
    payments = relationship("LoanPayment", back_populates="loan", cascade="all, delete-orphan")
    
    def __init__(self, user_id: str, bank_code: str, currency_id: str,
                 loan_type: str, loan_amount: Decimal, interest_rate: Decimal,
                 term_months: int, **kwargs):
        import uuid
        
        self.loan_id = str(uuid.uuid4())
        self.user_id = user_id
        self.bank_code = bank_code.upper()
        self.currency_id = currency_id
        self.loan_type = loan_type
        self.loan_amount = loan_amount
        self.outstanding_balance = loan_amount
        self.interest_rate = interest_rate
        self.term_months = term_months
        
        # 生成贷款编号
        self.loan_number = self._generate_loan_number()
        
        # 计算月还款额
        self.monthly_payment = self._calculate_monthly_payment()
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_loan_number(self) -> str:
        """生成贷款编号"""
        import random
        
        # 贷款类型前缀
        type_prefixes = {
            'personal': 'PL',
            'business': 'BL',
            'mortgage': 'ML',
            'auto': 'AL',
            'education': 'EL',
            'credit_line': 'CL'
        }
        
        prefix = type_prefixes.get(self.loan_type, 'LN')
        
        # 银行代码 + 类型前缀 + 12位随机数字
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        
        return f"{self.bank_code}{prefix}{random_digits}"
    
    def _calculate_monthly_payment(self) -> Decimal:
        """计算月还款额 (等额本息)"""
        if self.term_months <= 0 or self.interest_rate <= 0:
            return self.loan_amount / max(self.term_months, 1)
        
        # 月利率
        monthly_rate = self.interest_rate / 12
        
        # 等额本息公式
        # M = P * [r(1+r)^n] / [(1+r)^n - 1]
        # M: 月还款额, P: 本金, r: 月利率, n: 还款月数
        
        factor = (1 + monthly_rate) ** self.term_months
        monthly_payment = self.loan_amount * (monthly_rate * factor) / (factor - 1)
        
        return monthly_payment.quantize(Decimal('0.01'))
    
    def approve_loan(self, credit_score: int, notes: str = None) -> bool:
        """批准贷款
        
        Args:
            credit_score: 信用分数
            notes: 审批备注
            
        Returns:
            是否成功
        """
        if self.status != LoanStatus.PENDING.value:
            return False
        
        self.status = LoanStatus.APPROVED.value
        self.approval_date = datetime.utcnow()
        self.credit_score_at_approval = credit_score
        self.approval_notes = notes
        self.updated_at = datetime.utcnow()
        
        return True
    
    def disburse_loan(self) -> bool:
        """放款
        
        Returns:
            是否成功
        """
        if self.status != LoanStatus.APPROVED.value:
            return False
        
        self.status = LoanStatus.ACTIVE.value
        self.disbursement_date = datetime.utcnow()
        self.maturity_date = datetime.utcnow() + timedelta(days=30 * self.term_months)
        self.next_payment_date = datetime.utcnow() + timedelta(days=30)
        self.updated_at = datetime.utcnow()
        
        return True
    
    def make_payment(self, amount: Decimal, payment_date: datetime = None) -> dict:
        """还款
        
        Args:
            amount: 还款金额
            payment_date: 还款日期
            
        Returns:
            还款详情
        """
        if payment_date is None:
            payment_date = datetime.utcnow()
        
        if amount <= 0 or self.outstanding_balance <= 0:
            return {'success': False, 'message': '无效的还款金额'}
        
        # 计算利息和本金分配
        monthly_rate = self.interest_rate / 12
        interest_portion = self.outstanding_balance * monthly_rate
        principal_portion = min(amount - interest_portion, self.outstanding_balance)
        
        if principal_portion < 0:
            principal_portion = 0
            interest_portion = amount
        
        # 更新还款信息
        self.total_paid += amount
        self.principal_paid += principal_portion
        self.interest_paid += interest_portion
        self.outstanding_balance -= principal_portion
        self.last_payment_date = payment_date
        
        # 更新下次还款日期
        if self.next_payment_date:
            self.next_payment_date += timedelta(days=30)
        
        # 重置逾期状态
        self.days_overdue = 0
        
        # 检查是否还清
        if self.outstanding_balance <= Decimal('0.01'):
            self.outstanding_balance = Decimal('0')
            self.status = LoanStatus.COMPLETED.value
        
        self.updated_at = datetime.utcnow()
        
        return {
            'success': True,
            'amount': float(amount),
            'principal_portion': float(principal_portion),
            'interest_portion': float(interest_portion),
            'remaining_balance': float(self.outstanding_balance),
            'is_completed': self.status == LoanStatus.COMPLETED.value
        }
    
    def calculate_overdue_days(self) -> int:
        """计算逾期天数"""
        if not self.next_payment_date or self.status != LoanStatus.ACTIVE.value:
            return 0
        
        if datetime.utcnow() > self.next_payment_date:
            return (datetime.utcnow() - self.next_payment_date).days
        
        return 0
    
    def update_overdue_status(self):
        """更新逾期状态"""
        self.days_overdue = self.calculate_overdue_days()
        
        # 逾期90天以上视为违约
        if self.days_overdue >= 90 and self.status == LoanStatus.ACTIVE.value:
            self.status = LoanStatus.DEFAULTED.value
            self.default_date = datetime.utcnow()
        
        self.updated_at = datetime.utcnow()
    
    def calculate_late_fee(self) -> Decimal:
        """计算滞纳金"""
        if self.days_overdue <= 0:
            return Decimal('0')
        
        # 滞纳金 = 逾期天数 * 月还款额 * 0.05%
        daily_late_fee_rate = Decimal('0.0005')
        return self.monthly_payment * daily_late_fee_rate * self.days_overdue
    
    def get_payment_schedule(self) -> List[dict]:
        """获取还款计划
        
        Returns:
            还款计划列表
        """
        schedule = []
        remaining_balance = self.loan_amount
        monthly_rate = self.interest_rate / 12
        payment_date = self.disbursement_date or datetime.utcnow()
        
        for month in range(1, self.term_months + 1):
            payment_date += timedelta(days=30)
            
            interest_payment = remaining_balance * monthly_rate
            principal_payment = self.monthly_payment - interest_payment
            
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                total_payment = principal_payment + interest_payment
            else:
                total_payment = self.monthly_payment
            
            remaining_balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment_date': payment_date.strftime('%Y-%m-%d'),
                'total_payment': float(total_payment),
                'principal_payment': float(principal_payment),
                'interest_payment': float(interest_payment),
                'remaining_balance': float(remaining_balance)
            })
            
            if remaining_balance <= 0:
                break
        
        return schedule
    
    def get_loan_summary(self) -> dict:
        """获取贷款摘要
        
        Returns:
            贷款摘要信息
        """
        self.update_overdue_status()
        
        return {
            'loan_id': self.loan_id,
            'loan_number': self.loan_number,
            'loan_type': self.loan_type,
            'bank_code': self.bank_code,
            'currency_code': self.currency.code if self.currency else 'Unknown',
            'loan_amount': float(self.loan_amount),
            'outstanding_balance': float(self.outstanding_balance),
            'interest_rate': float(self.interest_rate),
            'monthly_payment': float(self.monthly_payment),
            'term_months': self.term_months,
            'status': self.status,
            'days_overdue': self.days_overdue,
            'total_paid': float(self.total_paid),
            'next_payment_date': self.next_payment_date.strftime('%Y-%m-%d') if self.next_payment_date else None,
            'maturity_date': self.maturity_date.strftime('%Y-%m-%d') if self.maturity_date else None,
            'application_date': self.application_date.strftime('%Y-%m-%d'),
            'progress_percent': float((self.principal_paid / self.loan_amount) * 100) if self.loan_amount > 0 else 0
        }
    
    @classmethod
    async def get_user_loans(cls, session, user_id: str, status: str = None) -> List['Loan']:
        """获取用户贷款列表
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            status: 贷款状态过滤
            
        Returns:
            贷款列表
        """
        try:
            stmt = select(cls).filter_by(user_id=user_id)
            
            if status:
                stmt = stmt.filter_by(status=status)
            
            result = await session.execute(stmt.order_by(cls.created_at.desc()))
            return result.scalars().all()
        except Exception:
            return []
    
    def __repr__(self):
        return f"<Loan(loan_id='{self.loan_id}', number='{self.loan_number}', amount={self.loan_amount}, status='{self.status}')>"


class LoanPayment(BaseModel):
    """贷款还款记录模型"""
    __tablename__ = 'loan_payments'
    
    # 基本信息
    payment_id = Column(String(36), primary_key=True)
    loan_id = Column(String(36), ForeignKey('loans.loan_id'), nullable=False)
    
    # 还款信息
    payment_amount = Column(Numeric(20, 8), nullable=False)
    principal_amount = Column(Numeric(20, 8), nullable=False)
    interest_amount = Column(Numeric(20, 8), nullable=False)
    late_fee_amount = Column(Numeric(20, 8), default=0)
    
    # 时间信息
    payment_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    
    # 状态信息
    payment_method = Column(String(50))  # 还款方式
    transaction_id = Column(String(100))  # 交易ID
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 备注
    notes = Column(Text)
    
    # 关系
    loan = relationship("Loan", back_populates="payments")
    
    def __init__(self, loan_id: str, payment_amount: Decimal,
                 principal_amount: Decimal, interest_amount: Decimal, **kwargs):
        import uuid
        
        self.payment_id = str(uuid.uuid4())
        self.loan_id = loan_id
        self.payment_amount = payment_amount
        self.principal_amount = principal_amount
        self.interest_amount = interest_amount
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<LoanPayment(payment_id='{self.payment_id}', amount={self.payment_amount}, date='{self.payment_date}')>"