# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 控制台模式
从main.py迁移的CLI游戏逻辑
"""

import sys
import os
import asyncio
import json
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

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
from core.game_time import GameTime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from adapters.console_adapter import ConsoleAdapter
from interfaces.ui_interface import InputRequest, InputType


class ConsoleGame:
    """控制台游戏主类，从main.py迁移的核心逻辑"""
    
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
        self.stock_service = None
        self.command_dispatcher = None
        self.current_user = None
        self.running = True
        self.ui_adapter = ConsoleAdapter()  # 使用新的UI适配器
        self.login_state_file = os.path.expanduser('~/.chips_battle_login_state.json')
        
        # 加载游戏信息配置
        self.game_info = self._load_game_info()
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, self.settings.LOG_LEVEL),
            format=self.settings.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(project_root / 'console_game.log', encoding='utf-8')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
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
    
    async def initialize(self):
        """初始化游戏系统"""
        try:
            self.logger.info("开始初始化游戏系统")
            
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
                self.logger.info("正在初始化数据库引擎")
                self.db_engine = DatabaseEngine(self.settings)
                await self.db_engine.initialize()
                self.logger.info("数据库引擎初始化完成")
                progress.advance(init_task)
                
                # 设置全局数据库引擎
                progress.update(init_task, description="[yellow]正在设置数据库引擎...")
                await asyncio.sleep(0.2)
                self.logger.debug("设置全局数据库引擎")
                set_global_engine(self.db_engine)
                self.uow = SqlAlchemyUnitOfWork(self.db_engine.sessionmaker)
                self.logger.debug("工作单元初始化完成")
                progress.advance(init_task)
                
                # 初始化时间服务（需要先初始化，因为其他服务依赖它）
                progress.update(init_task, description="[yellow]正在初始化时间服务...")
                await asyncio.sleep(0.2)
                self.logger.info("正在初始化时间服务")
                self.time_service = TimeService(self.event_bus, tick_interval=1)  # 1秒更新一次，让时间变化更明显
                
                # 设置GameTime的时间服务
                GameTime.set_time_service(self.time_service)
                self.logger.info("时间服务初始化完成")
                progress.advance(init_task)
                
                # 初始化货币服务
                progress.update(init_task, description="[yellow]正在初始化货币服务...")
                await asyncio.sleep(0.2)
                self.logger.info("正在初始化货币服务")
                self.currency_service = CurrencyService(self.uow, self.event_bus)
                self.logger.info("货币服务初始化完成")
                progress.advance(init_task)
                
                # 初始化认证服务
                progress.update(init_task, description="[yellow]正在初始化认证服务...")
                await asyncio.sleep(0.2)
                self.logger.info("正在初始化认证服务")
                self.auth_service = AuthService(self.uow, self.event_bus)
                self.logger.info("认证服务初始化完成")
                progress.advance(init_task)
                
                # 初始化应用服务
                progress.update(init_task, description="[yellow]正在初始化应用服务...")
                await asyncio.sleep(0.2)
                self.logger.info("正在初始化应用服务")
                self.app_service = AppService(self.uow, self.event_bus, self.currency_service)
                self.logger.info("应用服务初始化完成")
                progress.advance(init_task)
                
                # 初始化股票服务
                progress.update(init_task, description="[yellow]正在初始化股票服务...")
                await asyncio.sleep(0.2)
                self.logger.info("正在初始化股票服务")
                self.stock_service = StockService(self.uow, self.event_bus, self.currency_service, self.time_service)
                
                # 初始化股票数据
                progress.update(init_task, description="[yellow]正在加载股票数据...")
                await asyncio.sleep(0.2)
                self.logger.info("正在加载股票数据")
                await self.stock_service.initialize_stocks()
                self.logger.info("股票服务初始化完成")
                progress.advance(init_task)
                
                # 初始化新闻服务
                progress.update(init_task, description="[yellow]正在初始化新闻服务...")
                await asyncio.sleep(0.2)
                self.logger.info("正在初始化新闻服务")
                self.news_service = NewsService(self.event_bus, self.time_service)
                self.logger.info("新闻服务初始化完成")
                progress.advance(init_task)
                
                # 初始化命令系统
                progress.update(init_task, description="[yellow]正在创建命令注册器...")
                await asyncio.sleep(0.2)
                self.logger.info("正在创建命令注册器")
                command_registry = CommandRegistry(
                    auth_service=self.auth_service,
                    app_service=self.app_service,
                    news_service=self.news_service,
                    stock_service=self.stock_service,
                    time_service=self.time_service
                )
                self.logger.info("命令注册器创建完成")
                progress.advance(init_task)
                
                # 发现命令
                progress.update(init_task, description="[yellow]正在发现和注册命令...")
                await asyncio.sleep(0.3)
                self.logger.info("正在发现和注册命令")
                await command_registry.discover_commands()
                self.command_dispatcher = CommandDispatcher(
                    command_registry, 
                    self.auth_service,
                    self.event_bus,
                    self.ui_adapter
                )
                
                # 启动时间服务
                await asyncio.sleep(0.1)  # 确保事件循环准备就绪
                self.logger.info("正在启动时间服务")
                self.time_service.start()
                self.logger.info("命令系统初始化完成")
                progress.advance(init_task)
                
                # 完成初始化
                progress.update(init_task, description="[green]✓ 游戏系统初始化完成!")
            
            # 显示初始化完成信息
            self.logger.info("游戏系统初始化完成")
            self.console.print("\n[bold green]🎮 Chips Battle 系统已就绪![/bold green]")
            self.console.print("[dim]所有服务已启动，命令系统已加载完成[/dim]")
            
        except Exception as e:
            self.logger.error(f"游戏系统初始化失败: {e}", exc_info=True)
            self.console.print(f"[red]初始化失败: {e}[/red]")
            raise
    
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
                self.console.print("[white]4.[/white] [magenta]Debug测试 (hahaha账户)[/magenta]")
                
                if login_state and login_state.get('username'):
                    request = InputRequest("\n[cyan]请输入选项 (0-4): [/cyan]", InputType.TEXT)
                    choice = await self.ui_adapter.get_input(request)
                else:
                    request = InputRequest("\n[cyan]请输入选项 (1-4): [/cyan]", InputType.TEXT)
                    choice = await self.ui_adapter.get_input(request)
                
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
                elif choice == "4":
                    # Debug测试登录
                    await self._handle_debug_login()
                else:
                    if login_state and login_state.get('username'):
                        self.console.print("[red]无效选项，请输入 0、1、2、3 或 4[/red]")
                    else:
                        self.console.print("[red]无效选项，请输入 1、2、3 或 4[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]操作错误: {e}[/red]")
    
    async def _handle_quick_login(self, username: str):
        """处理快速登录上次账户"""
        self.console.print(f"\n[bold blue]快速登录: {username}[/bold blue]")
        
        request = InputRequest("[cyan]密码: [/cyan]", InputType.PASSWORD)
        password = await self.ui_adapter.get_input(request)
        
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
                clear_request = InputRequest("[yellow]是否清除保存的登录状态? (y/n): [/yellow]", InputType.TEXT)
                clear_choice = await self.ui_adapter.get_input(clear_request)
                if clear_choice == 'y':
                    self._clear_login_state()
                    self.console.print("[green]✓ 已清除保存的登录状态[/green]")
    
    async def _handle_existing_login(self):
        """处理现有用户登录"""
        self.console.print("\n[bold green]用户登录[/bold green]")
        
        username_request = InputRequest("[cyan]用户名: [/cyan]", InputType.TEXT)
        username = await self.ui_adapter.get_input(username_request)
        password_request = InputRequest("[cyan]密码: [/cyan]", InputType.PASSWORD)
        password = await self.ui_adapter.get_input(password_request)
        
        # 尝试登录
        auth_result, user = await self.auth_service.authenticate(username, password)
        if auth_result.value == "success" and user:
            self.current_user = user
            self.console.print(f"[green]✓ 登录成功! 欢迎回来, {user.username}![/green]")
            
            # 询问是否保留登录状态
            save_request = InputRequest("[cyan]是否保留登录状态以便下次快速登录? (y/n): [/cyan]", InputType.TEXT)
            save_choice = await self.ui_adapter.get_input(save_request)
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
    
    async def _handle_debug_login(self):
        """处理Debug测试登录"""
        self.console.print("\n[bold magenta]Debug测试登录[/bold magenta]")
        self.console.print("[yellow]使用预设账户: hahaha[/yellow]")
        
        # 直接使用预设的账户信息
        username = "hahaha"
        password = "hahaha"
        
        # 尝试登录
        auth_result, user = await self.auth_service.authenticate(username, password)
        if auth_result.value == "success" and user:
            self.current_user = user
            self.console.print(f"[green]✓ Debug登录成功! 欢迎, {user.username}![/green]")
        else:
            # 如果账户不存在，尝试注册
            self.console.print("[yellow]Debug账户不存在，正在创建...[/yellow]")
            try:
                # 创建Debug账户
                from models.auth.user import User
                new_user = User(
                    username=username,
                    email="debug@test.com",
                    password_hash=""  # 这里会在注册时被正确设置
                )
                
                register_result, created_user = await self.auth_service.register(
                    username, "debug@test.com", password
                )
                
                if register_result.value == "success" and created_user:
                    self.console.print("[green]✓ Debug账户创建成功![/green]")
                    # 再次尝试登录
                    auth_result, user = await self.auth_service.authenticate(username, password)
                    if auth_result.value == "success" and user:
                        self.current_user = user
                        self.console.print(f"[green]✓ Debug登录成功! 欢迎, {user.username}![/green]")
                    else:
                        self.console.print("[red]✗ Debug登录失败[/red]")
                else:
                    self.console.print("[red]✗ Debug账户创建失败[/red]")
            except Exception as e:
                self.console.print(f"[red]✗ Debug登录过程出错: {e}[/red]")
    
    async def _handle_registration(self):
        """处理新用户注册"""
        self.console.print("\n[bold yellow]用户注册[/bold yellow]")
        
        username_request = InputRequest("[cyan]请输入用户名: [/cyan]", InputType.TEXT)
        username = await self.ui_adapter.get_input(username_request)
        password_request = InputRequest("[cyan]请输入密码: [/cyan]", InputType.PASSWORD)
        password = await self.ui_adapter.get_input(password_request)
        confirm_request = InputRequest("[cyan]请确认密码: [/cyan]", InputType.PASSWORD)
        confirm_password = await self.ui_adapter.get_input(confirm_request)
        
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
            save_request = InputRequest("[cyan]是否保留登录状态以便下次快速登录? (y/n): [/cyan]", InputType.TEXT)
            save_choice = await self.ui_adapter.get_input(save_request)
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
                request = InputRequest(prompt, InputType.TEXT)
                command_input = await self.ui_adapter.get_input(request)
                
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
            clear_request = InputRequest("[cyan]是否清除保存的登录状态? (y/n): [/cyan]", InputType.TEXT)
            clear_choice = await self.ui_adapter.get_input(clear_request)
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


# 为了保持向后兼容性，保留原有的main函数
async def run_direct_command(command_args):
    """直接运行命令，无需进入游戏循环"""
    if len(command_args) < 1:
        print("错误: 请指定要运行的命令")
        return False
    
    try:
        # 初始化必要的组件
        settings = Settings()
        event_bus = EventBus()
        db_engine = DatabaseEngine(settings)
        await db_engine.initialize()
        set_global_engine(db_engine)
        uow = SqlAlchemyUnitOfWork(db_engine.sessionmaker)
        
        # 初始化时间服务（需要先初始化，因为其他服务依赖它）
        from services.time_service import TimeService
        from core.game_time import GameTime
        time_service = TimeService(event_bus)
        GameTime.set_time_service(time_service)
        
        # 初始化其他服务
        currency_service = CurrencyService(uow, event_bus)
        auth_service = AuthService(uow, event_bus)
        app_service = AppService(uow, event_bus, currency_service)
        stock_service = StockService(uow, event_bus, currency_service, time_service)
        news_service = NewsService(event_bus, time_service)
        
        # 创建命令注册器和分发器
        command_registry = CommandRegistry(
            auth_service=auth_service,
            app_service=app_service,
            news_service=news_service,
            stock_service=stock_service,
            time_service=time_service
        )
        await command_registry.discover_commands()
        
        command_dispatcher = CommandDispatcher(
            command_registry,
            auth_service,
            event_bus,
            Console()
        )
        
        # 获取命令字符串
        command_string = ' '.join(command_args)
        
        # 创建一个模拟用户（用于需要认证的命令）
        from models.auth.user import User
        mock_user = User(
            user_id=1,
            username="direct_command_user",
            email="direct@example.com"
        )
        
        # 执行命令
        result = await command_dispatcher.dispatch(command_string, mock_user)
        
        if result and result.success:
            print(result.message)
        else:
            print(f"命令执行失败: {result.message if result else '未知错误'}")
            return False
        
        # 清理资源
        if time_service:
            time_service.stop()
        await db_engine.close()
        return True
        
    except Exception as e:
        print(f"执行命令时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main(args):
    """主函数"""
    # 检查是否有直接命令要执行
    if args.command:
        # 如果有命令参数，作为直接命令执行
        success = await run_direct_command(args.command)
        sys.exit(0 if success else 1)
    else:
        # 否则启动正常游戏
        game = ConsoleGame()
        await game.run()


if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='Chips Battle Remake v3.0 Alpha - 控制台模式',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Chips Battle Remake v3.0 Alpha'
    )
    
    # 添加位置参数用于直接命令执行
    parser.add_argument(
        'command',
        nargs='*',
        help='要直接执行的命令（可选）'
    )
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        print("🐛 调试模式已启用")
    
    # 运行控制台游戏
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\n🎮 游戏已退出")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)