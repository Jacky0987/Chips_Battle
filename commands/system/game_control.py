# -*- coding: utf-8 -*-
"""
游戏控制命令

提供游戏基础控制功能，包括退出、版本信息、状态查看等。
"""

import time
import psutil
import platform
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from commands.base import Command, CommandResult, CommandContext
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel


class GameExitCommand(Command):
    """游戏退出命令（增强版）"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "quit"
    
    @property
    def aliases(self) -> List[str]:
        return ["exit", "stop", "shutdown"]
    
    @property
    def description(self) -> str:
        return "退出游戏"
    
    @property
    def category(self) -> str:
        return "游戏控制"
    
    @property
    def usage(self) -> str:
        return f"{self.name} [--force]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行退出命令"""
        try:
            force = "--force" in args or "-f" in args
            
            if not force:
                # 显示退出确认信息
                goodbye_text = Text("👋 感谢游玩！游戏即将退出...", style="cyan")
                self.console.print(goodbye_text)
            
            return CommandResult(
                success=True,
                message="游戏退出",
                action="quit"
            )
            
        except Exception as e:
            return self.format_error(f"退出失败: {str(e)}")


class VersionCommand(Command):
    """版本信息命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "version"
    
    @property
    def aliases(self) -> List[str]:
        return ["ver", "v"]
    
    @property
    def description(self) -> str:
        return "显示游戏版本信息"
    
    @property
    def category(self) -> str:
        return "游戏控制"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行版本查看命令"""
        try:
            # 从config.json读取版本信息
            config_path = Path("data/config.json")
            game_name = "Chips Battle"
            game_version = "v1.0.0-dev"
            game_subtitle = "命令驱动的金融模拟游戏"
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        game_info = config.get('game', {})
                        game_name = game_info.get('name', game_name)
                        game_version = game_info.get('version', game_version)
                        game_subtitle = game_info.get('subtitle', game_subtitle)
                except Exception as e:
                    # 如果读取配置失败，使用默认值
                    pass
            
            # 创建版本信息表格
            table = Table(title="🎮 游戏版本信息", show_header=True, header_style="bold magenta")
            table.add_column("项目", style="cyan", no_wrap=True)
            table.add_column("信息", style="white")
            
            # 添加版本信息
            table.add_row("游戏名称", game_name)
            table.add_row("版本号", game_version)
            table.add_row("游戏描述", game_subtitle)
            table.add_row("构建日期", "2024-01-15")
            table.add_row("Python版本", platform.python_version())
            table.add_row("系统平台", f"{platform.system()} {platform.release()}")
            table.add_row("架构", platform.machine())
            
            self.console.print(table)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"获取版本信息失败: {str(e)}")


class GameStatusCommand(Command):
    """游戏状态命令（增强版）"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.start_time = time.time()
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def aliases(self) -> List[str]:
        return ["stat", "info"]
    
    @property
    def description(self) -> str:
        return "显示游戏状态概览"
    
    @property
    def category(self) -> str:
        return "游戏控制"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行状态查看命令"""
        try:
            # 获取系统信息
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            # 创建状态信息面板
            status_table = Table(show_header=True, header_style="bold green")
            status_table.add_column("类别", style="cyan", no_wrap=True)
            status_table.add_column("状态", style="white")
            
            # 游戏基础信息
            current_time = datetime.now()
            if context.user:
                status_table.add_row("当前用户", str(context.user.username))
            
            if context.game_time:
                status_table.add_row("游戏时间", context.game_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            status_table.add_row("系统时间", current_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            # 运行时间
            uptime_seconds = time.time() - self.start_time
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            status_table.add_row("运行时间", uptime_str)
            
            # 系统资源
            memory_mb = memory_info.rss / 1024 / 1024
            status_table.add_row("内存使用", f"{memory_mb:.1f} MB")
            status_table.add_row("CPU使用率", f"{cpu_percent:.1f}%")
            
            # 服务状态（如果可用）
            if hasattr(context, 'registry') and context.registry:
                command_count = len(context.registry._commands)
                status_table.add_row("已注册命令", str(command_count))
            
            # 显示状态面板
            panel = Panel(status_table, title="🎮 游戏状态", border_style="green")
            self.console.print(panel)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"获取状态信息失败: {str(e)}")


class UptimeCommand(Command):
    """运行时间命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.start_time = time.time()
    
    @property
    def name(self) -> str:
        return "uptime"
    
    @property
    def aliases(self) -> List[str]:
        return ["runtime"]
    
    @property
    def description(self) -> str:
        return "显示游戏运行时间"
    
    @property
    def category(self) -> str:
        return "游戏控制"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行运行时间查看命令"""
        try:
            # 计算运行时间
            uptime_seconds = time.time() - self.start_time
            uptime_delta = timedelta(seconds=int(uptime_seconds))
            
            # 格式化显示
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_text = Text("⏱️ 游戏运行时间: ", style="bold cyan")
            
            if days > 0:
                uptime_text.append(f"{days}天 ", style="yellow")
            if hours > 0:
                uptime_text.append(f"{hours}小时 ", style="green")
            if minutes > 0:
                uptime_text.append(f"{minutes}分钟 ", style="blue")
            uptime_text.append(f"{seconds}秒", style="white")
            
            self.console.print(uptime_text)
            
            return CommandResult(
                success=True,
                message=f"运行时间: {uptime_delta}",
                data={"uptime_seconds": uptime_seconds}
            )
            
        except Exception as e:
            return self.format_error(f"获取运行时间失败: {str(e)}")