from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import json
import random

class TaskType(Enum):
    """任务类型"""
    TRADING = "trading"           # 交易任务
    DEPOSIT = "deposit"           # 存款任务
    LOAN = "loan"                # 贷款任务
    INVESTMENT = "investment"     # 投资任务
    CRYPTO = "crypto"            # 数字货币任务
    RESEARCH = "research"        # 研究任务
    REFERRAL = "referral"        # 推荐任务
    CHALLENGE = "challenge"      # 挑战任务

class TaskDifficulty(Enum):
    """任务难度"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

@dataclass
class TaskReward:
    """任务奖励"""
    cash_bonus: float = 0.0
    rate_discount: float = 0.0
    loan_limit_increase: float = 0.0
    relationship_points: int = 0
    special_privileges: List[str] = None
    
    def __post_init__(self):
        if self.special_privileges is None:
            self.special_privileges = []

@dataclass
class BankTask:
    """银行任务"""
    task_id: str
    bank_id: str
    title: str
    description: str
    task_type: TaskType
    difficulty: TaskDifficulty
    requirements: Dict
    reward: TaskReward
    deadline: Optional[datetime] = None
    is_repeatable: bool = False
    cooldown_hours: int = 24
    unlock_level: int = 1
    
    def __post_init__(self):
        self.status = "available"  # available, active, completed, expired, failed
        self.progress = {}
        self.accepted_time = None
        self.completed_time = None
        
    def accept_task(self):
        """接受任务"""
        if self.status != "available":
            return False, "任务不可接受"
            
        self.status = "active"
        self.accepted_time = datetime.now()
        if self.deadline is None:
            # 默认7天期限
            self.deadline = datetime.now() + timedelta(days=7)
        return True, "任务已接受"
        
    def update_progress(self, user_data, portfolio):
        """更新任务进度"""
        if self.status != "active":
            return False, 0.0
            
        progress_funcs = {
            TaskType.TRADING: self._update_trading_progress,
            TaskType.DEPOSIT: self._update_deposit_progress,
            TaskType.LOAN: self._update_loan_progress,
            TaskType.INVESTMENT: self._update_investment_progress,
            TaskType.CRYPTO: self._update_crypto_progress,
            TaskType.RESEARCH: self._update_research_progress,
            TaskType.REFERRAL: self._update_referral_progress,
            TaskType.CHALLENGE: self._update_challenge_progress
        }
        
        update_func = progress_funcs.get(self.task_type)
        if update_func:
            return update_func(user_data, portfolio)
        return False, 0.0
        
    def _update_trading_progress(self, user_data, portfolio):
        """更新交易任务进度"""
        req = self.requirements
        current_trades = user_data.get('trades_count', 0)
        
        if 'trade_count' in req:
            target = req['trade_count']
            progress = min(1.0, current_trades / target)
            self.progress['trades'] = current_trades
            
            if progress >= 1.0:
                return self._complete_task()
                
        if 'profit_target' in req:
            current_profit = user_data.get('total_profit', 0)
            target_profit = req['profit_target']
            progress = max(0, min(1.0, current_profit / target_profit))
            self.progress['profit'] = current_profit
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_deposit_progress(self, user_data, portfolio):
        """更新存款任务进度"""
        req = self.requirements
        bank_data = user_data.get('bank_data', {}).get(self.bank_id, {})
        deposits = bank_data.get('deposits', [])
        
        if 'deposit_amount' in req:
            total_deposits = sum(d.get('amount', 0) for d in deposits if d.get('status') == 'active')
            target = req['deposit_amount']
            progress = min(1.0, total_deposits / target)
            self.progress['deposits'] = total_deposits
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_loan_progress(self, user_data, portfolio):
        """更新贷款任务进度"""
        req = self.requirements
        bank_data = user_data.get('bank_data', {}).get(self.bank_id, {})
        loans = bank_data.get('loans', [])
        
        if 'loan_repayment' in req:
            repaid_loans = [l for l in loans if l.get('status') == 'repaid']
            target = req['loan_repayment']
            progress = min(1.0, len(repaid_loans) / target)
            self.progress['repaid_loans'] = len(repaid_loans)
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_investment_progress(self, user_data, portfolio):
        """更新投资任务进度"""
        req = self.requirements
        
        if 'portfolio_value' in req:
            # 计算投资组合价值
            total_value = user_data.get('cash', 0)
            for symbol, position in portfolio.items():
                if symbol != 'pending_orders' and isinstance(position, dict):
                    quantity = position.get('quantity', 0)
                    if quantity > 0:  # 只计算多头仓位
                        # 这里需要从market_data获取当前价格
                        total_value += quantity * 100  # 简化计算
                        
            target = req['portfolio_value']
            progress = min(1.0, total_value / target)
            self.progress['portfolio_value'] = total_value
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_crypto_progress(self, user_data, portfolio):
        """更新数字货币任务进度"""
        req = self.requirements
        crypto_trades = user_data.get('crypto_trades', 0)
        
        if 'crypto_trades' in req:
            target = req['crypto_trades']
            progress = min(1.0, crypto_trades / target)
            self.progress['crypto_trades'] = crypto_trades
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_research_progress(self, user_data, portfolio):
        """更新研究任务进度"""
        req = self.requirements
        research_points = user_data.get('research_points', 0)
        
        if 'research_reports' in req:
            target = req['research_reports']
            progress = min(1.0, research_points / target)
            self.progress['research'] = research_points
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_referral_progress(self, user_data, portfolio):
        """更新推荐任务进度"""
        req = self.requirements
        referrals = user_data.get('referrals', 0)
        
        if 'referral_count' in req:
            target = req['referral_count']
            progress = min(1.0, referrals / target)
            self.progress['referrals'] = referrals
            
            if progress >= 1.0:
                return self._complete_task()
                
        return False, self._calculate_overall_progress()
        
    def _update_challenge_progress(self, user_data, portfolio):
        """更新挑战任务进度"""
        req = self.requirements
        
        # 挑战任务通常有多个条件
        completed_conditions = 0
        total_conditions = len(req)
        
        for condition, target in req.items():
            if condition == 'consecutive_profitable_days':
                profitable_days = user_data.get('consecutive_profitable_days', 0)
                if profitable_days >= target:
                    completed_conditions += 1
            elif condition == 'max_drawdown_limit':
                max_drawdown = user_data.get('max_drawdown', 0)
                if max_drawdown <= target:
                    completed_conditions += 1
            # 可以添加更多条件
                    
        progress = completed_conditions / total_conditions if total_conditions > 0 else 0
        self.progress['challenge'] = completed_conditions
        
        if progress >= 1.0:
            return self._complete_task()
            
        return False, progress
        
    def _complete_task(self):
        """完成任务"""
        self.status = "completed"
        self.completed_time = datetime.now()
        return True, 1.0
        
    def _calculate_overall_progress(self):
        """计算总体进度"""
        if not self.progress:
            return 0.0
            
        # 根据任务类型计算进度
        req = self.requirements
        total_progress = 0.0
        total_weight = 0
        
        for key, target in req.items():
            if key in self.progress:
                current = self.progress[key]
                weight = 1.0
                progress = min(1.0, current / target) if target > 0 else 0
                total_progress += progress * weight
                total_weight += weight
                
        return total_progress / total_weight if total_weight > 0 else 0.0
        
    def is_expired(self):
        """检查任务是否过期"""
        if self.deadline and datetime.now() > self.deadline:
            if self.status == "active":
                self.status = "expired"
            return True
        return False
        
    def can_repeat(self):
        """检查是否可以重复"""
        if not self.is_repeatable:
            return False
            
        if self.completed_time:
            cooldown_end = self.completed_time + timedelta(hours=self.cooldown_hours)
            return datetime.now() >= cooldown_end
            
        return True

class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.task_templates = {}
        self.active_tasks = {}  # user_id -> [task_ids]
        self.completed_tasks = {}  # user_id -> [task_ids]
        self.init_task_templates()
        
    def init_task_templates(self):
        """初始化任务模板"""
        self._create_commercial_bank_tasks()
        self._create_investment_bank_tasks()
        self._create_trading_bank_tasks()
        self._create_crypto_bank_tasks()
        self._create_wealth_bank_tasks()
        self._create_central_bank_tasks()
        
    def _create_commercial_bank_tasks(self):
        """创建商业银行任务"""
        bank_id = "JC_COMMERCIAL"
        
        # 新手任务
        self.task_templates[f"{bank_id}_STARTER_DEPOSIT"] = BankTask(
            task_id=f"{bank_id}_STARTER_DEPOSIT",
            bank_id=bank_id,
            title="首次存款",
            description="在商业银行进行首次存款，金额不少于J$10,000",
            task_type=TaskType.DEPOSIT,
            difficulty=TaskDifficulty.EASY,
            requirements={"deposit_amount": 10000},
            reward=TaskReward(
                cash_bonus=500,
                rate_discount=0.005,
                relationship_points=10
            ),
            is_repeatable=False,
            unlock_level=1
        )
        
        # 交易任务
        self.task_templates[f"{bank_id}_FREQUENT_TRADER"] = BankTask(
            task_id=f"{bank_id}_FREQUENT_TRADER",
            bank_id=bank_id,
            title="活跃交易者",
            description="在一周内完成至少20笔股票交易",
            task_type=TaskType.TRADING,
            difficulty=TaskDifficulty.MEDIUM,
            requirements={"trade_count": 20},
            reward=TaskReward(
                cash_bonus=1000,
                rate_discount=0.01,
                relationship_points=15
            ),
            is_repeatable=True,
            cooldown_hours=168,  # 一周
            unlock_level=2
        )
        
    def _create_investment_bank_tasks(self):
        """创建投资银行任务"""
        bank_id = "JC_INVESTMENT"
        
        self.task_templates[f"{bank_id}_PORTFOLIO_BUILDER"] = BankTask(
            task_id=f"{bank_id}_PORTFOLIO_BUILDER",
            bank_id=bank_id,
            title="投资组合构建师",
            description="建立价值不少于J$500,000的多样化投资组合",
            task_type=TaskType.INVESTMENT,
            difficulty=TaskDifficulty.HARD,
            requirements={"portfolio_value": 500000},
            reward=TaskReward(
                cash_bonus=10000,
                loan_limit_increase=100000,
                relationship_points=25,
                special_privileges=["投资顾问服务"]
            ),
            is_repeatable=False,
            unlock_level=5
        )
        
    def _create_trading_bank_tasks(self):
        """创建交易银行任务"""
        bank_id = "JC_TRADING"
        
        self.task_templates[f"{bank_id}_PROFIT_MASTER"] = BankTask(
            task_id=f"{bank_id}_PROFIT_MASTER",
            bank_id=bank_id,
            title="盈利大师",
            description="实现总盈利超过J$100,000",
            task_type=TaskType.TRADING,
            difficulty=TaskDifficulty.EXPERT,
            requirements={"profit_target": 100000},
            reward=TaskReward(
                cash_bonus=20000,
                rate_discount=0.02,
                loan_limit_increase=500000,
                relationship_points=50,
                special_privileges=["VIP交易通道", "专属客户经理"]
            ),
            is_repeatable=False,
            unlock_level=8
        )
        
    def _create_crypto_bank_tasks(self):
        """创建数字银行任务"""
        bank_id = "JC_CRYPTO"
        
        self.task_templates[f"{bank_id}_CRYPTO_PIONEER"] = BankTask(
            task_id=f"{bank_id}_CRYPTO_PIONEER",
            bank_id=bank_id,
            title="数字货币先锋",
            description="完成50笔数字货币相关交易",
            task_type=TaskType.CRYPTO,
            difficulty=TaskDifficulty.HARD,
            requirements={"crypto_trades": 50},
            reward=TaskReward(
                cash_bonus=15000,
                special_privileges=["DeFi服务权限", "智能合约部署"]
            ),
            is_repeatable=True,
            cooldown_hours=720,  # 30天
            unlock_level=10
        )
        
    def _create_wealth_bank_tasks(self):
        """创建私人银行任务"""
        bank_id = "JC_WEALTH"
        
        self.task_templates[f"{bank_id}_HIGH_NET_WORTH"] = BankTask(
            task_id=f"{bank_id}_HIGH_NET_WORTH",
            bank_id=bank_id,
            title="高净值客户",
            description="维持净资产超过J$2,000,000连续30天",
            task_type=TaskType.CHALLENGE,
            difficulty=TaskDifficulty.EXPERT,
            requirements={"net_worth_target": 2000000, "duration_days": 30},
            reward=TaskReward(
                cash_bonus=50000,
                rate_discount=0.03,
                special_privileges=["家族信托服务", "私人理财师", "专属贵宾室"]
            ),
            is_repeatable=False,
            unlock_level=15
        )
        
    def _create_central_bank_tasks(self):
        """创建央行任务"""
        bank_id = "JC_CENTRAL"
        
        self.task_templates[f"{bank_id}_ECONOMIC_RESEARCH"] = BankTask(
            task_id=f"{bank_id}_ECONOMIC_RESEARCH",
            bank_id=bank_id,
            title="经济研究员",
            description="提交5份市场分析报告",
            task_type=TaskType.RESEARCH,
            difficulty=TaskDifficulty.MEDIUM,
            requirements={"research_reports": 5},
            reward=TaskReward(
                cash_bonus=5000,
                special_privileges=["经济数据早期访问", "政策预告"]
            ),
            is_repeatable=True,
            cooldown_hours=336,  # 14天
            unlock_level=3
        )
        
    def get_available_tasks(self, user_data, bank_id=None):
        """获取可用任务"""
        user_level = user_data.get('level', 1)
        available_tasks = []
        
        for task_template in self.task_templates.values():
            if bank_id and task_template.bank_id != bank_id:
                continue
                
            if task_template.unlock_level > user_level:
                continue
                
            # 检查是否已完成且不可重复
            if not task_template.is_repeatable:
                user_completed = self.completed_tasks.get(user_data.get('username', ''), [])
                if task_template.task_id in user_completed:
                    continue
                    
            # 检查重复任务的冷却时间
            if task_template.is_repeatable and not task_template.can_repeat():
                continue
                
            available_tasks.append(task_template)
            
        return available_tasks
        
    def accept_task(self, user_id, task_id):
        """接受任务"""
        if task_id not in self.task_templates:
            return False, "任务不存在"
            
        # 复制任务模板创建实例
        task = self.task_templates[task_id]
        success, message = task.accept_task()
        
        if success:
            if user_id not in self.active_tasks:
                self.active_tasks[user_id] = []
            self.active_tasks[user_id].append(task_id)
            
        return success, message
        
    def complete_task(self, user_id, task_id):
        """完成任务"""
        if user_id not in self.active_tasks or task_id not in self.active_tasks[user_id]:
            return False, "任务未激活"
            
        # 移动到已完成列表
        self.active_tasks[user_id].remove(task_id)
        if user_id not in self.completed_tasks:
            self.completed_tasks[user_id] = []
        self.completed_tasks[user_id].append(task_id)
        
        return True, "任务已完成"
        
    def get_active_tasks(self, user_id):
        """获取活跃任务"""
        if user_id not in self.active_tasks:
            return []
            
        active_task_objects = []
        for task_id in self.active_tasks[user_id]:
            if task_id in self.task_templates:
                active_task_objects.append(self.task_templates[task_id])
                
        return active_task_objects
        
    def update_all_tasks(self, user_id, user_data, portfolio):
        """更新所有任务进度"""
        if user_id not in self.active_tasks:
            return []
            
        completed_tasks = []
        for task_id in self.active_tasks[user_id][:]:  # 使用切片复制列表
            if task_id in self.task_templates:
                task = self.task_templates[task_id]
                task.update_progress(user_data, portfolio)
                
                if task.status == "completed":
                    self.complete_task(user_id, task_id)
                    completed_tasks.append(task)
                elif task.is_expired():
                    self.active_tasks[user_id].remove(task_id)
                    
        return completed_tasks 