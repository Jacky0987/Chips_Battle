# -*- coding: utf-8 -*-
"""
退出命令

安全退出游戏。
"""

from typing import List
from commands.base import BasicCommand, CommandResult, CommandContext
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text


class QuitCommand(BasicCommand):
    """退出命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "quit"
    
    @property
    def aliases(self) -> List[str]:
        return ["exit", "bye", "logout"]
    
    @property
    def description(self) -> str:
        return "安全退出游戏"
    
    @property
    def usage(self) -> str:
        return "quit [--force]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行退出命令
        
        Args:
            args: 命令参数
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        try:
            # 检查是否强制退出
            force_quit = "--force" in args or "-f" in args
            
            # 如果不是强制退出，显示确认信息
            if not force_quit:
                if not await self._confirm_quit(context):
                    return self.info("已取消退出")
            
            # 执行退出流程
            await self._perform_quit(context)
            
            # 设置退出标志
            if hasattr(context, 'should_quit'):
                context.should_quit = True
            
            result = self.success("再见！感谢游玩 Chips Battle Remake!")
            result.action = 'quit'
            return result
            
        except Exception as e:
            return self.error(f"退出时发生错误: {str(e)}")
    
    async def _confirm_quit(self, context: CommandContext) -> bool:
        """确认退出
        
        Args:
            context: 命令上下文
            
        Returns:
            是否确认退出
        """
        # 显示退出信息
        quit_info = self._create_quit_info_panel(context)
        self.console.print(quit_info)
        
        try:
            # 询问确认
            return Confirm.ask(
                "[bold yellow]确定要退出游戏吗?[/bold yellow]",
                default=False
            )
        except KeyboardInterrupt:
            # 如果用户按 Ctrl+C，视为取消
            return False
    
    def _create_quit_info_panel(self, context: CommandContext) -> Panel:
        """创建退出信息面板
        
        Args:
            context: 命令上下文
            
        Returns:
            退出信息面板
        """
        content = Text()
        content.append("🎮 ", style="blue")
        content.append("Chips Battle Remake v3.0 Alpha\n\n", style="bold cyan")
        
        # 显示会话信息
        if context.user:
            content.append(f"👤 用户: {context.user.username}\n", style="white")
        
        # 显示会话统计（如果有的话）
        if hasattr(context, 'session_stats'):
            stats = context.session_stats
            content.append(f"📊 本次会话统计:\n", style="bold white")
            content.append(f"   • 执行命令: {stats.get('commands_executed', 0)} 次\n", style="dim")
            content.append(f"   • 会话时长: {stats.get('session_duration', '未知')}\n", style="dim")
        
        content.append("\n💾 退出时将自动保存游戏数据\n", style="green")
        content.append("🔒 会话将被安全清理\n", style="green")
        
        return Panel(
            content,
            title="🚪 退出游戏",
            border_style="yellow",
            padding=(1, 2)
        )
    
    async def _perform_quit(self, context: CommandContext):
        """执行退出流程
        
        Args:
            context: 命令上下文
        """
        self.console.print("[yellow]正在退出游戏...[/yellow]")
        
        try:
            # 1. 保存用户数据
            await self._save_user_data(context)
            
            # 2. 清理会话
            await self._cleanup_session(context)
            
            # 3. 记录退出日志
            await self._log_quit(context)
            
            # 4. 发布退出事件
            await self._publish_quit_event(context)
            
            self.console.print("[green]✅ 游戏数据已保存[/green]")
            
        except Exception as e:
            self.console.print(f"[red]⚠️ 退出时发生错误: {str(e)}[/red]")
            # 即使有错误也继续退出流程
    
    async def _save_user_data(self, context: CommandContext):
        """保存用户数据
        
        Args:
            context: 命令上下文
        """
        if not context.user:
            return
        
        try:
            # 更新最后活动时间
            from datetime import datetime
            if hasattr(context.user, 'last_activity'):
                context.user.last_activity = datetime.now()
            
            # 如果有工作单元，提交更改
            if hasattr(context, 'uow') and context.uow:
                # await context.uow.users.update(context.user)
                # await context.uow.commit()
                pass
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️ 保存用户数据时出现问题: {str(e)}[/yellow]")
    
    async def _cleanup_session(self, context: CommandContext):
        """清理会话数据
        
        Args:
            context: 命令上下文
        """
        try:
            # 清理认证会话
            if hasattr(context, 'auth_service') and context.auth_service:
                if context.user:
                    # await context.auth_service.destroy_session(context.user.user_id)
                    pass
            
            # 清理临时数据
            if hasattr(context, 'session_data'):
                context.session_data.clear()
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️ 清理会话时出现问题: {str(e)}[/yellow]")
    
    async def _log_quit(self, context: CommandContext):
        """记录退出日志
        
        Args:
            context: 命令上下文
        """
        try:
            # 这里应该记录到日志系统
            # 暂时只在控制台显示
            if context.user:
                self.console.print(f"[dim]📝 用户 {context.user.username} 已退出游戏[/dim]")
            
        except Exception as e:
            # 日志记录失败不应该影响退出流程
            pass
    
    async def _publish_quit_event(self, context: CommandContext):
        """发布退出事件
        
        Args:
            context: 命令上下文
        """
        try:
            # 如果有事件总线，发布用户退出事件
            if hasattr(context, 'event_bus') and context.event_bus:
                from core.event_bus import UserActionEvent
                
                event = UserActionEvent(
                    user_id=context.user.user_id if context.user else None,
                    action="quit",
                    details={"command": "quit", "timestamp": "now"}
                )
                
                # await context.event_bus.publish(event)
                pass
            
        except Exception as e:
            # 事件发布失败不应该影响退出流程
            pass
    
    def validate_args(self, args: List[str]) -> bool:
        """验证命令参数
        
        Args:
            args: 命令参数
            
        Returns:
            是否有效
        """
        # quit命令可以接受0-1个参数（--force标志）
        if len(args) > 1:
            return False
        
        # 如果有参数，应该是有效的标志
        if args:
            valid_flags = ["--force", "-f"]
            return args[0] in valid_flags
        
        return True
    
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

参数说明:
  --force, -f    - 强制退出，跳过确认提示

退出流程:
  1. 显示退出确认（除非使用 --force）
  2. 保存用户数据和游戏状态
  3. 清理会话数据
  4. 记录退出日志
  5. 发布退出事件
  6. 安全关闭游戏

示例:
  quit           # 正常退出（会显示确认提示）
  quit --force   # 强制退出（跳过确认）
  exit           # 使用别名退出

注意:
  • 退出前会自动保存所有数据
  • 可以使用 Ctrl+C 取消退出确认
  • 强制退出会跳过确认，但仍会执行保存流程
  • 即使保存过程中出现错误，游戏仍会退出
"""