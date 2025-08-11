# -*- coding: utf-8 -*-
"""
状态命令

显示当前游戏状态和用户信息。
"""

from typing import List
from datetime import datetime
from commands.base import BasicCommand, CommandResult, CommandContext
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn


class StatusCommand(BasicCommand):
    """状态命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def aliases(self) -> List[str]:
        return ["stat", "info"]
    
    @property
    def description(self) -> str:
        return "显示当前游戏状态和用户信息"
    
    @property
    def usage(self) -> str:
        return "status"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行状态命令
        
        Args:
            args: 命令参数
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        try:
            # 获取用户信息
            user = context.user
            if not user:
                return self.error("无法获取用户信息")
            
            # 显示状态信息
            await self._display_status(user, context)
            
            return self.success("状态信息已显示")
            
        except Exception as e:
            return self.error(f"显示状态时发生错误: {str(e)}")
    
    async def _display_status(self, user, context: CommandContext):
        """显示状态信息
        
        Args:
            user: 用户对象
            context: 命令上下文
        """
        # 创建用户信息面板
        user_info = self._create_user_info_panel(user)
        
        # 创建游戏状态面板
        game_status = self._create_game_status_panel(context)
        
        # 创建财务状态面板
        finance_status = await self._create_finance_status_panel(user, context)
        
        # 创建统计信息面板
        stats_panel = self._create_stats_panel(user)
        
        # 显示所有面板
        self.console.print(user_info)
        self.console.print(Columns([game_status, finance_status]))
        self.console.print(stats_panel)
    
    def _create_user_info_panel(self, user) -> Panel:
        """创建用户信息面板
        
        Args:
            user: 用户对象
            
        Returns:
            用户信息面板
        """
        # 创建用户信息表格
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("属性", style="cyan", no_wrap=True)
        table.add_column("值", style="white")
        
        # 基本信息
        table.add_row("👤 用户名", user.username)
        table.add_row("📧 邮箱", user.email or "未设置")
        table.add_row("🏷️ 显示名", user.display_name or user.username)
        
        # 等级和经验
        level_text = Text()
        level_text.append(f"Lv.{user.level}", style="bold yellow")
        if user.level < 100:  # 假设最高等级是100
            exp_needed = (user.level + 1) * 1000 - user.experience  # 简单的经验计算
            level_text.append(f" (还需 {exp_needed} 经验升级)", style="dim")
        table.add_row("⭐ 等级", level_text)
        
        # 状态
        status_text = Text()
        if user.is_active:
            status_text.append("🟢 在线", style="green")
        else:
            status_text.append("🔴 离线", style="red")
        
        if user.is_verified:
            status_text.append(" ✅ 已验证", style="green")
        else:
            status_text.append(" ⚠️ 未验证", style="yellow")
        
        table.add_row("📊 状态", status_text)
        
        # 注册时间
        if hasattr(user, 'created_at') and user.created_at:
            reg_time = user.created_at.strftime("%Y-%m-%d %H:%M")
            table.add_row("📅 注册时间", reg_time)
        
        # 最后活动时间
        if hasattr(user, 'last_activity') and user.last_activity:
            last_activity = user.last_activity.strftime("%Y-%m-%d %H:%M")
            table.add_row("🕐 最后活动", last_activity)
        
        return Panel(
            table,
            title=f"👤 {user.username} 的个人信息",
            border_style="blue",
            padding=(1, 2)
        )
    
    def _create_game_status_panel(self, context: CommandContext) -> Panel:
        """创建游戏状态面板
        
        Args:
            context: 命令上下文
            
        Returns:
            游戏状态面板
        """
        table = Table(show_header=False, box=None)
        table.add_column("属性", style="cyan", no_wrap=True)
        table.add_column("值", style="white")
        
        # 当前时间
        from core.game_time import GameTime
        current_time = (GameTime.now() if GameTime.is_initialized() else datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        table.add_row("🕐 当前时间", current_time)
        
        # 游戏时间
        if GameTime.is_initialized():
            game_time = GameTime.now().strftime("%Y-%m-%d %H:%M:%S")
            table.add_row("🎮 游戏时间", game_time)
        else:
            table.add_row("🎮 游戏时间", "未初始化")
        
        # 服务器状态
        table.add_row("🖥️ 服务器", "🟢 正常运行")
        
        # 在线用户数（模拟数据）
        table.add_row("👥 在线用户", "1 人")
        
        # 会话时长
        if hasattr(context, 'session_start_time'):
            current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
            session_duration = current_time - context.session_start_time
            duration_str = str(session_duration).split('.')[0]  # 去掉微秒
            table.add_row("⏱️ 会话时长", duration_str)
        
        return Panel(
            table,
            title="🎮 游戏状态",
            border_style="green",
            padding=(1, 1)
        )
    
    async def _create_finance_status_panel(self, user, context: CommandContext) -> Panel:
        """创建财务状态面板
        
        Args:
            user: 用户对象
            context: 命令上下文
            
        Returns:
            财务状态面板
        """
        table = Table(show_header=False, box=None)
        table.add_column("货币", style="cyan", no_wrap=True)
        table.add_column("余额", style="white", justify="right")
        
        try:
            # 尝试从银行服务获取账户信息
            from services.bank_service import BankService
            from dal.unit_of_work import UnitOfWork
            from dal.database import get_session
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select
            from models.bank.bank_account import BankAccount
            
            async with get_session() as session:
                # 直接查询账户并加载currency关系
                result = await session.execute(
                    select(BankAccount)
                    .options(selectinload(BankAccount.currency))
                    .filter_by(user_id=user.user_id, is_active=True)
                    .order_by(BankAccount.is_default.desc(), BankAccount.created_at.desc())
                )
                accounts = result.scalars().all()
                
                if accounts:
                    total_jcy_value = 0
                    for account in accounts:
                        currency_code = account.currency.code if account.currency else 'UNKNOWN'
                        currency_symbol = {
                            'JCY': '💰',
                            'CNY': '💴', 
                            'USD': '💵',
                            'EUR': '💶'
                        }.get(currency_code, '💱')
                        
                        balance_str = f"{account.balance:,.2f}"
                        table.add_row(f"{currency_symbol} {currency_code}", balance_str)
                        
                        # 简单汇率转换到JCY（实际应该从汇率服务获取）
                        if currency_code == 'JCY':
                            total_jcy_value += account.balance
                        elif currency_code == 'CNY':
                            total_jcy_value += account.balance * 2  # 假设1CNY=2JCY
                        elif currency_code == 'USD':
                            total_jcy_value += account.balance * 10  # 假设1USD=10JCY
                        elif currency_code == 'EUR':
                            total_jcy_value += account.balance * 12  # 假设1EUR=12JCY
                    
                    # 添加总价值
                    if len(accounts) > 1:
                        table.add_row("", "")  # 空行
                        table.add_row(
                            Text("💎 总价值 (JCY)", style="bold yellow"),
                            Text(f"{total_jcy_value:,.2f}", style="bold yellow")
                        )
                else:
                    table.add_row("💰 JCY", "0.00")
                    table.add_row(Text("ℹ️ 提示", style="dim"), Text("请先申请银行卡", style="dim"))
                    
        except Exception as e:
            # 如果获取银行数据失败，显示默认信息
            table.add_row("💰 JCY", "--")
            table.add_row(Text("⚠️ 错误", style="red"), Text("无法获取财务数据", style="red"))
        
        return Panel(
            table,
            title="💰 财务状态",
            border_style="yellow",
            padding=(1, 1)
        )
    
    def _create_stats_panel(self, user) -> Panel:
        """创建统计信息面板
        
        Args:
            user: 用户对象
            
        Returns:
            统计信息面板
        """
        # 创建经验进度条
        current_level_exp = user.level * 1000  # 当前等级所需经验
        next_level_exp = (user.level + 1) * 1000  # 下一等级所需经验
        
        # 修复进度计算，避免负数和除零错误
        if next_level_exp > current_level_exp and user.experience >= current_level_exp:
            level_progress = (user.experience - current_level_exp) / (next_level_exp - current_level_exp) * 100
        else:
            level_progress = 0.0
        
        # 确保进度在0-100之间
        level_progress = max(0.0, min(100.0, level_progress))
        
        # 统计表格
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("统计项", style="cyan")
        stats_table.add_column("数值", style="white", justify="right")
        
        # 添加统计数据
        stats_table.add_row("🎯 总经验值", f"{user.experience:,}")
        stats_table.add_row("📊 命令执行次数", f"{getattr(user, 'command_count', 0):,}")
        stats_table.add_row("🔐 登录次数", f"{getattr(user, 'login_count', 0):,}")
        
        # 创建进度条
        progress_text = Text()
        progress_text.append(f"等级进度: {level_progress:.1f}%\n", style="white")
        
        # 简单的文本进度条
        bar_length = 20
        filled_length = int(bar_length * level_progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        progress_text.append(f"[{bar}] ", style="blue")
        progress_text.append(f"{user.experience - current_level_exp}/{next_level_exp - current_level_exp}", style="dim")
        
        # 组合内容
        content = Columns([stats_table, Panel(progress_text, border_style="dim")])
        
        return Panel(
            content,
            title="📈 统计信息",
            border_style="magenta",
            padding=(1, 1)
        )
    
    def validate_args(self, args: List[str]) -> bool:
        """验证命令参数
        
        Args:
            args: 命令参数
            
        Returns:
            是否有效
        """
        # status命令不需要参数
        return len(args) == 0
    
    def get_help(self) -> str:
        """获取命令帮助信息
        
        Returns:
            帮助信息字符串
        """
        return f"""
命令: {self.name}
别名: {', '.join(self.aliases)}
描述: {self.description}
用法: {self.usage}

显示内容:
  • 用户基本信息（用户名、邮箱、等级等）
  • 游戏状态（当前时间、服务器状态等）
  • 财务状态（各种货币余额）
  • 统计信息（经验值、命令执行次数等）

示例:
  status            # 显示完整状态信息

注意:
  该命令不需要任何参数，直接执行即可查看当前状态。
"""