#!C:\programdata\anaconda3\python.exe
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
import json
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
from services.stock_service import StockService
from commands.registry import CommandRegistry
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
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
        self.login_state_file = os.path.expanduser('~/.chips_battle_login_state.json')
        
        # 加载游戏信息配置
        self.game_info = self._load_game_info()
    
    def _save_login_state(self, username: str):
        """保存登录状态"""
        try:
            login_data = {
                'username': username,
                'timestamp': asyncio.get_event_loop().time()
            }
            with open(self.login_state_file, 'w', encoding='utf-8') as f:
                json.dump(login_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.console.print(f"[yellow]保存登录状态失败: {e}[/yellow]")
    
    def _load_login_state(self):
        """加载登录状态"""
        try:
            if os.path.exists(self.login_state_file):
                with open(self.login_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.console.print(f"[yellow]加载登录状态失败: {e}[/yellow]")
        return None
    
    def _clear_login_state(self):
        """清除登录状态"""
        try:
            if os.path.exists(self.login_state_file):
                os.remove(self.login_state_file)
        except Exception as e:
            self.console.print(f"[yellow]清除登录状态失败: {e}[/yellow]")
    
    def _load_game_info(self):
        """加载游戏信息配置"""
        try:
            info_file = project_root / "data" / "config.json"
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.console.print(f"[yellow]加载游戏信息配置失败: {e}[/yellow]")
        
        # 返回默认配置
        return {
            "game": {
                "name": "CHIPS BATTLE REMAKE",
                "version": "v3.0 Alpha",
                "subtitle": "命令驱动的金融模拟游戏",
                "welcome_title": "欢迎来到 Chips Battle"
            }
        }
        
    async def initialize(self):
        """初始化游戏系统"""
        try:
            # 显示启动画面
            self._show_startup_banner()
            
            # 创建进度条
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                
                # 定义初始化任务
                init_task = progress.add_task("[cyan]正在初始化游戏系统...", total=10)
                
                # 初始化数据库
                progress.update(init_task, description="[yellow]正在初始化数据库...")
                await asyncio.sleep(0.3)  # 让用户看到进度
                self.db_engine = DatabaseEngine(self.settings)
                await self.db_engine.initialize()
                progress.advance(init_task)
                
                # 设置全局数据库引擎
                progress.update(init_task, description="[yellow]正在设置数据库引擎...")
                await asyncio.sleep(0.2)
                set_global_engine(self.db_engine)
                self.uow = SqlAlchemyUnitOfWork(self.db_engine.sessionmaker)
                progress.advance(init_task)
                
                # 初始化时间服务
                progress.update(init_task, description="[yellow]正在初始化时间服务...")
                await asyncio.sleep(0.2)
                self.time_service = TimeService(self.event_bus)
                progress.advance(init_task)
                
                # 初始化货币服务
                progress.update(init_task, description="[yellow]正在初始化货币服务...")
                await asyncio.sleep(0.2)
                self.currency_service = CurrencyService(self.uow, self.event_bus)
                progress.advance(init_task)
                
                # 初始化认证服务
                progress.update(init_task, description="[yellow]正在初始化认证服务...")
                await asyncio.sleep(0.2)
                self.auth_service = AuthService(self.uow, self.event_bus)
                progress.advance(init_task)
                
                # 初始化应用服务
                progress.update(init_task, description="[yellow]正在初始化应用服务...")
                await asyncio.sleep(0.2)
                self.app_service = AppService(self.uow, self.event_bus, self.currency_service)
                progress.advance(init_task)
                
                # 初始化股票服务
                progress.update(init_task, description="[yellow]正在初始化股票服务...")
                await asyncio.sleep(0.2)
                self.stock_service = StockService(self.uow, self.event_bus, self.currency_service, self.time_service)
                progress.advance(init_task)
                
                # 初始化新闻服务
                progress.update(init_task, description="[yellow]正在初始化新闻服务...")
                await asyncio.sleep(0.2)
                self.news_service = NewsService(self.event_bus, self.time_service)
                progress.advance(init_task)
                
                # 初始化命令系统
                progress.update(init_task, description="[yellow]正在创建命令注册器...")
                await asyncio.sleep(0.2)
                command_registry = CommandRegistry(
                    auth_service=self.auth_service,
                    app_service=self.app_service,
                    news_service=self.news_service,
                    stock_service=self.stock_service
                )
                progress.advance(init_task)
                
                # 发现命令
                progress.update(init_task, description="[yellow]正在发现和注册命令...")
                await asyncio.sleep(0.3)
                await command_registry.discover_commands()
                self.command_dispatcher = CommandDispatcher(
                    command_registry, 
                    self.auth_service,
                    self.event_bus,
                    self.console
                )
                
                # 启动时间服务
                self.time_service.start()
                progress.advance(init_task)
                
                # 完成初始化
                progress.update(init_task, description="[green]✓ 游戏系统初始化完成!")
            
            # 显示初始化完成信息
            self.console.print("\n[bold green]🎮 Chips Battle 系统已就绪![/bold green]")
            self.console.print("[dim]所有服务已启动，命令系统已加载完成[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]初始化失败: {e}[/red]")
            raise
    
    def _show_startup_banner(self):
        """显示启动横幅"""
        game_config = self.game_info.get('game', {})
        banner_config = self.game_info.get('banner', {})
        
        banner_text = Text()
        banner_text.append("\n")
        
        # 使用配置中的ASCII艺术字或默认的
        ascii_art = banner_config.get('ascii_art', [
            "  ██████╗██╗  ██╗██╗██████╗ ███████╗",
            " ██╔════╝██║  ██║██║██╔══██╗██╔════╝",
            " ██║     ███████║██║██████╔╝███████╗",
            " ██║     ██╔══██║██║██╔═══╝ ╚════██║",
            " ╚██████╗██║  ██║██║██║     ███████║",
            "  ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝"
        ])
        
        ascii_color = banner_config.get('colors', {}).get('ascii_art', 'bold cyan')
        for line in ascii_art:
            banner_text.append(f"{line}\n", style=ascii_color)
        
        banner_text.append("\n")
        
        # 游戏标题和版本
        game_name = game_config.get('name', 'CHIPS BATTLE REMAKE')
        game_version = game_config.get('version', 'v3.0 Alpha')
        title_color = banner_config.get('colors', {}).get('game_title', 'bold yellow')
        banner_text.append(f"    {game_name} {game_version}\n", style=title_color)
        
        # 副标题
        subtitle = game_config.get('subtitle', '命令驱动的金融模拟游戏')
        subtitle_color = banner_config.get('colors', {}).get('subtitle', 'dim')
        banner_text.append(f"    {subtitle}\n", style=subtitle_color)
        
        banner_text.append("\n")
        
        # 面板标题和边框颜色
        panel_title = game_config.get('welcome_title', '欢迎来到 Chips Battle')
        panel_title_color = banner_config.get('colors', {}).get('panel_title', 'bold green')
        panel_border_color = banner_config.get('colors', {}).get('panel_border', 'green')
        
        panel = Panel(
            banner_text,
            title=f"[{panel_title_color}]{panel_title}[/{panel_title_color}]",
            border_style=panel_border_color,
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
        
        # 检查是否有保存的登录状态
        login_state = self._load_login_state()
        
        while not self.current_user:
            try:
                # 显示选项菜单
                self.console.print("\n[cyan]请选择操作:[/cyan]")
                
                # 如果有保存的登录状态，显示快速登录选项
                if login_state and login_state.get('username'):
                    self.console.print(f"[white]0.[/white] [blue]登录上次账户 ({login_state['username']})[/blue]")
                
                self.console.print("[white]1.[/white] [green]登录现有账户[/green]")
                self.console.print("[white]2.[/white] [yellow]注册新账户[/yellow]")
                self.console.print("[white]3.[/white] [red]退出游戏[/red]")
                
                if login_state and login_state.get('username'):
                    choice = self.console.input("\n[cyan]请输入选项 (0-3): [/cyan]").strip()
                else:
                    choice = self.console.input("\n[cyan]请输入选项 (1-3): [/cyan]").strip()
                
                if choice == "0" and login_state and login_state.get('username'):
                    # 快速登录上次账户
                    await self._handle_quick_login(login_state['username'])
                elif choice == "1":
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
                    if login_state and login_state.get('username'):
                        self.console.print("[red]无效选项，请输入 0、1、2 或 3[/red]")
                    else:
                        self.console.print("[red]无效选项，请输入 1、2 或 3[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]操作错误: {e}[/red]")
    
    async def _handle_quick_login(self, username: str):
        """处理快速登录上次账户"""
        self.console.print(f"\n[bold blue]快速登录: {username}[/bold blue]")
        
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
            
            # 如果登录失败，询问是否清除保存的登录状态
            if auth_result.value in ["user_not_found", "invalid_credentials"]:
                clear_choice = self.console.input("[yellow]是否清除保存的登录状态? (y/n): [/yellow]").strip().lower()
                if clear_choice == 'y':
                    self._clear_login_state()
                    self.console.print("[green]✓ 已清除保存的登录状态[/green]")
    
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
            
            # 询问是否保留登录状态
            save_choice = self.console.input("[cyan]是否保留登录状态以便下次快速登录? (y/n): [/cyan]").strip().lower()
            if save_choice == 'y':
                self._save_login_state(username)
                self.console.print("[green]✓ 登录状态已保存[/green]")
            else:
                # 如果用户选择不保存，清除可能存在的旧登录状态
                self._clear_login_state()
                self.console.print("[blue]ℹ 登录状态未保存[/blue]")
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
            
            # 询问是否保留登录状态
            save_choice = self.console.input("[cyan]是否保留登录状态以便下次快速登录? (y/n): [/cyan]").strip().lower()
            if save_choice == 'y':
                self._save_login_state(username)
                self.console.print("[green]✓ 登录状态已保存[/green]")
            else:
                self.console.print("[blue]ℹ 登录状态未保存[/blue]")
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
        
        # 检查是否有保存的登录状态，询问是否清除
        login_state = self._load_login_state()
        if login_state:
            clear_choice = self.console.input("[cyan]是否清除保存的登录状态? (y/n): [/cyan]").strip().lower()
            if clear_choice == 'y':
                self._clear_login_state()
                self.console.print("[green]✓ 登录状态已清除[/green]")
            else:
                self.console.print("[blue]ℹ 登录状态已保留[/blue]")
        
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