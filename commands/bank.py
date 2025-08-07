from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
import asyncio

from models.auth.user import User
from models.bank.bank_card import BankCard
from models.bank.bank_account import BankAccount
from models.bank.loan import Loan
from models.bank.credit_profile import CreditProfile
from models.bank.bank_task import BankTask, UserBankTask
from services.bank_service import BankService
from services.credit_service import CreditService
from services.bank_task_service import BankTaskService
from services.currency_service import CurrencyService
from dal.unit_of_work import SqlAlchemyUnitOfWork, AbstractUnitOfWork
from dal.database import get_session
from utils.formatters import format_currency, format_table, format_list
from utils.validators import validate_amount, validate_positive_integer


class BankCommands:
    """银行命令类
    
    提供所有银行相关的命令功能，包括：
    - 银行卡管理
    - 账户操作
    - 存取款
    - 转账
    - 贷款
    - 银行任务
    """
    
    def __init__(self):
        self.sessionmaker = get_session
        self.uow = None
        self.currency_service = None
        self.bank_service = None
        self.credit_service = None
        self.task_service = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            from core.event_bus import EventBus
            
            # 创建一个临时的事件总线实例
            event_bus = EventBus()
            
            self.uow = SqlAlchemyUnitOfWork(self.sessionmaker)
            self.currency_service = CurrencyService(self.uow, event_bus)
            self.bank_service = BankService(self.uow, self.currency_service)
            self.credit_service = CreditService(self.uow)
            self.task_service = BankTaskService(self.uow)
            self._initialized = True
    
    # ==================== 主命令 ====================
    
    async def bank(self, user_id: str, args: List[str] = None) -> str:
        """银行主命令
        
        Args:
            user_id: 用户ID
            args: 命令参数
            
        Returns:
            命令执行结果
        """
        # 确保服务已初始化
        self._ensure_initialized()
        uow = SqlAlchemyUnitOfWork(self.sessionmaker)
        self.bank_service.uow = uow
        self.credit_service.uow = uow
        self.task_service.uow = uow
        self.currency_service.uow = uow

        async with uow:
            if not args:
                return await self._show_bank_overview(user_id)
            
            subcommand = args[0].lower()
            
            if subcommand == 'apply_card':
                return await self._apply_card(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'cards':
                return await self._show_cards(user_id)
            elif subcommand == 'deposit':
                return await self._deposit(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'withdraw':
                return await self._withdraw(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'transfer':
                return await self._transfer(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'loan':
                return await self._loan_menu(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'repay':
                return await self._repay_loan(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'credit':
                return await self._credit_info(user_id)
            elif subcommand == 'task':
                return await self._task_menu(user_id, args[1:] if len(args) > 1 else [])
            elif subcommand == 'help':
                return self._show_help()
            else:
                return f"未知的银行命令: {subcommand}\n使用 'bank help' 查看帮助"
    
    # ==================== 银行概览 ====================
    
    async def _show_bank_overview(self, user_id: str) -> str:
        """显示银行概览"""
        try:
            overview = await self.bank_service.get_account_overview(user_id)
            
            if 'error' in overview:
                return f"❌ 获取银行信息失败: {overview['error']}"
            
            result = []
            result.append("🏦 === 银行账户概览 ===")
            result.append("")
            
            # 资产概况
            result.append("💰 资产概况:")
            result.append(f"  总资产: {format_currency(overview['total_assets'], 'JCY')}")
            result.append(f"  总负债: {format_currency(overview['total_debt'], 'JCY')}")
            result.append(f"  净资产: {format_currency(overview['net_worth'], 'JCY')}")
            result.append(f"  信用分: {overview['credit_score']}")
            result.append("")
            
            # 银行卡信息
            if overview['bank_cards']:
                result.append("💳 银行卡:")
                for card in overview['bank_cards']:
                    status = "✅" if card['is_active'] else "❌"
                    result.append(f"  {status} {card['bank_name']} - {card['card_number']}")
            else:
                result.append("💳 银行卡: 暂无")
            result.append("")
            
            # 账户信息
            if overview['accounts']:
                result.append("🏛️ 银行账户:")
                for account in overview['accounts']:
                    default_mark = "⭐" if account['is_default'] else "  "
                    result.append(f"  {default_mark} {account['account_name']}: {format_currency(account['balance'], account['currency_code'])}")
            else:
                result.append("🏛️ 银行账户: 暂无")
            result.append("")
            
            # 贷款信息
            if overview['loans']:
                result.append("💸 贷款信息:")
                for loan in overview['loans']:
                    result.append(f"  {loan['loan_type']}: 剩余 {format_currency(loan['remaining_balance'], 'JCY')}")
            else:
                result.append("💸 贷款信息: 暂无")
            
            result.append("")
            result.append("💡 使用 'bank help' 查看所有银行命令")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取银行概览失败: {str(e)}"
    
    # ==================== 银行卡管理 ====================
    
    async def _apply_card(self, user_id: str, args: List[str]) -> str:
        """申请银行卡"""
        if not args:
            return self._show_available_banks()
        
        bank_code = args[0].upper()
        card_type = args[1] if len(args) > 1 else 'debit'
        
        try:
            success, message, card = await self.bank_service.apply_bank_card(
                user_id, bank_code, card_type
            )
            
            if success:
                return f"✅ {message}\n卡号: {card.get_masked_card_number()}"
            else:
                return f"❌ {message}"
                
        except Exception as e:
            return f"❌ 申请银行卡失败: {str(e)}"
    
    def _show_available_banks(self) -> str:
        """显示可用银行列表"""
        banks = BankCard.get_available_banks()
        
        result = []
        result.append("🏦 可申请的银行:")
        result.append("")
        
        for bank_info in banks:
            result.append(f"🏛️ {bank_info['code']} - {bank_info['name']}")
            result.append(f"   业务特色: {bank_info['focus']}")
            result.append("")
        
        result.append("💡 使用方法: bank apply_card <银行代码>")
        result.append("   例如: bank apply_card PSBJC")
        
        return "\n".join(result)
    
    async def _show_cards(self, user_id: str) -> str:
        """显示银行卡列表"""
        try:
            cards = await self.bank_service.get_user_bank_cards(user_id)
            
            if not cards:
                return "💳 您还没有银行卡\n使用 'bank apply_card' 申请银行卡"
            
            result = []
            result.append("💳 您的银行卡:")
            result.append("")
            
            for card in cards:
                info = card.get_display_info()
                status = "✅ 正常" if info['is_active'] else "❌ 停用"
                
                result.append(f"🏛️ {info['bank_name']}")
                result.append(f"   卡号: {info['card_number']}")
                result.append(f"   类型: {info['card_type']}")
                result.append(f"   状态: {status}")
                result.append(f"   开卡日期: {info['created_at']}")
                result.append("")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取银行卡信息失败: {str(e)}"
    
    # ==================== 存取款操作 ====================
    
    async def _deposit(self, user_id: str, args: List[str]) -> str:
        """存款到银行卡"""
        cards = await self.bank_service.get_user_bank_cards(user_id)
        if not cards:
            return "❌ 您还没有银行卡，无法存款。请先使用 `bank apply_card` 申请银行卡。"

        if not args or len(args) < 2:
            return await self._prompt_card_selection(user_id, "deposit", cards)

        try:
            card_index = int(args[0]) - 1
            if not (0 <= card_index < len(cards)):
                return "❌ 无效的卡片选择。"
            selected_card = cards[card_index]
        except ValueError:
            return "❌ 请输入有效的卡片序号。"

        try:
            amount = Decimal(args[1])
            if amount <= 0:
                return "❌ 存款金额必须大于0。"
        except (ValueError, TypeError):
            return "❌ 无效的金额格式。"

        description = " ".join(args[2:]) if len(args) > 2 else "存款"

        try:
            # Since BankAccount is tied to BankCard, we find the JCY account for that card
            jcy_account = await self.bank_service.get_account_by_card_and_currency(selected_card.card_id, 'JCY')
            if not jcy_account:
                return f"❌ 未找到卡号 {selected_card.card_number} 对应的JCY账户。"

            success, message = await self.bank_service.deposit(
                user_id, jcy_account.account_id, amount, description
            )

            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"

        except Exception as e:
            return f"❌ 存款失败: {str(e)}"
    
    async def _withdraw(self, user_id: str, args: List[str]) -> str:
        """从银行卡取款"""
        cards = await self.bank_service.get_user_bank_cards(user_id)
        if not cards:
            return "❌ 您还没有银行卡，无法取款。请先使用 `bank apply_card` 申请银行卡。"

        if not args or len(args) < 2:
            return await self._prompt_card_selection(user_id, "withdraw", cards)

        try:
            card_index = int(args[0]) - 1
            if not (0 <= card_index < len(cards)):
                return "❌ 无效的卡片选择。"
            selected_card = cards[card_index]
        except ValueError:
            return "❌ 请输入有效的卡片序号。"

        try:
            amount = Decimal(args[1])
            if amount <= 0:
                return "❌ 取款金额必须大于0。"
        except (ValueError, TypeError):
            return "❌ 无效的金额格式。"

        description = " ".join(args[2:]) if len(args) > 2 else "取款"

        try:
            jcy_account = await self.bank_service.get_account_by_card_and_currency(selected_card.card_id, 'JCY')
            if not jcy_account:
                return f"❌ 未找到卡号 {selected_card.card_number} 对应的JCY账户。"

            success, message = await self.bank_service.withdraw(
                user_id, jcy_account.account_id, amount, description
            )

            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"

        except Exception as e:
            return f"❌ 取款失败: {str(e)}"
    
    async def _prompt_card_selection(self, user_id: str, action: str, cards: List[BankCard]) -> str:
        """提示用户选择银行卡"""
        result = []
        result.append(f"请选择要{action}的银行卡 (输入序号):\n")
        
        for i, card in enumerate(cards):
            info = card.get_display_info()
            # We need to get the balance from the associated JCY account
            jcy_account = await self.bank_service.get_account_by_card_and_currency(card.card_id, 'JCY')
            balance_str = "查询中..." # Default text
            if jcy_account:
                balance_str = format_currency(jcy_account.balance, 'JCY')

            result.append(f"  [{i+1}] {info['bank_name']} ({info['card_number']}) - 余额: {balance_str}")
        
        result.append(f"\n用法: bank {action} <卡片序号> <金额> [描述]")
        return "\n".join(result)
    
    # ==================== 转账功能 ====================
    
    async def _transfer(self, user_id: str, args: List[str]) -> str:
        """转账"""
        if len(args) < 4:
            return "❌ 用法: bank transfer <转出账户ID> <转入用户ID> <转入账户ID> <金额> [描述]"
        
        from_account_id = args[0]
        to_user_id = args[1]
        to_account_id = args[2]
        
        try:
            amount = Decimal(args[3])
            if amount <= 0:
                return "❌ 转账金额必须大于0"
        except (ValueError, TypeError):
            return "❌ 无效的金额格式"
        
        description = " ".join(args[4:]) if len(args) > 4 else None
        
        try:
            success, message = await self.bank_service.transfer(
                user_id, from_account_id, to_user_id, to_account_id, amount, description
            )
            
            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
                
        except Exception as e:
            return f"❌ 转账失败: {str(e)}"
    
    # ==================== 贷款管理 ====================
    
    async def _loan_menu(self, user_id: str, args: List[str]) -> str:
        """贷款菜单"""
        if not args:
            return await self._show_loan_info(user_id)
        
        subcommand = args[0].lower()
        
        if subcommand == 'apply':
            return await self._apply_loan(user_id, args[1:])
        elif subcommand == 'list':
            return await self._list_loans(user_id)
        elif subcommand == 'info':
            return await self._loan_detail(user_id, args[1:] if len(args) > 1 else [])
        else:
            return await self._show_loan_info(user_id)
    
    async def _show_loan_info(self, user_id: str) -> str:
        """显示贷款信息"""
        try:
            loans = self.bank_service.get_user_loans(user_id)
            credit_profile = self.credit_service.get_or_create_credit_profile(user_id)
            
            result = []
            result.append("💸 贷款信息:")
            result.append("")
            
            # 信用信息
            result.append(f"📊 信用分数: {credit_profile.credit_score}")
            result.append(f"📈 信用等级: {credit_profile.credit_grade.value}")
            result.append("")
            
            # 当前贷款
            active_loans = [loan for loan in loans if loan.status == 'approved']
            if active_loans:
                result.append("🏦 当前贷款:")
                for loan in active_loans:
                    summary = loan.get_loan_summary()
                    result.append(f"  📋 {summary['loan_number']} ({summary['loan_type']})")
                    result.append(f"     剩余: {format_currency(summary['remaining_balance'], 'JCY')}")
                    result.append(f"     月还款: {format_currency(summary['monthly_payment'], 'JCY')}")
                result.append("")
            
            # 贷款历史
            if loans:
                result.append(f"📈 贷款历史: 共 {len(loans)} 笔")
                completed_loans = len([loan for loan in loans if loan.status == 'completed'])
                result.append(f"   已完成: {completed_loans} 笔")
            else:
                result.append("📈 贷款历史: 暂无")
            
            result.append("")
            result.append("💡 命令:")
            result.append("   bank loan apply - 申请贷款")
            result.append("   bank loan list - 查看贷款列表")
            result.append("   bank repay <贷款ID> <金额> - 还款")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取贷款信息失败: {str(e)}"
    
    async def _apply_loan(self, user_id: str, args: List[str]) -> str:
        """申请贷款"""
        if len(args) < 3:
            return "❌ 用法: bank loan apply <贷款类型> <金额> <期限(月)> [用途]"
        
        loan_type = args[0]
        
        try:
            amount = Decimal(args[1])
            if amount <= 0:
                return "❌ 贷款金额必须大于0"
        except (ValueError, TypeError):
            return "❌ 无效的金额格式"
        
        try:
            term_months = int(args[2])
            if term_months <= 0:
                return "❌ 贷款期限必须大于0"
        except (ValueError, TypeError):
            return "❌ 无效的期限格式"
        
        purpose = " ".join(args[3:]) if len(args) > 3 else None
        
        try:
            # 先评估贷款资格
            evaluation = self.credit_service.evaluate_loan_eligibility(
                user_id, amount, loan_type
            )
            
            if 'error' in evaluation:
                return f"❌ 贷款评估失败: {evaluation['error']}"
            
            # 显示评估结果
            result = []
            result.append("📊 贷款资格评估:")
            result.append(f"   批准概率: {evaluation['approval_probability']:.1%}")
            result.append(f"   建议利率: {evaluation['suggested_interest_rate']:.2%}")
            result.append(f"   风险等级: {evaluation['risk_level']}")
            result.append(f"   评估建议: {evaluation['recommendation']}")
            result.append("")
            
            if evaluation['approval_probability'] < 0.3:
                result.append("❌ 贷款申请被拒绝，建议提升信用分后再试")
                return "\n".join(result)
            
            # 申请贷款
            success, message, loan = await self.bank_service.apply_loan(
                user_id, loan_type, amount, term_months, purpose
            )
            
            if success:
                result.append(f"✅ {message}")
                if loan:
                    summary = loan.get_loan_summary()
                    result.append(f"   贷款编号: {summary['loan_number']}")
                    result.append(f"   月还款额: {format_currency(summary['monthly_payment'], 'JCY')}")
            else:
                result.append(f"❌ {message}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 申请贷款失败: {str(e)}"
    
    async def _list_loans(self, user_id: str) -> str:
        """列出贷款"""
        try:
            loans = self.bank_service.get_user_loans(user_id)
            
            if not loans:
                return "💸 您还没有贷款记录"
            
            result = []
            result.append("💸 贷款列表:")
            result.append("")
            
            for loan in loans:
                summary = loan.get_loan_summary()
                status_emoji = {
                    'pending': '⏳',
                    'approved': '✅',
                    'rejected': '❌',
                    'completed': '✅'
                }.get(summary['status'], '❓')
                
                result.append(f"{status_emoji} {summary['loan_number']} ({summary['loan_type']})")
                result.append(f"   金额: {format_currency(summary['principal_amount'], 'JCY')}")
                result.append(f"   剩余: {format_currency(summary['remaining_balance'], 'JCY')}")
                result.append(f"   利率: {summary['interest_rate']:.2%}")
                result.append(f"   状态: {summary['status']}")
                result.append(f"   申请日期: {summary['application_date']}")
                result.append("")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取贷款列表失败: {str(e)}"
    
    async def _repay_loan(self, user_id: str, args: List[str]) -> str:
        """还款"""
        if len(args) < 2:
            return "❌ 用法: bank repay <贷款ID> <金额> [账户ID]"
        
        loan_id = args[0]
        
        try:
            amount = Decimal(args[1])
            if amount <= 0:
                return "❌ 还款金额必须大于0"
        except (ValueError, TypeError):
            return "❌ 无效的金额格式"
        
        account_id = args[2] if len(args) > 2 else None
        
        try:
            success, message = await self.bank_service.repay_loan(
                user_id, loan_id, amount, account_id
            )
            
            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
                
        except Exception as e:
            return f"❌ 还款失败: {str(e)}"
    
    # ==================== 信用信息 ====================
    
    async def _credit_info(self, user_id: str) -> str:
        """显示信用信息"""
        try:
            # 重新计算信用分数
            success, message, new_score = await self.credit_service.recalculate_credit_score(user_id)
            
            if not success:
                return f"❌ 获取信用信息失败: {message}"
            
            # 生成信用报告
            report = self.credit_service.generate_credit_report(user_id)
            
            if 'error' in report:
                return f"❌ 生成信用报告失败: {report['error']}"
            
            result = []
            result.append("📊 信用档案:")
            result.append("")
            
            # 信用概况
            credit_summary = report['credit_summary']
            result.append(f"🎯 信用分数: {credit_summary['credit_score']}")
            result.append(f"📈 信用等级: {credit_summary['credit_grade']}")
            result.append(f"📅 更新日期: {credit_summary['last_updated']}")
            result.append("")
            
            # 账户概况
            account_summary = report['account_summary']
            result.append("🏛️ 账户概况:")
            result.append(f"   总账户数: {account_summary['total_accounts']}")
            result.append(f"   活跃账户: {account_summary['active_accounts']}")
            result.append(f"   总余额: {format_currency(account_summary['total_balance'], 'JCY')}")
            result.append("")
            
            # 贷款概况
            loan_summary = report['loan_summary']
            result.append("💸 贷款概况:")
            result.append(f"   总贷款数: {loan_summary['total_loans']}")
            result.append(f"   活跃贷款: {loan_summary['active_loans']}")
            result.append(f"   总负债: {format_currency(loan_summary['total_debt'], 'JCY')}")
            result.append("")
            
            # 改进建议
            suggestions = report['improvement_suggestions']
            if suggestions:
                result.append("💡 改进建议:")
                for suggestion in suggestions[:3]:  # 只显示前3个建议
                    result.append(f"   • {suggestion['suggestion']}")
                    result.append(f"     预期提升: {suggestion['expected_improvement']}分")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取信用信息失败: {str(e)}"
    
    # ==================== 银行任务 ====================
    
    async def _task_menu(self, user_id: str, args: List[str]) -> str:
        """银行任务菜单"""
        if not args:
            return await self._show_task_overview(user_id)
        
        subcommand = args[0].lower()
        
        if subcommand == 'list':
            return await self._list_available_tasks(user_id, args[1:] if len(args) > 1 else [])
        elif subcommand == 'accept':
            return await self._accept_task(user_id, args[1:] if len(args) > 1 else [])
        elif subcommand == 'submit':
            return await self._submit_task(user_id, args[1:] if len(args) > 1 else [])
        elif subcommand == 'my':
            return await self._show_my_tasks(user_id)
        elif subcommand == 'recommend':
            return await self._show_recommended_tasks(user_id)
        else:
            return await self._show_task_overview(user_id)
    
    async def _show_task_overview(self, user_id: str) -> str:
        """显示任务概览"""
        try:
            # 获取用户任务统计
            my_tasks = await self.task_service.get_user_task_history(user_id, limit=100)
            
            completed_count = len([t for t in my_tasks if t['status'] == 'completed'])
            in_progress_count = len([t for t in my_tasks if t['status'] in ['accepted', 'in_progress']])
            
            # 获取可用任务数量
            available_tasks = await self.task_service.get_available_tasks_for_user(user_id, limit=100)
            
            result = []
            result.append("🎯 银行任务中心:")
            result.append("")
            
            result.append("📊 任务统计:")
            result.append(f"   可接取任务: {len(available_tasks)} 个")
            result.append(f"   进行中任务: {in_progress_count} 个")
            result.append(f"   已完成任务: {completed_count} 个")
            result.append("")
            
            # 推荐任务
            recommended = self.task_service.get_recommended_tasks(user_id, limit=3)
            if recommended:
                result.append("⭐ 推荐任务:")
                for task in recommended:
                    result.append(f"   🎯 {task['title']}")
                    result.append(f"      奖励: {format_currency(task['reward_amount'], task['reward_currency'])}")
                    result.append(f"      推荐理由: {task['recommendation_reason']}")
                result.append("")
            
            result.append("💡 命令:")
            result.append("   bank task list - 查看所有可用任务")
            result.append("   bank task recommend - 查看推荐任务")
            result.append("   bank task my - 查看我的任务")
            result.append("   bank task accept <任务ID> - 接取任务")
            result.append("   bank task submit <任务ID> - 提交任务")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取任务概览失败: {str(e)}"
    
    async def _list_available_tasks(self, user_id: str, args: List[str]) -> str:
        """列出可用任务"""
        try:
            bank_code = args[0].upper() if args else None
            
            tasks = self.task_service.get_available_tasks_for_user(
                user_id, bank_code=bank_code, limit=20
            )
            
            if not tasks:
                filter_msg = f"({bank_code}银行)" if bank_code else ""
                return f"🎯 暂无可用任务{filter_msg}"
            
            result = []
            result.append(f"🎯 可用任务 ({len(tasks)}个):")
            result.append("")
            
            for task in tasks:
                difficulty_emoji = {
                    'easy': '🟢',
                    'medium': '🟡',
                    'hard': '🔴',
                    'expert': '🟣'
                }.get(task['difficulty'], '⚪')
                
                result.append(f"{difficulty_emoji} {task['title']}")
                result.append(f"   ID: {task['task_id'][:8]}...")
                result.append(f"   银行: {task['bank_code']}")
                result.append(f"   奖励: {format_currency(task['reward_amount'], task['reward_currency'])}")
                if task['credit_score_bonus'] > 0:
                    result.append(f"   信用分奖励: +{task['credit_score_bonus']}")
                result.append(f"   参与人数: {task['current_participants']}/{task['max_participants'] or '∞'}")
                result.append("")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取任务列表失败: {str(e)}"
    
    async def _accept_task(self, user_id: str, args: List[str]) -> str:
        """接取任务"""
        if not args:
            return "❌ 用法: bank task accept <任务ID>"
        
        task_id = args[0]
        
        try:
            success, message, user_task = await self.task_service.accept_task(user_id, task_id)
            
            if success:
                return f"✅ {message}\n任务ID: {user_task.user_task_id[:8]}..."
            else:
                return f"❌ {message}"
                
        except Exception as e:
            return f"❌ 接取任务失败: {str(e)}"
    
    async def _submit_task(self, user_id: str, args: List[str]) -> str:
        """提交任务"""
        if not args:
            return "❌ 用法: bank task submit <任务ID> [提交数据]"
        
        task_id = args[0]
        submission_data = {}
        
        # 简化的提交数据处理
        if len(args) > 1:
            submission_data['notes'] = " ".join(args[1:])
        
        try:
            success, message = await self.task_service.submit_task(
                user_id, task_id, submission_data
            )
            
            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
                
        except Exception as e:
            return f"❌ 提交任务失败: {str(e)}"
    
    async def _show_my_tasks(self, user_id: str) -> str:
        """显示我的任务"""
        try:
            tasks = await self.task_service.get_user_task_history(user_id, limit=20)
            
            if not tasks:
                return "🎯 您还没有接取任何任务"
            
            result = []
            result.append(f"🎯 我的任务 ({len(tasks)}个):")
            result.append("")
            
            for task in tasks:
                status_emoji = {
                    'accepted': '📝',
                    'in_progress': '⏳',
                    'submitted': '📤',
                    'completed': '✅',
                    'rejected': '❌',
                    'expired': '⏰'
                }.get(task['status'], '❓')
                
                task_info = task.get('task_info', {})
                
                result.append(f"{status_emoji} {task_info.get('title', '未知任务')}")
                result.append(f"   状态: {task['status']}")
                result.append(f"   进度: {task['progress']:.1f}%")
                result.append(f"   接取时间: {task['accepted_at']}")
                if task['completed_at']:
                    result.append(f"   完成时间: {task['completed_at']}")
                result.append("")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取我的任务失败: {str(e)}"
    
    async def _show_recommended_tasks(self, user_id: str) -> str:
        """显示推荐任务"""
        try:
            tasks = self.task_service.get_recommended_tasks(user_id, limit=10)
            
            if not tasks:
                return "⭐ 暂无推荐任务"
            
            result = []
            result.append(f"⭐ 推荐任务 ({len(tasks)}个):")
            result.append("")
            
            for task in tasks:
                difficulty_emoji = {
                    'easy': '🟢',
                    'medium': '🟡',
                    'hard': '🔴',
                    'expert': '🟣'
                }.get(task['difficulty'], '⚪')
                
                result.append(f"{difficulty_emoji} {task['title']}")
                result.append(f"   ID: {task['task_id'][:8]}...")
                result.append(f"   推荐分数: {task['recommendation_score']:.1f}")
                result.append(f"   推荐理由: {task['recommendation_reason']}")
                result.append(f"   奖励: {format_currency(task['reward_amount'], task['reward_currency'])}")
                result.append("")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ 获取推荐任务失败: {str(e)}"
    
    # ==================== 帮助信息 ====================
    
    def _show_help(self) -> str:
        """显示帮助信息"""
        return """🏦 银行系统帮助:

📋 基本命令:
  bank                    - 显示银行概览
  bank help              - 显示此帮助信息

💳 银行卡管理:
  bank apply_card        - 查看可申请的银行
  bank apply_card <银行>  - 申请指定银行的银行卡
  bank cards             - 查看我的银行卡

🏛️ 账户管理:
  bank accounts          - 查看我的银行账户

💰 存取款:
  bank deposit <账户ID> <金额> [描述]    - 存款
  bank withdraw <账户ID> <金额> [描述]   - 取款
  bank transfer <转出账户> <转入用户> <转入账户> <金额> [描述] - 转账

💸 贷款管理:
  bank loan              - 查看贷款信息
  bank loan apply <类型> <金额> <期限> [用途] - 申请贷款
  bank loan list         - 查看贷款列表
  bank repay <贷款ID> <金额> [账户ID]    - 还款

📊 信用管理:
  bank credit            - 查看信用档案

🎯 银行任务:
  bank task              - 任务中心概览
  bank task list [银行]   - 查看可用任务
  bank task recommend    - 查看推荐任务
  bank task my           - 查看我的任务
  bank task accept <任务ID> - 接取任务
  bank task submit <任务ID> - 提交任务

💡 提示:
  - 使用银行卡前需要先申请
  - 建议从邮政储蓄银行(PSBJC)开始
  - 完成银行任务可以获得奖励和信用分"""


# 全局银行命令实例
bank_commands = BankCommands()


# 命令注册函数
async def handle_bank_command(user_id: str, args: List[str]) -> str:
    """处理银行命令
    
    Args:
        user_id: 用户ID
        args: 命令参数
        
    Returns:
        命令执行结果
    """
    return await bank_commands.bank(user_id, args)