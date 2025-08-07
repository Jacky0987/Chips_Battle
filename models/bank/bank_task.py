from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum

from dal.database import Base


class TaskType(Enum):
    """任务类型枚举"""
    DEPOSIT = "deposit"  # 存款任务
    LOAN_APPLICATION = "loan_application"  # 贷款申请任务
    CREDIT_IMPROVEMENT = "credit_improvement"  # 信用提升任务
    INVESTMENT = "investment"  # 投资任务
    REFERRAL = "referral"  # 推荐任务
    SURVEY = "survey"  # 调研任务
    EDUCATION = "education"  # 金融教育任务
    TRANSACTION = "transaction"  # 交易任务


class TaskStatus(Enum):
    """任务状态枚举"""
    AVAILABLE = "available"  # 可接取
    ACCEPTED = "accepted"  # 已接取
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    SUBMITTED = "submitted"  # 已提交
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期
    CANCELLED = "cancelled"  # 已取消


class TaskDifficulty(Enum):
    """任务难度枚举"""
    EASY = "easy"  # 简单
    MEDIUM = "medium"  # 中等
    HARD = "hard"  # 困难
    EXPERT = "expert"  # 专家级


class BankTask(Base):
    """银行任务模型"""
    __tablename__ = 'bank_tasks'
    
    # 基本信息
    task_id = Column(String(36), primary_key=True)
    bank_code = Column(String(10), nullable=False)  # 发布银行
    
    # 任务信息
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String(30), nullable=False)  # TaskType
    difficulty = Column(String(20), default=TaskDifficulty.EASY.value)
    
    # 要求条件
    requirements = Column(JSON)  # 任务要求
    min_credit_score = Column(Integer, default=0)  # 最低信用分要求
    min_account_age_days = Column(Integer, default=0)  # 最低账户年龄要求
    required_bank_cards = Column(JSON)  # 需要的银行卡类型
    
    # 奖励信息
    reward_amount = Column(Numeric(20, 8), default=0)  # 奖励金额
    reward_currency = Column(String(10), default='JCY')  # 奖励货币
    credit_score_bonus = Column(Integer, default=0)  # 信用分奖励
    experience_points = Column(Integer, default=0)  # 经验值奖励
    special_rewards = Column(JSON)  # 特殊奖励
    
    # 时间限制
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    duration_hours = Column(Integer)  # 任务持续时间(小时)
    
    # 限制条件
    max_participants = Column(Integer)  # 最大参与人数
    current_participants = Column(Integer, default=0)  # 当前参与人数
    max_completions_per_user = Column(Integer, default=1)  # 每用户最大完成次数
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    is_repeatable = Column(Boolean, default=False)
    auto_approve = Column(Boolean, default=False)  # 自动批准
    
    # 完成条件
    completion_criteria = Column(JSON)  # 完成标准
    verification_method = Column(String(50), default='manual')  # 验证方式
    
    # 统计信息
    total_accepted = Column(Integer, default=0)  # 总接取数
    total_completed = Column(Integer, default=0)  # 总完成数
    success_rate = Column(Numeric(5, 4), default=0)  # 成功率
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 创建者信息
    created_by = Column(String(100))  # 创建者
    notes = Column(Text)  # 备注
    
    # 关系
    user_tasks = relationship("UserBankTask", back_populates="task", cascade="all, delete-orphan")
    
    def __init__(self, bank_code: str, title: str, description: str, 
                 task_type: str, **kwargs):
        import uuid
        
        self.task_id = str(uuid.uuid4())
        self.bank_code = bank_code.upper()
        self.title = title
        self.description = description
        self.task_type = task_type
        
        # 设置默认结束时间(30天后)
        if not kwargs.get('end_date'):
            self.end_date = datetime.utcnow() + timedelta(days=30)
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def is_available(self) -> bool:
        """检查任务是否可用
        
        Returns:
            是否可用
        """
        now = datetime.utcnow()
        
        # 检查基本条件
        if not self.is_active:
            return False
        
        # 检查时间范围
        if now < self.start_date or (self.end_date and now > self.end_date):
            return False
        
        # 检查参与人数限制
        if self.max_participants and self.current_participants >= self.max_participants:
            return False
        
        return True
    
    def can_user_accept(self, user_id: str, uow) -> tuple[bool, str]:
        """检查用户是否可以接取任务
        
        Args:
            user_id: 用户ID
            uow: 工作单元
            
        Returns:
            (是否可以接取, 原因)
        """
        if not self.is_available():
            return False, "任务不可用"
        
        try:
            # 检查用户是否已接取
            existing_task = uow.query(UserBankTask).filter_by(
                user_id=user_id,
                task_id=self.task_id,
                status__in=[TaskStatus.ACCEPTED.value, TaskStatus.IN_PROGRESS.value]
            ).first()
            
            if existing_task:
                return False, "已接取此任务"
            
            # 检查完成次数限制
            if not self.is_repeatable:
                completed_count = uow.query(UserBankTask).filter_by(
                    user_id=user_id,
                    task_id=self.task_id,
                    status=TaskStatus.COMPLETED.value
                ).count()
                
                if completed_count >= self.max_completions_per_user:
                    return False, "已达到最大完成次数"
            
            # 检查用户条件
            from models.auth.user import User
            from models.bank.credit_profile import CreditProfile
            
            user = uow.query(User).filter_by(user_id=user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 检查信用分要求
            if self.min_credit_score > 0:
                credit_profile = uow.query(CreditProfile).filter_by(user_id=user_id).first()
                if not credit_profile or credit_profile.credit_score < self.min_credit_score:
                    return False, f"信用分不足，需要{self.min_credit_score}分"
            
            # 检查账户年龄要求
            if self.min_account_age_days > 0:
                account_age = (datetime.utcnow() - user.created_at).days
                if account_age < self.min_account_age_days:
                    return False, f"账户年龄不足，需要{self.min_account_age_days}天"
            
            # 检查银行卡要求
            if self.required_bank_cards:
                from models.bank.bank_card import BankCard
                user_cards = uow.query(BankCard).filter_by(
                    user_id=user_id, is_active=True
                ).all()
                
                user_bank_codes = {card.bank_code for card in user_cards}
                required_codes = set(self.required_bank_cards)
                
                if not required_codes.issubset(user_bank_codes):
                    missing = required_codes - user_bank_codes
                    return False, f"需要以下银行的银行卡: {', '.join(missing)}"
            
            return True, "可以接取"
            
        except Exception as e:
            return False, f"检查失败: {str(e)}"
    
    def accept_task(self, user_id: str, uow) -> tuple[bool, str, Optional['UserBankTask']]:
        """接取任务
        
        Args:
            user_id: 用户ID
            uow: 工作单元
            
        Returns:
            (是否成功, 消息, 用户任务对象)
        """
        can_accept, reason = self.can_user_accept(user_id, uow)
        if not can_accept:
            return False, reason, None
        
        try:
            # 创建用户任务记录
            user_task = UserBankTask(
                user_id=user_id,
                task_id=self.task_id,
                status=TaskStatus.ACCEPTED.value
            )
            
            uow.add(user_task)
            
            # 更新任务统计
            self.total_accepted += 1
            self.current_participants += 1
            self.updated_at = datetime.utcnow()
            
            return True, "任务接取成功", user_task
            
        except Exception as e:
            return False, f"接取失败: {str(e)}", None
    
    def complete_task(self, user_id: str, uow, submission_data: Dict = None) -> tuple[bool, str]:
        """完成任务
        
        Args:
            user_id: 用户ID
            uow: 工作单元
            submission_data: 提交数据
            
        Returns:
            (是否成功, 消息)
        """
        try:
            # 查找用户任务
            user_task = uow.query(UserBankTask).filter_by(
                user_id=user_id,
                task_id=self.task_id,
                status__in=[TaskStatus.ACCEPTED.value, TaskStatus.IN_PROGRESS.value]
            ).first()
            
            if not user_task:
                return False, "未找到可完成的任务"
            
            # 验证完成条件
            if not self._verify_completion(user_id, uow, submission_data):
                return False, "未满足完成条件"
            
            # 更新用户任务状态
            if self.auto_approve:
                user_task.status = TaskStatus.COMPLETED.value
                user_task.completed_at = datetime.utcnow()
                
                # 发放奖励
                self._grant_rewards(user_id, uow)
                
                # 更新统计
                self.total_completed += 1
                self._update_success_rate()
                
                return True, "任务完成，奖励已发放"
            else:
                user_task.status = TaskStatus.SUBMITTED.value
                user_task.submitted_at = datetime.utcnow()
                
                return True, "任务已提交，等待审核"
            
        except Exception as e:
            return False, f"完成失败: {str(e)}"
    
    def _verify_completion(self, user_id: str, uow, submission_data: Dict = None) -> bool:
        """验证任务完成条件
        
        Args:
            user_id: 用户ID
            uow: 工作单元
            submission_data: 提交数据
            
        Returns:
            是否满足完成条件
        """
        if not self.completion_criteria:
            return True
        
        try:
            criteria = self.completion_criteria
            
            # 根据任务类型验证不同条件
            if self.task_type == TaskType.DEPOSIT.value:
                return self._verify_deposit_task(user_id, uow, criteria)
            elif self.task_type == TaskType.LOAN_APPLICATION.value:
                return self._verify_loan_task(user_id, uow, criteria)
            elif self.task_type == TaskType.TRANSACTION.value:
                return self._verify_transaction_task(user_id, uow, criteria)
            elif self.task_type == TaskType.SURVEY.value:
                return self._verify_survey_task(submission_data, criteria)
            else:
                return True  # 其他类型默认通过
                
        except Exception:
            return False
    
    def _verify_deposit_task(self, user_id: str, uow, criteria: Dict) -> bool:
        """验证存款任务"""
        required_amount = Decimal(str(criteria.get('min_amount', 0)))
        
        # 查询用户最近的存款记录
        # 这里需要实现具体的存款记录查询逻辑
        return True  # 简化实现
    
    def _verify_loan_task(self, user_id: str, uow, criteria: Dict) -> bool:
        """验证贷款任务"""
        # 查询用户是否申请了贷款
        from models.bank.loan import Loan
        
        recent_loans = uow.query(Loan).filter(
            Loan.user_id == user_id,
            Loan.application_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return recent_loans > 0
    
    def _verify_transaction_task(self, user_id: str, uow, criteria: Dict) -> bool:
        """验证交易任务"""
        min_transactions = criteria.get('min_transactions', 1)
        
        # 查询用户最近的交易记录
        # 这里需要实现具体的交易记录查询逻辑
        return True  # 简化实现
    
    def _verify_survey_task(self, submission_data: Dict, criteria: Dict) -> bool:
        """验证调研任务"""
        if not submission_data:
            return False
        
        required_fields = criteria.get('required_fields', [])
        
        for field in required_fields:
            if field not in submission_data or not submission_data[field]:
                return False
        
        return True
    
    def _grant_rewards(self, user_id: str, uow):
        """发放奖励
        
        Args:
            user_id: 用户ID
            uow: 工作单元
        """
        try:
            # 发放金额奖励
            if self.reward_amount > 0:
                # 这里需要实现具体的账户充值逻辑
                pass
            
            # 发放信用分奖励
            if self.credit_score_bonus > 0:
                from models.bank.credit_profile import CreditProfile
                
                credit_profile = CreditProfile.get_or_create_profile(uow, user_id)
                credit_profile.credit_score += self.credit_score_bonus
                credit_profile.last_updated = datetime.utcnow()
            
            # 发放经验值奖励
            if self.experience_points > 0:
                from models.auth.user import User
                
                user = uow.query(User).filter_by(user_id=user_id).first()
                if user:
                    user.add_experience(self.experience_points)
            
        except Exception as e:
            # 记录奖励发放失败
            pass
    
    def _update_success_rate(self):
        """更新成功率"""
        if self.total_accepted > 0:
            self.success_rate = Decimal(self.total_completed) / Decimal(self.total_accepted)
        else:
            self.success_rate = Decimal('0')
    
    def get_task_summary(self) -> Dict:
        """获取任务摘要
        
        Returns:
            任务摘要信息
        """
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'difficulty': self.difficulty,
            'bank_code': self.bank_code,
            'reward_amount': float(self.reward_amount),
            'reward_currency': self.reward_currency,
            'credit_score_bonus': self.credit_score_bonus,
            'experience_points': self.experience_points,
            'min_credit_score': self.min_credit_score,
            'duration_hours': self.duration_hours,
            'current_participants': self.current_participants,
            'max_participants': self.max_participants,
            'success_rate': float(self.success_rate * 100) if self.success_rate else 0,
            'is_available': self.is_available(),
            'start_date': self.start_date.strftime('%Y-%m-%d %H:%M'),
            'end_date': self.end_date.strftime('%Y-%m-%d %H:%M') if self.end_date else None,
            'requirements': self.requirements or {},
            'completion_criteria': self.completion_criteria or {}
        }
    
    @classmethod
    def get_available_tasks(cls, uow, user_id: str = None, bank_code: str = None, 
                          task_type: str = None) -> List['BankTask']:
        """获取可用任务列表
        
        Args:
            uow: 工作单元
            user_id: 用户ID (用于过滤用户可接取的任务)
            bank_code: 银行代码过滤
            task_type: 任务类型过滤
            
        Returns:
            可用任务列表
        """
        try:
            query = uow.query(cls).filter(
                cls.is_active == True,
                cls.start_date <= datetime.utcnow()
            )
            
            # 添加结束时间过滤
            query = query.filter(
                (cls.end_date.is_(None)) | (cls.end_date > datetime.utcnow())
            )
            
            # 添加银行过滤
            if bank_code:
                query = query.filter(cls.bank_code == bank_code.upper())
            
            # 添加任务类型过滤
            if task_type:
                query = query.filter(cls.task_type == task_type)
            
            tasks = query.order_by(cls.created_at.desc()).all()
            
            # 如果指定了用户，进一步过滤用户可接取的任务
            if user_id:
                available_tasks = []
                for task in tasks:
                    can_accept, _ = task.can_user_accept(user_id, uow)
                    if can_accept:
                        available_tasks.append(task)
                return available_tasks
            
            return tasks
            
        except Exception:
            return []
    
    def __repr__(self):
        return f"<BankTask(task_id='{self.task_id}', title='{self.title}', type='{self.task_type}')>"


class UserBankTask(Base):
    """用户银行任务关联模型"""
    __tablename__ = 'user_bank_tasks'
    
    # 基本信息
    user_task_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    task_id = Column(String(36), ForeignKey('bank_tasks.task_id'), nullable=False)
    
    # 状态信息
    status = Column(String(20), default=TaskStatus.ACCEPTED.value)
    progress = Column(Numeric(5, 4), default=0)  # 进度百分比
    
    # 时间信息
    accepted_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    submitted_at = Column(DateTime)
    completed_at = Column(DateTime)
    expired_at = Column(DateTime)
    
    # 提交数据
    submission_data = Column(JSON)  # 提交的数据
    review_notes = Column(Text)  # 审核备注
    
    # 奖励信息
    rewards_granted = Column(Boolean, default=False)
    reward_details = Column(JSON)  # 奖励详情
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    task = relationship("BankTask", back_populates="user_tasks")
    
    def __init__(self, user_id: str, task_id: str, **kwargs):
        import uuid
        
        self.user_task_id = str(uuid.uuid4())
        self.user_id = user_id
        self.task_id = task_id
        
        # 应用其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def start_task(self):
        """开始任务"""
        self.status = TaskStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def submit_task(self, submission_data: Dict = None):
        """提交任务"""
        self.status = TaskStatus.SUBMITTED.value
        self.submitted_at = datetime.utcnow()
        self.submission_data = submission_data
        self.updated_at = datetime.utcnow()
    
    def approve_task(self, review_notes: str = None):
        """批准任务"""
        self.status = TaskStatus.APPROVED.value
        self.completed_at = datetime.utcnow()
        self.review_notes = review_notes
        self.updated_at = datetime.utcnow()
    
    def reject_task(self, review_notes: str = None):
        """拒绝任务"""
        self.status = TaskStatus.REJECTED.value
        self.review_notes = review_notes
        self.updated_at = datetime.utcnow()
    
    def get_task_summary(self) -> Dict:
        """获取用户任务摘要"""
        return {
            'user_task_id': self.user_task_id,
            'task_id': self.task_id,
            'status': self.status,
            'progress': float(self.progress * 100) if self.progress else 0,
            'accepted_at': self.accepted_at.strftime('%Y-%m-%d %H:%M'),
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M') if self.started_at else None,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M') if self.submitted_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'rewards_granted': self.rewards_granted,
            'task_info': self.task.get_task_summary() if self.task else {}
        }
    
    def __repr__(self):
        return f"<UserBankTask(user_task_id='{self.user_task_id}', status='{self.status}')>"