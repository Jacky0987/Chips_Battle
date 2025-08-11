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
    
    async def can_user_accept(self, user_id: str, uow) -> tuple[bool, str]:
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
            existing_task_stmt = select(UserBankTask).filter_by(
                user_id=user_id,
                task_id=self.task_id,
                status__in=[TaskStatus.ACCEPTED.value, TaskStatus.IN_PROGRESS.value]
            )
            existing_task_result = await uow.session.execute(existing_task_stmt)
            existing_task = existing_task_result.scalars().first()
            
            if existing_task:
                return False, "已接取此任务"
            
            # 检查完成次数限制
            if not self.is_repeatable:
                completed_count_stmt = select(func.count(UserBankTask.id)).filter_by(
                    user_id=user_id,
                    task_id=self.task_id,
                    status=TaskStatus.COMPLETED.value
                )
                completed_count_result = await uow.session.execute(completed_count_stmt)
                completed_count = completed_count_result.scalar_one()
                
                if completed_count >= self.max_completions_per_user:
                    return False, "已达到最大完成次数"
            
            # 检查用户条件
            from models.auth.user import User
            from models.bank.credit_profile import CreditProfile
            
            user_result = await uow.session.execute(select(User).filter_by(user_id=user_id))
            user = user_result.scalars().first()
            if not user:
                return False, "用户不存在"
            
            # 检查信用分要求
            if self.min_credit_score > 0:
                credit_profile_result = await uow.session.execute(select(CreditProfile).filter_by(user_id=user_id))
                credit_profile = credit_profile_result.scalars().first()
                if not credit_profile or credit_profile.credit_score < self.min_credit_score:
                    return False, f"信用分不足，需要{self.min_credit_score}分"
            
            # 检查账户年龄要求
            if self.min_account_age_days > 0:
                account_age = (datetime.utcnow() - user.created_at).days
                if account_age < self.min_account_age_days:
                    return False, f"账户年龄不足，需要{self.min_account_age_days}天"
            
            return True, ""
            
        except Exception as e:
            return False, f"检查任务资格失败: {e}"

    async def accept_task(self, user_id: str, uow) -> tuple[bool, str, Optional['UserBankTask']]:
        """用户接取任务"""
        can_accept, reason = await self.can_user_accept(user_id, uow)
        if not can_accept:
            return False, reason, None
        
        try:
            # 创建用户任务记录
            user_task = UserBankTask(
                user_id=user_id,
                task_id=self.task_id,
                bank_code=self.bank_code
            )
            
            uow.add(user_task)
            
            # 更新任务统计
            self.current_participants += 1
            self.total_accepted += 1
            
            return True, "任务接取成功", user_task
            
        except Exception as e:
            return False, f"接取任务失败: {str(e)}", None

    async def complete_task(self, user_id: str, uow, submission_data: Dict = None) -> tuple[bool, str]:
        """用户完成任务"""
        try:
            # 查找用户任务
            user_task_stmt = select(UserBankTask).filter_by(
                user_id=user_id,
                task_id=self.task_id,
                status__in=[TaskStatus.ACCEPTED.value, TaskStatus.IN_PROGRESS.value]
            )
            user_task_result = await uow.session.execute(user_task_stmt)
            user_task = user_task_result.scalars().first()
            
            if not user_task:
                return False, "未找到已接取的任务"
            
            # 验证完成条件
            is_complete, reason = await self.verify_completion(user_id, uow, submission_data)
            if not is_complete:
                return False, f"任务未完成: {reason}"
            
            # 更新用户任务状态
            user_task.status = TaskStatus.COMPLETED.value
            user_task.completed_at = datetime.utcnow()
            user_task.submission_data = submission_data
            
            # 发放奖励
            await self.grant_rewards(user_id, uow)
            
            # 更新任务统计
            self.total_completed += 1
            if self.total_accepted > 0:
                self.success_rate = Decimal(self.total_completed) / Decimal(self.total_accepted)
            
            return True, "任务完成"
            
        except Exception as e:
            return False, f"完成任务失败: {str(e)}"

    async def verify_completion(self, user_id: str, uow, submission_data: Dict = None) -> tuple[bool, str]:
        """验证任务是否完成"""
        # 默认实现，可被子类覆盖
        # 简单任务可直接返回True
        if self.task_type == TaskType.DEPOSIT.value:
            # 检查存款记录
            required_amount = self.completion_criteria.get('amount', 0)
            # ... 这里需要查询交易记录 ...
            return True, ""
        
        return True, ""

    async def grant_rewards(self, user_id: str, uow):
        """发放任务奖励"""
        from models.bank.bank_account import BankAccount
        # 发放货币奖励
        if self.reward_amount > 0:
            # 找到用户默认账户
            default_account_stmt = select(BankAccount).filter_by(user_id=user_id, is_default=True)
            default_account_result = await uow.session.execute(default_account_stmt)
            default_account = default_account_result.scalars().first()
            if default_account:
                await default_account.deposit(self.reward_amount, f"任务奖励: {self.title}")

        # 发放信用分奖励
        if self.credit_score_bonus > 0:
            from models.bank.credit_profile import CreditProfile
            credit_profile_stmt = select(CreditProfile).filter_by(user_id=user_id)
            credit_profile_result = await uow.session.execute(credit_profile_stmt)
            credit_profile = credit_profile_result.scalars().first()
            if credit_profile:
                await credit_profile.add_credit_history("task_reward", self.credit_score_bonus, f"完成任务: {self.title}")

    @classmethod
    async def get_available_tasks(cls, uow, user_id: str = None, bank_code: str = None) -> List['BankTask']:
        """获取可用的任务列表"""
        try:
            stmt = select(cls).filter(
                cls.is_active == True,
                cls.start_date <= datetime.utcnow(),
                (cls.end_date == None) | (cls.end_date >= datetime.utcnow()),
                (cls.max_participants == None) | (cls.current_participants < cls.max_participants)
            )
            
            if bank_code:
                stmt = stmt.filter_by(bank_code=bank_code)
            
            result = await uow.session.execute(stmt)
            tasks = result.scalars().all()
            
            if user_id:
                # 过滤掉用户不符合条件的任务
                available_tasks = []
                for task in tasks:
                    can_accept, _ = await task.can_user_accept(user_id, uow)
                    if can_accept:
                        available_tasks.append(task)
                return available_tasks
            else:
                return tasks
                
        except Exception:
            return []


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