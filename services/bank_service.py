from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from models.auth.user import User
from models.bank.bank_card import BankCard
from models.bank.bank_account import BankAccount
from models.bank.loan import Loan, LoanPayment
from models.bank.credit_profile import CreditProfile
from models.bank.bank_task import BankTask, UserBankTask, TaskStatus
from models.finance.currency import Currency
from services.currency_service import CurrencyService
from dal.unit_of_work import UnitOfWork


class BankService:
    """银行服务类
    
    提供银行相关的核心业务功能，包括：
    - 银行卡管理
    - 账户管理
    - 存取款操作
    - 转账功能
    - 贷款管理
    - 银行任务管理
    """
    
    def __init__(self, uow: UnitOfWork, currency_service: CurrencyService):
        self.uow = uow
        self.currency_service = currency_service
    
    # ==================== 银行卡管理 ====================
    
    async def apply_bank_card(self, user_id: str, bank_code: str, 
                            card_type: str = 'debit') -> Tuple[bool, str, Optional[BankCard]]:
        """申请银行卡
        
        Args:
            user_id: 用户ID
            bank_code: 银行代码
            card_type: 卡片类型
            
        Returns:
            (是否成功, 消息, 银行卡对象)
        """
        try:
            async with self.uow:
                # 检查用户是否存在
                user = self.uow.query(User).filter_by(user_id=user_id).first()
                if not user:
                    return False, "用户不存在", None
                
                # 检查银行代码是否有效
                valid_banks = BankCard.get_available_banks()
                if bank_code.upper() not in valid_banks:
                    return False, f"无效的银行代码: {bank_code}", None
                
                # 检查用户是否已有该银行的卡片
                existing_card = self.uow.query(BankCard).filter_by(
                    user_id=user_id,
                    bank_code=bank_code.upper(),
                    is_active=True
                ).first()
                
                if existing_card:
                    return False, f"您已拥有{bank_code.upper()}银行的银行卡", None
                
                # 创建银行卡
                bank_card = BankCard(
                    user_id=user_id,
                    bank_code=bank_code.upper(),
                    card_type=card_type
                )
                
                self.uow.add(bank_card)
                await self.uow.commit()
                
                return True, f"成功申请{bank_code.upper()}银行卡", bank_card
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"申请银行卡失败: {str(e)}", None
    
    def get_user_bank_cards(self, user_id: str, active_only: bool = True) -> List[BankCard]:
        """获取用户的银行卡列表
        
        Args:
            user_id: 用户ID
            active_only: 是否只返回激活的卡片
            
        Returns:
            银行卡列表
        """
        try:
            query = self.uow.query(BankCard).filter_by(user_id=user_id)
            
            if active_only:
                query = query.filter_by(is_active=True)
            
            return query.order_by(BankCard.created_at.desc()).all()
            
        except Exception:
            return []
    
    # ==================== 账户管理 ====================
    
    async def create_bank_account(self, user_id: str, bank_card_id: str, 
                                currency_code: str = 'JCY', 
                                account_name: str = None) -> Tuple[bool, str, Optional[BankAccount]]:
        """创建银行账户
        
        Args:
            user_id: 用户ID
            bank_card_id: 银行卡ID
            currency_code: 货币代码
            account_name: 账户名称
            
        Returns:
            (是否成功, 消息, 银行账户对象)
        """
        try:
            async with self.uow:
                # 验证银行卡
                bank_card = self.uow.query(BankCard).filter_by(
                    card_id=bank_card_id,
                    user_id=user_id,
                    is_active=True
                ).first()
                
                if not bank_card:
                    return False, "银行卡不存在或未激活", None
                
                # 验证货币
                currency = self.uow.query(Currency).filter_by(code=currency_code).first()
                if not currency:
                    return False, f"不支持的货币: {currency_code}", None
                
                # 检查是否已有相同货币的账户
                existing_account = self.uow.query(BankAccount).filter_by(
                    user_id=user_id,
                    bank_card_id=bank_card_id,
                    currency_id=currency.currency_id
                ).first()
                
                if existing_account:
                    return False, f"已存在{currency_code}账户", None
                
                # 创建账户
                if not account_name:
                    account_name = f"{bank_card.get_bank_info()['name']}{currency_code}账户"
                
                bank_account = BankAccount(
                    user_id=user_id,
                    bank_card_id=bank_card_id,
                    currency_id=currency.currency_id,
                    account_name=account_name
                )
                
                self.uow.add(bank_account)
                
                # 如果是用户第一个账户，设为默认账户
                user_accounts = self.uow.query(BankAccount).filter_by(
                    user_id=user_id, is_enabled=True
                ).count()
                
                if user_accounts == 0:
                    bank_account.set_as_default(self.uow)
                
                await self.uow.commit()
                
                return True, f"成功创建{currency_code}账户", bank_account
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"创建账户失败: {str(e)}", None
    
    def get_user_accounts(self, user_id: str, currency_code: str = None) -> List[BankAccount]:
        """获取用户账户列表
        
        Args:
            user_id: 用户ID
            currency_code: 货币代码过滤
            
        Returns:
            账户列表
        """
        try:
            query = self.uow.query(BankAccount).filter_by(
                user_id=user_id, is_enabled=True
            )
            
            if currency_code:
                currency = self.uow.query(Currency).filter_by(code=currency_code).first()
                if currency:
                    query = query.filter_by(currency_id=currency.currency_id)
            
            return query.order_by(BankAccount.is_default.desc(), 
                                BankAccount.created_at.desc()).all()
            
        except Exception:
            return []
    
    # ==================== 存取款操作 ====================
    
    async def deposit(self, user_id: str, account_id: str, amount: Decimal, 
                    description: str = None) -> Tuple[bool, str]:
        """存款
        
        Args:
            user_id: 用户ID
            account_id: 账户ID
            amount: 存款金额
            description: 描述
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                # 验证账户
                account = self.uow.query(BankAccount).filter_by(
                    account_id=account_id,
                    user_id=user_id,
                    is_enabled=True
                ).first()
                
                if not account:
                    return False, "账户不存在或未启用"
                
                # 验证金额
                if amount <= 0:
                    return False, "存款金额必须大于0"
                
                # 执行存款
                success, message = account.deposit(amount, description or "存款")
                if not success:
                    return False, message
                
                # 记录交易
                await self._record_transaction(
                    user_id, account_id, 'deposit', amount, 
                    description or "存款"
                )
                
                await self.uow.commit()
                
                return True, f"成功存款 {amount} {account.currency.code}"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"存款失败: {str(e)}"
    
    async def withdraw(self, user_id: str, account_id: str, amount: Decimal, 
                     description: str = None) -> Tuple[bool, str]:
        """取款
        
        Args:
            user_id: 用户ID
            account_id: 账户ID
            amount: 取款金额
            description: 描述
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                # 验证账户
                account = self.uow.query(BankAccount).filter_by(
                    account_id=account_id,
                    user_id=user_id,
                    is_enabled=True
                ).first()
                
                if not account:
                    return False, "账户不存在或未启用"
                
                # 验证金额
                if amount <= 0:
                    return False, "取款金额必须大于0"
                
                # 检查余额
                if not account.can_withdraw(amount):
                    return False, f"余额不足，可用余额: {account.available_balance}"
                
                # 执行取款
                success, message = account.withdraw(amount, description or "取款")
                if not success:
                    return False, message
                
                # 记录交易
                await self._record_transaction(
                    user_id, account_id, 'withdraw', -amount, 
                    description or "取款"
                )
                
                await self.uow.commit()
                
                return True, f"成功取款 {amount} {account.currency.code}"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"取款失败: {str(e)}"
    
    # ==================== 转账功能 ====================
    
    async def transfer(self, from_user_id: str, from_account_id: str, 
                     to_user_id: str, to_account_id: str, amount: Decimal, 
                     description: str = None) -> Tuple[bool, str]:
        """转账
        
        Args:
            from_user_id: 转出用户ID
            from_account_id: 转出账户ID
            to_user_id: 转入用户ID
            to_account_id: 转入账户ID
            amount: 转账金额
            description: 描述
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                # 验证转出账户
                from_account = self.uow.query(BankAccount).filter_by(
                    account_id=from_account_id,
                    user_id=from_user_id,
                    is_enabled=True
                ).first()
                
                if not from_account:
                    return False, "转出账户不存在或未启用"
                
                # 验证转入账户
                to_account = self.uow.query(BankAccount).filter_by(
                    account_id=to_account_id,
                    user_id=to_user_id,
                    is_enabled=True
                ).first()
                
                if not to_account:
                    return False, "转入账户不存在或未启用"
                
                # 验证金额
                if amount <= 0:
                    return False, "转账金额必须大于0"
                
                # 检查余额
                if not from_account.can_withdraw(amount):
                    return False, f"余额不足，可用余额: {from_account.available_balance}"
                
                # 检查转账限额
                if not self._check_transfer_limit(from_account, amount):
                    return False, "超出转账限额"
                
                # 货币转换
                if from_account.currency_id != to_account.currency_id:
                    converted_amount = await self._convert_currency(
                        amount, from_account.currency.code, to_account.currency.code
                    )
                    if converted_amount is None:
                        return False, "货币转换失败"
                else:
                    converted_amount = amount
                
                # 执行转账
                # 转出
                success, message = from_account.withdraw(amount, f"转账给 {to_user_id}")
                if not success:
                    return False, message
                
                # 转入
                success, message = to_account.deposit(converted_amount, f"来自 {from_user_id} 的转账")
                if not success:
                    # 回滚转出操作
                    from_account.deposit(amount, "转账失败回滚")
                    return False, message
                
                # 记录交易
                await self._record_transaction(
                    from_user_id, from_account_id, 'transfer_out', -amount, 
                    description or f"转账给 {to_user_id}"
                )
                
                await self._record_transaction(
                    to_user_id, to_account_id, 'transfer_in', converted_amount, 
                    description or f"来自 {from_user_id} 的转账"
                )
                
                await self.uow.commit()
                
                return True, f"成功转账 {amount} {from_account.currency.code}"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"转账失败: {str(e)}"
    
    # ==================== 贷款管理 ====================
    
    async def apply_loan(self, user_id: str, loan_type: str, amount: Decimal, 
                       term_months: int, purpose: str = None) -> Tuple[bool, str, Optional[Loan]]:
        """申请贷款
        
        Args:
            user_id: 用户ID
            loan_type: 贷款类型
            amount: 贷款金额
            term_months: 贷款期限(月)
            purpose: 贷款用途
            
        Returns:
            (是否成功, 消息, 贷款对象)
        """
        try:
            async with self.uow:
                # 检查用户信用档案
                credit_profile = CreditProfile.get_or_create_profile(self.uow, user_id)
                
                # 评估贷款资格
                approval_probability = credit_profile.calculate_loan_approval_probability(
                    amount, loan_type
                )
                
                if approval_probability < 0.3:  # 30%以下拒绝
                    return False, "信用评分不足，贷款申请被拒绝", None
                
                # 计算利率
                interest_rate = credit_profile.suggest_interest_rate(loan_type, amount)
                
                # 创建贷款申请
                loan = Loan(
                    user_id=user_id,
                    loan_type=loan_type,
                    principal_amount=amount,
                    interest_rate=interest_rate,
                    term_months=term_months,
                    purpose=purpose or "个人用途"
                )
                
                self.uow.add(loan)
                
                # 如果概率高，自动批准
                if approval_probability > 0.8:  # 80%以上自动批准
                    success, message = loan.approve_loan("系统自动批准")
                    if success:
                        # 放款到用户默认账户
                        default_account = BankAccount.get_user_default_account(self.uow, user_id)
                        if default_account:
                            await self.deposit(user_id, default_account.account_id, amount, 
                                             f"贷款放款 - {loan.loan_number}")
                
                await self.uow.commit()
                
                status_msg = "已批准并放款" if loan.status == 'approved' else "申请已提交，等待审核"
                return True, f"贷款申请成功，{status_msg}", loan
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"贷款申请失败: {str(e)}", None
    
    async def repay_loan(self, user_id: str, loan_id: str, amount: Decimal, 
                       account_id: str = None) -> Tuple[bool, str]:
        """还款
        
        Args:
            user_id: 用户ID
            loan_id: 贷款ID
            amount: 还款金额
            account_id: 还款账户ID
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                # 验证贷款
                loan = self.uow.query(Loan).filter_by(
                    loan_id=loan_id,
                    user_id=user_id,
                    status='approved'
                ).first()
                
                if not loan:
                    return False, "贷款不存在或状态异常"
                
                # 获取还款账户
                if account_id:
                    account = self.uow.query(BankAccount).filter_by(
                        account_id=account_id,
                        user_id=user_id,
                        is_enabled=True
                    ).first()
                else:
                    account = BankAccount.get_user_default_account(self.uow, user_id)
                
                if not account:
                    return False, "还款账户不存在"
                
                # 检查余额
                if not account.can_withdraw(amount):
                    return False, f"账户余额不足，可用余额: {account.available_balance}"
                
                # 执行还款
                success, message = loan.make_payment(amount, 'bank_transfer')
                if not success:
                    return False, message
                
                # 从账户扣款
                success, message = account.withdraw(amount, f"贷款还款 - {loan.loan_number}")
                if not success:
                    return False, message
                
                # 记录交易
                await self._record_transaction(
                    user_id, account.account_id, 'loan_repayment', -amount, 
                    f"贷款还款 - {loan.loan_number}"
                )
                
                await self.uow.commit()
                
                return True, f"成功还款 {amount}，剩余欠款: {loan.remaining_balance}"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"还款失败: {str(e)}"
    
    def get_user_loans(self, user_id: str, status: str = None) -> List[Loan]:
        """获取用户贷款列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            
        Returns:
            贷款列表
        """
        try:
            query = self.uow.query(Loan).filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            return query.order_by(Loan.application_date.desc()).all()
            
        except Exception:
            return []
    
    # ==================== 银行任务管理 ====================
    
    def get_available_tasks(self, user_id: str = None, bank_code: str = None) -> List[BankTask]:
        """获取可用任务
        
        Args:
            user_id: 用户ID
            bank_code: 银行代码
            
        Returns:
            任务列表
        """
        return BankTask.get_available_tasks(self.uow, user_id, bank_code)
    
    async def accept_task(self, user_id: str, task_id: str) -> Tuple[bool, str, Optional[UserBankTask]]:
        """接取任务
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            
        Returns:
            (是否成功, 消息, 用户任务对象)
        """
        try:
            async with self.uow:
                task = self.uow.query(BankTask).filter_by(task_id=task_id).first()
                if not task:
                    return False, "任务不存在", None
                
                success, message, user_task = task.accept_task(user_id, self.uow)
                
                if success:
                    await self.uow.commit()
                
                return success, message, user_task
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"接取任务失败: {str(e)}", None
    
    async def submit_task(self, user_id: str, task_id: str, 
                        submission_data: Dict = None) -> Tuple[bool, str]:
        """提交任务
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            submission_data: 提交数据
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                task = self.uow.query(BankTask).filter_by(task_id=task_id).first()
                if not task:
                    return False, "任务不存在"
                
                success, message = task.complete_task(user_id, self.uow, submission_data)
                
                if success:
                    await self.uow.commit()
                
                return success, message
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"提交任务失败: {str(e)}"
    
    def get_user_tasks(self, user_id: str, status: str = None) -> List[UserBankTask]:
        """获取用户任务列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            
        Returns:
            用户任务列表
        """
        try:
            query = self.uow.query(UserBankTask).filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            return query.order_by(UserBankTask.created_at.desc()).all()
            
        except Exception:
            return []
    
    # ==================== 辅助方法 ====================
    
    async def _record_transaction(self, user_id: str, account_id: str, 
                                transaction_type: str, amount: Decimal, 
                                description: str):
        """记录交易
        
        Args:
            user_id: 用户ID
            account_id: 账户ID
            transaction_type: 交易类型
            amount: 金额
            description: 描述
        """
        # 这里可以实现交易记录功能
        # 暂时简化实现
        pass
    
    def _check_transfer_limit(self, account: BankAccount, amount: Decimal) -> bool:
        """检查转账限额
        
        Args:
            account: 账户对象
            amount: 转账金额
            
        Returns:
            是否在限额内
        """
        # 检查日限额
        if account.daily_transfer_limit and amount > account.daily_transfer_limit:
            return False
        
        # 检查月限额
        if account.monthly_transfer_limit and amount > account.monthly_transfer_limit:
            return False
        
        return True
    
    async def _convert_currency(self, amount: Decimal, from_code: str, 
                              to_code: str) -> Optional[Decimal]:
        """货币转换
        
        Args:
            amount: 金额
            from_code: 源货币代码
            to_code: 目标货币代码
            
        Returns:
            转换后的金额
        """
        try:
            return self.currency_service.convert_currency(amount, from_code, to_code)
        except Exception:
            return None
    
    def get_account_overview(self, user_id: str) -> Dict:
        """获取账户概览
        
        Args:
            user_id: 用户ID
            
        Returns:
            账户概览信息
        """
        try:
            # 获取银行卡
            bank_cards = self.get_user_bank_cards(user_id)
            
            # 获取账户
            accounts = self.get_user_accounts(user_id)
            
            # 获取贷款
            loans = self.get_user_loans(user_id, 'approved')
            
            # 计算总资产
            total_assets = sum(account.balance for account in accounts)
            
            # 计算总负债
            total_debt = sum(loan.remaining_balance for loan in loans)
            
            # 获取信用档案
            credit_profile = CreditProfile.get_or_create_profile(self.uow, user_id)
            
            return {
                'user_id': user_id,
                'bank_cards': [card.get_display_info() for card in bank_cards],
                'accounts': [account.get_account_summary() for account in accounts],
                'loans': [loan.get_loan_summary() for loan in loans],
                'total_assets': float(total_assets),
                'total_debt': float(total_debt),
                'net_worth': float(total_assets - total_debt),
                'credit_score': credit_profile.credit_score if credit_profile else 0,
                'account_count': len(accounts),
                'loan_count': len(loans)
            }
            
        except Exception:
            return {
                'user_id': user_id,
                'error': '获取账户概览失败'
            }