from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, select
import random
import uuid

from models.auth.user import User
from models.bank.bank_task import BankTask, UserBankTask, TaskType, TaskStatus, TaskDifficulty
from models.bank.credit_profile import CreditProfile
from models.bank.bank_card import BankCard
from dal.unit_of_work import UnitOfWork


class BankTaskService:
    """银行任务服务类
    
    提供银行任务相关功能，包括：
    - 任务生成和管理
    - 任务分发和验证
    - 任务完成度跟踪
    - 奖励发放
    - 任务统计分析
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
        # 银行列表
        self.banks = {
            'PBJC': '杰克币人民银行',
            'ICBJC': '杰克币工商银行',
            'JCCB': '杰克币建设银行',
            'ABJC': '杰克币农业银行',
            'BJC': '杰克币银行',
            'BCOJC': '杰克币交通银行',
            'PSBJC': '杰克币邮政储蓄银行'
        }
    
    # ==================== 任务生成 ====================
    
    async def generate_daily_tasks(self) -> Tuple[bool, str, int]:
        """生成每日任务
        
        Returns:
            (是否成功, 消息, 生成任务数量)
        """
        try:
            async with self.uow:
                generated_count = 0
                
                # 为每个银行生成任务
                for bank_code, bank_name in self.banks.items():
                    # 每个银行生成2-4个任务
                    task_count = random.randint(2, 4)
                    
                    for _ in range(task_count):
                        task = self._create_random_task(bank_code)
                        if task:
                            self.uow.add(task)
                            generated_count += 1
                
                await self.uow.commit()
                
                return True, f"成功生成 {generated_count} 个每日任务", generated_count
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"生成任务失败: {str(e)}", 0
    
    def _create_random_task(self, bank_code: str) -> Optional[BankTask]:
        """创建随机任务
        
        Args:
            bank_code: 银行代码
            
        Returns:
            银行任务对象
        """
        try:
            # 随机选择任务类型
            task_types = list(TaskType)
            task_type = random.choice(task_types)
            
            # 根据任务类型生成具体任务
            if task_type == TaskType.DEPOSIT:
                return self._create_deposit_task(bank_code)
            elif task_type == TaskType.LOAN_APPLICATION:
                return self._create_loan_task(bank_code)
            elif task_type == TaskType.CREDIT_IMPROVEMENT:
                return self._create_credit_task(bank_code)
            elif task_type == TaskType.INVESTMENT:
                return self._create_investment_task(bank_code)
            elif task_type == TaskType.REFERRAL:
                return self._create_referral_task(bank_code)
            elif task_type == TaskType.SURVEY:
                return self._create_survey_task(bank_code)
            elif task_type == TaskType.EDUCATION:
                return self._create_education_task(bank_code)
            elif task_type == TaskType.TRANSACTION:
                return self._create_transaction_task(bank_code)
            else:
                return None
                
        except Exception:
            return None
    
    def _create_deposit_task(self, bank_code: str) -> BankTask:
        """创建存款任务"""
        amounts = [1000, 5000, 10000, 20000, 50000]
        amount = random.choice(amounts)
        
        difficulty = TaskDifficulty.EASY if amount <= 5000 else TaskDifficulty.MEDIUM
        
        return BankTask(
            bank_code=bank_code,
            title=f"存款挑战 - {amount} JCY",
            description=f"在{self.banks[bank_code]}存入 {amount} JCY，体验我们的优质服务",
            task_type=TaskType.DEPOSIT.value,
            difficulty=difficulty.value,
            requirements={'min_amount': amount},
            reward_amount=Decimal(str(amount * 0.01)),  # 1%奖励
            credit_score_bonus=random.randint(5, 15),
            experience_points=random.randint(10, 30),
            completion_criteria={'min_amount': amount},
            duration_hours=24,
            max_participants=100,
            auto_approve=True
        )
    
    def _create_loan_task(self, bank_code: str) -> BankTask:
        """创建贷款任务"""
        return BankTask(
            bank_code=bank_code,
            title="贷款申请体验",
            description=f"在{self.banks[bank_code]}申请任意金额贷款，了解我们的贷款产品",
            task_type=TaskType.LOAN_APPLICATION.value,
            difficulty=TaskDifficulty.MEDIUM.value,
            min_credit_score=500,
            reward_amount=Decimal('500'),
            credit_score_bonus=20,
            experience_points=50,
            completion_criteria={'loan_applied': True},
            duration_hours=48,
            max_participants=50,
            auto_approve=False
        )
    
    def _create_credit_task(self, bank_code: str) -> BankTask:
        """创建信用提升任务"""
        return BankTask(
            bank_code=bank_code,
            title="信用提升计划",
            description=f"完成{self.banks[bank_code]}的信用评估，获得个性化信用改进建议",
            task_type=TaskType.CREDIT_IMPROVEMENT.value,
            difficulty=TaskDifficulty.EASY.value,
            reward_amount=Decimal('200'),
            credit_score_bonus=30,
            experience_points=25,
            completion_criteria={'credit_check': True},
            duration_hours=72,
            max_participants=200,
            auto_approve=True
        )
    
    def _create_investment_task(self, bank_code: str) -> BankTask:
        """创建投资任务"""
        amounts = [10000, 50000, 100000]
        amount = random.choice(amounts)
        
        return BankTask(
            bank_code=bank_code,
            title=f"理财产品体验 - {amount} JCY",
            description=f"购买{self.banks[bank_code]}理财产品，最低投资 {amount} JCY",
            task_type=TaskType.INVESTMENT.value,
            difficulty=TaskDifficulty.HARD.value,
            min_credit_score=600,
            requirements={'min_investment': amount},
            reward_amount=Decimal(str(amount * 0.005)),  # 0.5%奖励
            credit_score_bonus=25,
            experience_points=75,
            completion_criteria={'min_investment': amount},
            duration_hours=168,  # 一周
            max_participants=30,
            auto_approve=False
        )
    
    def _create_referral_task(self, bank_code: str) -> BankTask:
        """创建推荐任务"""
        return BankTask(
            bank_code=bank_code,
            title="好友推荐计划",
            description=f"推荐朋友开通{self.banks[bank_code]}银行卡，双方都有奖励",
            task_type=TaskType.REFERRAL.value,
            difficulty=TaskDifficulty.MEDIUM.value,
            min_account_age_days=30,
            reward_amount=Decimal('1000'),
            credit_score_bonus=15,
            experience_points=40,
            completion_criteria={'referrals': 1},
            duration_hours=240,  # 10天
            max_participants=100,
            is_repeatable=True,
            max_completions_per_user=5,
            auto_approve=False
        )
    
    def _create_survey_task(self, bank_code: str) -> BankTask:
        """创建调研任务"""
        return BankTask(
            bank_code=bank_code,
            title="客户满意度调研",
            description=f"参与{self.banks[bank_code]}客户满意度调研，帮助我们改进服务",
            task_type=TaskType.SURVEY.value,
            difficulty=TaskDifficulty.EASY.value,
            reward_amount=Decimal('100'),
            credit_score_bonus=5,
            experience_points=15,
            completion_criteria={
                'required_fields': ['satisfaction_rating', 'service_feedback', 'improvement_suggestions']
            },
            duration_hours=48,
            max_participants=500,
            auto_approve=True
        )
    
    def _create_education_task(self, bank_code: str) -> BankTask:
        """创建金融教育任务"""
        topics = ['理财基础', '投资风险', '信用管理', '贷款知识', '保险规划']
        topic = random.choice(topics)
        
        return BankTask(
            bank_code=bank_code,
            title=f"金融知识学习 - {topic}",
            description=f"学习{self.banks[bank_code]}提供的{topic}课程，提升金融素养",
            task_type=TaskType.EDUCATION.value,
            difficulty=TaskDifficulty.EASY.value,
            reward_amount=Decimal('50'),
            credit_score_bonus=10,
            experience_points=20,
            completion_criteria={'course_completed': True, 'quiz_score': 80},
            duration_hours=72,
            max_participants=1000,
            auto_approve=True
        )
    
    def _create_transaction_task(self, bank_code: str) -> BankTask:
        """创建交易任务"""
        transaction_counts = [5, 10, 20]
        count = random.choice(transaction_counts)
        
        return BankTask(
            bank_code=bank_code,
            title=f"活跃交易挑战 - {count}笔",
            description=f"使用{self.banks[bank_code]}银行卡完成 {count} 笔交易",
            task_type=TaskType.TRANSACTION.value,
            difficulty=TaskDifficulty.MEDIUM.value,
            required_bank_cards=[bank_code],
            reward_amount=Decimal(str(count * 10)),
            credit_score_bonus=count,
            experience_points=count * 2,
            completion_criteria={'min_transactions': count},
            duration_hours=168,  # 一周
            max_participants=200,
            auto_approve=True
        )
    
    # ==================== 任务管理 ====================
    
    async def create_custom_task(self, bank_code: str, title: str, description: str, 
                               task_type: str, **kwargs) -> Tuple[bool, str, Optional[BankTask]]:
        """创建自定义任务
        
        Args:
            bank_code: 银行代码
            title: 任务标题
            description: 任务描述
            task_type: 任务类型
            **kwargs: 其他参数
            
        Returns:
            (是否成功, 消息, 任务对象)
        """
        try:
            async with self.uow:
                # 验证银行代码
                if bank_code not in self.banks:
                    return False, f"无效的银行代码: {bank_code}", None
                
                # 验证任务类型
                valid_types = [t.value for t in TaskType]
                if task_type not in valid_types:
                    return False, f"无效的任务类型: {task_type}", None
                
                # 创建任务
                task = BankTask(
                    bank_code=bank_code,
                    title=title,
                    description=description,
                    task_type=task_type,
                    **kwargs
                )
                
                self.uow.add(task)
                await self.uow.commit()
                
                return True, "任务创建成功", task
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"创建任务失败: {str(e)}", None
    
    async def update_task(self, task_id: str, **kwargs) -> Tuple[bool, str]:
        """更新任务
        
        Args:
            task_id: 任务ID
            **kwargs: 更新字段
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                stmt = select(BankTask).filter_by(task_id=task_id)
                result = await self.uow.session.execute(stmt)
                task = result.scalars().first()
                if not task:
                    return False, "任务不存在"
                
                # 更新字段
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                
                task.updated_at = datetime.utcnow()
                
                await self.uow.commit()
                
                return True, "任务更新成功"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"更新任务失败: {str(e)}"
    
    async def deactivate_task(self, task_id: str, reason: str = None) -> Tuple[bool, str]:
        """停用任务
        
        Args:
            task_id: 任务ID
            reason: 停用原因
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                stmt = select(BankTask).filter_by(task_id=task_id)
                result = await self.uow.session.execute(stmt)
                task = result.scalars().first()
                if not task:
                    return False, "任务不存在"
                
                task.is_active = False
                task.updated_at = datetime.utcnow()
                
                if reason:
                    task.notes = f"停用原因: {reason}"
                
                await self.uow.commit()
                
                return True, "任务已停用"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"停用任务失败: {str(e)}"
    
    # ==================== 任务查询 ====================
    
    async def get_available_tasks_for_user(self, user_id: str, bank_code: str = None, 
                                   task_type: str = None, limit: int = 20) -> List[Dict]:
        """获取用户可用任务
        
        Args:
            user_id: 用户ID
            bank_code: 银行代码过滤
            task_type: 任务类型过滤
            limit: 返回数量限制
            
        Returns:
            任务列表
        """
        try:
            tasks = await BankTask.get_available_tasks(self.uow, user_id, bank_code, task_type)
            
            # 限制返回数量
            tasks = tasks[:limit]
            
            # 转换为字典格式
            result = []
            for task in tasks:
                task_info = task.get_task_summary()
                
                # 检查用户是否可以接取
                can_accept, reason = await task.can_user_accept(user_id, self.uow)
                task_info['can_accept'] = can_accept
                task_info['accept_reason'] = reason
                
                result.append(task_info)
            
            return result
            
        except Exception:
            return []
    
    async def get_user_task_history(self, user_id: str, status: str = None, 
                            limit: int = 50) -> List[Dict]:
        """获取用户任务历史
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            limit: 返回数量限制
            
        Returns:
            任务历史列表
        """
        try:
            stmt = select(UserBankTask).filter_by(user_id=user_id)
            
            if status:
                stmt = stmt.filter_by(status=status)
            
            stmt = stmt.order_by(UserBankTask.created_at.desc()).limit(limit)
            result = await self.uow.session.execute(stmt)
            user_tasks = result.scalars().all()
            
            return [ut.get_task_summary() for ut in user_tasks]
            
        except Exception:
            return []
    
    async def get_task_statistics(self, bank_code: str = None, 
                          days: int = 30) -> Dict[str, Any]:
        """获取任务统计
        
        Args:
            bank_code: 银行代码过滤
            days: 统计天数
            
        Returns:
            统计信息
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 基础查询
            task_stmt = select(BankTask).filter(
                BankTask.created_at >= start_date
            )
            
            user_task_stmt = select(UserBankTask).filter(
                UserBankTask.created_at >= start_date
            )
            
            if bank_code:
                task_stmt = task_stmt.filter(BankTask.bank_code == bank_code)
                user_task_stmt = user_task_stmt.join(BankTask).filter(
                    BankTask.bank_code == bank_code
                )
            
            # 统计数据
            total_tasks_result = await self.uow.session.execute(select(func.count()).select_from(task_stmt.alias()))
            total_tasks = total_tasks_result.scalar_one()

            active_tasks_result = await self.uow.session.execute(select(func.count()).select_from(task_stmt.filter(BankTask.is_active == True).alias()))
            active_tasks = active_tasks_result.scalar_one()
            
            total_accepted_result = await self.uow.session.execute(select(func.count()).select_from(user_task_stmt.alias()))
            total_accepted = total_accepted_result.scalar_one()

            total_completed_result = await self.uow.session.execute(select(func.count()).select_from(user_task_stmt.filter(UserBankTask.status == TaskStatus.COMPLETED.value).alias()))
            total_completed = total_completed_result.scalar_one()
            
            # 按类型统计
            type_stats = {}
            for task_type in TaskType:
                type_stmt = task_stmt.filter(BankTask.task_type == task_type.value)
                type_count_result = await self.uow.session.execute(select(func.count()).select_from(type_stmt.alias()))
                type_stats[task_type.value] = type_count_result.scalar_one()
            
            # 按银行统计
            bank_stats = {}
            for bank_code_key, bank_name in self.banks.items():
                bank_stmt = task_stmt.filter(BankTask.bank_code == bank_code_key)
                bank_count_result = await self.uow.session.execute(select(func.count()).select_from(bank_stmt.alias()))
                bank_stats[bank_code_key] = {
                    'name': bank_name,
                    'task_count': bank_count_result.scalar_one()
                }
            
            return {
                'period_days': days,
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'total_accepted': total_accepted,
                'total_completed': total_completed,
                'completion_rate': (total_completed / total_accepted * 100) if total_accepted > 0 else 0,
                'type_distribution': type_stats,
                'bank_distribution': bank_stats,
                'statistics_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'error': f"统计失败: {str(e)}"
            }
    
    # ==================== 任务验证 ====================
    
    async def verify_task_completion(self, user_task_id: str, 
                                   reviewer: str = None) -> Tuple[bool, str]:
        """验证任务完成
        
        Args:
            user_task_id: 用户任务ID
            reviewer: 审核人
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                user_task = self.uow.query(UserBankTask).filter_by(
                    user_task_id=user_task_id
                ).first()
                
                if not user_task:
                    return False, "用户任务不存在"
                
                if user_task.status != TaskStatus.SUBMITTED.value:
                    return False, "任务状态不正确"
                
                # 验证完成条件
                task = user_task.task
                if not await task.verify_completion(user_task.user_id, self.uow, 
                                             user_task.submission_data):
                    user_task.reject_task("未满足完成条件")
                    await self.uow.commit()
                    return False, "任务验证失败，已拒绝"
                
                # 批准任务
                user_task.approve_task(f"审核通过 - {reviewer or '系统'}")
                
                # 发放奖励
                task._grant_rewards(user_task.user_id, self.uow)
                user_task.rewards_granted = True
                
                # 更新任务统计
                task.total_completed += 1
                task._update_success_rate()
                
                await self.uow.commit()
                
                return True, "任务验证通过，奖励已发放"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"验证失败: {str(e)}"
    
    async def reject_task_submission(self, user_task_id: str, reason: str, 
                                   reviewer: str = None) -> Tuple[bool, str]:
        """拒绝任务提交
        
        Args:
            user_task_id: 用户任务ID
            reason: 拒绝原因
            reviewer: 审核人
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                user_task = self.uow.query(UserBankTask).filter_by(
                    user_task_id=user_task_id
                ).first()
                
                if not user_task:
                    return False, "用户任务不存在"
                
                if user_task.status != TaskStatus.SUBMITTED.value:
                    return False, "任务状态不正确"
                
                # 拒绝任务
                review_note = f"{reason} - {reviewer or '系统'}"
                user_task.reject_task(review_note)
                
                await self.uow.commit()
                
                return True, "任务已拒绝"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"拒绝失败: {str(e)}"
    
    # ==================== 清理任务 ====================
    
    async def cleanup_expired_tasks(self) -> Tuple[bool, str, int]:
        """清理过期任务
        
        Returns:
            (是否成功, 消息, 清理数量)
        """
        try:
            async with self.uow:
                now = datetime.utcnow()
                
                # 查找过期任务
                expired_tasks = self.uow.query(BankTask).filter(
                    BankTask.end_date < now,
                    BankTask.is_active == True
                ).all()
                
                # 停用过期任务
                for task in expired_tasks:
                    task.is_active = False
                    task.updated_at = now
                
                # 查找过期的用户任务
                expired_user_tasks = self.uow.query(UserBankTask).filter(
                    UserBankTask.status.in_([
                        TaskStatus.ACCEPTED.value,
                        TaskStatus.IN_PROGRESS.value
                    ])
                ).join(BankTask).filter(
                    BankTask.end_date < now
                ).all()
                
                # 标记为过期
                for user_task in expired_user_tasks:
                    user_task.status = TaskStatus.EXPIRED.value
                    user_task.updated_at = now
                
                total_cleaned = len(expired_tasks) + len(expired_user_tasks)
                
                await self.uow.commit()
                
                return True, f"清理完成，共处理 {total_cleaned} 个过期项目", total_cleaned
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"清理失败: {str(e)}", 0
    
    # ==================== 推荐系统 ====================
    
    def get_recommended_tasks(self, user_id: str, limit: int = 5) -> List[Dict]:
        """获取推荐任务
        
        Args:
            user_id: 用户ID
            limit: 推荐数量
            
        Returns:
            推荐任务列表
        """
        try:
            # 获取用户信息
            user = self.uow.query(User).filter_by(user_id=user_id).first()
            if not user:
                return []
            
            # 获取用户信用档案
            credit_profile = self.uow.query(CreditProfile).filter_by(
                user_id=user_id
            ).first()
            
            # 获取用户银行卡
            user_cards = self.uow.query(BankCard).filter_by(
                user_id=user_id, is_active=True
            ).all()
            user_banks = {card.bank_code for card in user_cards}
            
            # 获取可用任务
            available_tasks = BankTask.get_available_tasks(self.uow, user_id)
            
            # 推荐算法
            scored_tasks = []
            for task in available_tasks:
                score = self._calculate_task_score(task, user, credit_profile, user_banks)
                scored_tasks.append((task, score))
            
            # 按分数排序
            scored_tasks.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前N个推荐任务
            recommended = []
            for task, score in scored_tasks[:limit]:
                task_info = task.get_task_summary()
                task_info['recommendation_score'] = score
                task_info['recommendation_reason'] = self._get_recommendation_reason(
                    task, user, credit_profile, user_banks
                )
                recommended.append(task_info)
            
            return recommended
            
        except Exception:
            return []
    
    def _calculate_task_score(self, task: BankTask, user: User, 
                            credit_profile: CreditProfile, user_banks: set) -> float:
        """计算任务推荐分数
        
        Args:
            task: 任务对象
            user: 用户对象
            credit_profile: 信用档案
            user_banks: 用户银行集合
            
        Returns:
            推荐分数
        """
        score = 0.0
        
        # 基础分数
        score += 50.0
        
        # 银行匹配度
        if task.bank_code in user_banks:
            score += 20.0
        
        # 难度匹配度
        if credit_profile:
            if credit_profile.credit_score >= 700 and task.difficulty == TaskDifficulty.EASY.value:
                score += 10.0
            elif 500 <= credit_profile.credit_score < 700 and task.difficulty == TaskDifficulty.MEDIUM.value:
                score += 15.0
            elif credit_profile.credit_score < 500 and task.difficulty == TaskDifficulty.EASY.value:
                score += 15.0
        
        # 奖励吸引度
        if task.reward_amount > 0:
            score += min(float(task.reward_amount) / 100, 20.0)
        
        if task.credit_score_bonus > 0:
            score += min(task.credit_score_bonus / 2, 10.0)
        
        # 任务类型偏好（简化实现）
        if task.task_type in [TaskType.DEPOSIT.value, TaskType.EDUCATION.value]:
            score += 10.0
        
        # 参与度调整
        if task.max_participants:
            participation_rate = task.current_participants / task.max_participants
            if participation_rate < 0.5:
                score += 5.0  # 参与度低的任务加分
            elif participation_rate > 0.8:
                score -= 5.0  # 参与度高的任务减分
        
        return score
    
    def _get_recommendation_reason(self, task: BankTask, user: User, 
                                 credit_profile: CreditProfile, user_banks: set) -> str:
        """获取推荐理由
        
        Args:
            task: 任务对象
            user: 用户对象
            credit_profile: 信用档案
            user_banks: 用户银行集合
            
        Returns:
            推荐理由
        """
        reasons = []
        
        if task.bank_code in user_banks:
            reasons.append("您已有该银行的银行卡")
        
        if task.difficulty == TaskDifficulty.EASY.value:
            reasons.append("简单易完成")
        
        if task.reward_amount > 500:
            reasons.append("奖励丰厚")
        
        if task.credit_score_bonus > 15:
            reasons.append("有助于提升信用分")
        
        if task.task_type == TaskType.EDUCATION.value:
            reasons.append("提升金融知识")
        
        return "、".join(reasons) if reasons else "适合您的当前状况"