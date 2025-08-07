#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha
主程序入口

这是一个命令驱动的金融模拟游戏，玩家通过命令行界面与游戏世界交互。
核心特性：
- 命令驱动交互
- 模块化设计
- 事件驱动架构
- 多币种金融系统
- 动态股票市场
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from core.event_bus import EventBus
from dal.database import DatabaseEngine, set_global_engine
from dal.unit_of_work import SqlAlchemyUnitOfWork
from services.time_service import TimeService
from services.command_dispatcher import CommandDispatcher
from services.auth_service import AuthService, AuthResult
from services.app_service import AppService
from services.news_service import NewsService
from services.currency_service import CurrencyService
from commands.registry import CommandRegistry
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory


class ChipsBattleGame:
    """游戏主类，负责初始化和运行游戏"""
    
    def __init__(self):
        self.console = Console()
        self.settings = Settings()
        self.event_bus = EventBus()
        self.db_engine = None
        self.uow = None
        self.time_service = None
        self.auth_service = None
        self.app_service = None
        self.news_service = None
        self.currency_service = None
        self.command_dispatcher = None
        self.current_user = None
        self.running = True
        self.session = PromptSession(history=FileHistory(os.path.expanduser('~/.chips_battle_history')))
        
    async def initialize(self):
        """初始化游戏系统"""
        try:
            # 显示启动画面
            self._show_startup_banner()
            
            # 初始化数据库
            self.console.print("[yellow]正在初始化数据库...[/yellow]")
            self.db_engine = DatabaseEngine(self.settings)
            await self.db_engine.initialize()
            
            # 设置全局数据库引擎
            set_global_engine(self.db_engine)
            
            # 初始化工作单元
            self.uow = SqlAlchemyUnitOfWork(self.db_engine.sessionmaker)
            
            # 初始化服务
            self.console.print("[yellow]正在启动核心服务...[/yellow]")
            self.time_service = TimeService(self.event_bus)
            self.currency_service = CurrencyService(self.uow, self.event_bus)
            self.auth_service = AuthService(self.uow, self.event_bus)
            self.app_service = AppService(self.uow, self.event_bus, self.currency_service)
            self.news_service = NewsService(self.event_bus, self.time_service)
            
            # 初始化命令系统
            self.console.print("[yellow]正在加载命令系统...[/yellow]")
            command_registry = CommandRegistry(
                auth_service=self.auth_service,
                app_service=self.app_service,
                news_service=self.news_service
            )
            await command_registry.discover_commands()
            self.command_dispatcher = CommandDispatcher(
                command_registry, 
                self.auth_service,
                self.event_bus,
                self.console
            )
            
            # 启动时间服务
            self.time_service.start()
            
            self.console.print("[green]✓ 游戏系统初始化完成![/green]")
            
        except Exception as e:
            self.console.print(f"[red]初始化失败: {e}[/red]")
            raise
    
    def _show_startup_banner(self):
        """显示启动横幅"""
        banner_text = Text()
        banner_text.append("\n")
        banner_text.append("  ██████╗██╗  ██╗██╗██████╗ ███████╗\n", style="bold cyan")
        banner_text.append(" ██╔════╝██║  ██║██║██╔══██╗██╔════╝\n", style="bold cyan")
        banner_text.append(" ██║     ███████║██║██████╔╝███████╗\n", style="bold cyan")
        banner_text.append(" ██║     ██╔══██║██║██╔═══╝ ╚════██║\n", style="bold cyan")
        banner_text.append(" ╚██████╗██║  ██║██║██║     ███████║\n", style="bold cyan")
        banner_text.append("  ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝\n", style="bold cyan")
        banner_text.append("\n")
        banner_text.append("    BATTLE REMAKE v3.0 Alpha\n", style="bold yellow")
        banner_text.append("    命令驱动的金融模拟游戏\n", style="dim")
        banner_text.append("\n")
        
        panel = Panel(
            banner_text,
            title="[bold green]欢迎来到 Chips Battle[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    async def run(self):
        """运行游戏主循环"""
        try:
            await self.initialize()
            
            # 用户登录
            await self._handle_login()
            
            # 主游戏循环
            await self._main_loop()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]游戏被用户中断[/yellow]")
        except Exception as e:
            self.console.print(f"[red]游戏运行错误: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def _handle_login(self):
        """处理用户登录"""
        self.console.print("\n[bold blue]账户系统[/bold blue]")
        
        while not self.current_user:
            try:
                # 显示选项菜单
                self.console.print("\n[cyan]请选择操作:[/cyan]")
                self.console.print("[white]1.[/white] [green]登录现有账户[/green]")
                self.console.print("[white]2.[/white] [yellow]注册新账户[/yellow]")
                self.console.print("[white]3.[/white] [red]退出游戏[/red]")
                
                choice = self.console.input("\n[cyan]请输入选项 (1-3): [/cyan]").strip()
                
                if choice == "1":
                    # 登录流程
                    await self._handle_existing_login()
                elif choice == "2":
                    # 注册流程
                    await self._handle_registration()
                elif choice == "3":
                    # 退出游戏
                    self.console.print("[yellow]感谢游玩，再见![/yellow]")
                    sys.exit(0)
                else:
                    self.console.print("[red]无效选项，请输入 1、2 或 3[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]操作错误: {e}[/red]")
    
    async def _handle_existing_login(self):
        """处理现有用户登录"""
        self.console.print("\n[bold green]用户登录[/bold green]")
        
        username = self.console.input("[cyan]用户名: [/cyan]")
        password = self.console.input("[cyan]密码: [/cyan]", password=True)
        
        # 尝试登录
        auth_result, user = await self.auth_service.authenticate(username, password)
        if auth_result.value == "success" and user:
            self.current_user = user
            self.console.print(f"[green]✓ 登录成功! 欢迎回来, {user.username}![/green]")
        else:
            # 处理登录错误
            error_messages = {
                "user_not_found": "用户不存在",
                "invalid_credentials": "用户名或密码错误",
                "user_disabled": "账户已被禁用",
                "account_locked": "账户已被锁定",
                "too_many_attempts": "尝试次数过多，请稍后再试"
            }
            error_msg = error_messages.get(auth_result.value, "登录失败")
            self.console.print(f"[red]✗ {error_msg}[/red]")
    
    async def _handle_registration(self):
        """处理新用户注册"""
        self.console.print("\n[bold yellow]用户注册[/bold yellow]")
        
        username = self.console.input("[cyan]请输入用户名: [/cyan]")
        password = self.console.input("[cyan]请输入密码: [/cyan]", password=True)
        confirm_password = self.console.input("[cyan]请确认密码: [/cyan]", password=True)
        
        # 验证密码确认
        if password != confirm_password:
            self.console.print("[red]✗ 两次输入的密码不一致[/red]")
            return
        
        # 尝试注册
        success, message, new_user = await self.auth_service.register_user(username, password)
        if success and new_user:
            self.current_user = new_user
            self.console.print(f"[green]✓ 注册成功! 欢迎加入, {new_user.username}![/green]")
        else:
            self.console.print(f"[red]✗ 注册失败: {message}[/red]")
    
    async def _main_loop(self):
        """主游戏循环"""
        self.console.print("\n[green]游戏开始! 输入 'help' 查看可用命令[/green]")
        
        while self.running:
            try:
                # 显示提示符
                prompt = f"{self.current_user.username}@ChipsBattle$ "
                command_input = await self.session.prompt_async(prompt)
                
                if not command_input.strip():
                    continue
                
                # 分发命令
                result = await self.command_dispatcher.dispatch(
                    command_input, 
                    self.current_user
                )
                
                # 处理特殊命令结果
                if result and result.action == 'quit':
                    self.running = False
                    self.console.print("[yellow]再见![/yellow]")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]使用 'quit' 命令退出游戏[/yellow]")
            except Exception as e:
                self.console.print(f"[red]命令执行错误: {e}[/red]")
    
    async def _cleanup(self):
        """清理资源"""
        self.console.print("[yellow]正在清理资源...[/yellow]")
        
        if self.time_service:
            self.time_service.stop()
        
        if self.db_engine:
            await self.db_engine.close()
        
        self.console.print("[green]清理完成[/green]")


async def main():
    """主函数"""
    game = ChipsBattleGame()
    await game.run()


if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 运行游戏
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n游戏已退出")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)