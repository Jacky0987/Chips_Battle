# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - GUI主窗口
VSCode风格的主界面布局
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from terminal.layout_manager import VSCodeLayoutManager
from terminal.login_window import LoginWindow
from terminal.terminal_panel import TerminalPanel
from terminal.sidebar import SidebarPanel
from terminal.right_panel_manager import RightPanelManager
from terminal.status_bar import StatusBar
from terminal.header_bar import HeaderBar
from terminal.theme_manager import ThemeManager

# 导入游戏核心模块
from config.settings import Settings
from core.event_bus import EventBus
from dal.database import DatabaseEngine, set_global_engine
from dal.unit_of_work import SqlAlchemyUnitOfWork
from services.time_service import TimeService
from services.command_dispatcher import CommandDispatcher
from services.auth_service import AuthService
from services.app_service import AppService
from services.news_service import NewsService
from services.currency_service import CurrencyService
from services.stock_service import StockService
from commands.registry import CommandRegistry
from core.game_time import GameTime

class ChipsBattleGUI:
    """Chips Battle GUI主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CHIPS BATTLE REMAKE v3.0 Alpha")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap("assets/icon.ico")
            pass
        except:
            pass
            
        # 初始化组件
        self.theme_manager = ThemeManager()
        self.layout_manager = VSCodeLayoutManager(self.root)
        
        # GUI组件
        self.header_bar: Optional[HeaderBar] = None
        self.sidebar: Optional[SidebarPanel] = None
        self.terminal_panel: Optional[TerminalPanel] = None
        self.right_panel_manager: Optional[RightPanelManager] = None
        self.status_bar: Optional[StatusBar] = None
        
        # 游戏相关
        self.game_instance = None
        self.current_user = None
        self.is_logged_in = False
        
        # 异步事件循环
        self.loop = None
        self.loop_thread = None
        
        # 游戏核心组件
        self.settings = None
        self.event_bus = None
        self.db_engine = None
        self.uow = None
        self.time_service = None
        self.auth_service = None
        self.app_service = None
        self.news_service = None
        self.currency_service = None
        self.stock_service = None
        self.command_dispatcher = None
        
        # UI适配器
        self.ui_adapter = None
        
        # 登录状态文件
        self.login_state_file = Path.home() / '.chips_battle_login_state.json'
        
        # 设置日志
        self._setup_logging()
        
        # 初始化界面
        self._setup_ui()
        self._setup_events()
        
        # 初始化游戏服务
        self._initialize_game_services()
        
    def _setup_logging(self):
        """设置日志配置 - 与console模式完全一致"""
        import logging
        self.settings = Settings()
        
        logging.basicConfig(
            level=getattr(logging, self.settings.LOG_LEVEL),
            format=self.settings.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(project_root / 'gui_game.log', encoding='utf-8')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def _initialize_game_services(self):
        """初始化游戏服务基础组件"""
        # 初始化事件总线
        self.event_bus = EventBus()
        
        # 初始化UI适配器
        from adapters.gui_adapter import GUIAdapter
        self.ui_adapter = GUIAdapter(self.terminal_panel)
        
    def _setup_ui(self):
        """设置用户界面"""
        # 应用主题
        self.theme_manager.apply_theme(self.root, 'professional')
        
        # 创建主要布局区域
        self.layout_manager.create_layout()
        
        # 创建各个面板
        self._create_header_bar()
        self._create_sidebar()
        self._create_terminal_panel()
        self._create_right_panel()
        self._create_status_bar()
        
    def _create_header_bar(self):
        """创建顶部状态栏"""
        header_frame = self.layout_manager.get_frame('header')
        self.header_bar = HeaderBar(header_frame, self)
        
    def _create_sidebar(self):
        """创建左侧活动栏"""
        sidebar_frame = self.layout_manager.get_frame('sidebar')
        self.sidebar = SidebarPanel(sidebar_frame, self)
        
    def _create_terminal_panel(self):
        """创建中央终端面板"""
        terminal_frame = self.layout_manager.get_frame('terminal')
        self.terminal_panel = TerminalPanel(terminal_frame, self)
        
    def _create_right_panel(self):
        """创建右侧面板管理器"""
        panel_frame = self.layout_manager.get_frame('panel')
        self.right_panel_manager = RightPanelManager(panel_frame, self)
        
    def _create_status_bar(self):
        """创建底部状态栏"""
        status_frame = self.layout_manager.get_frame('footer')
        self.status_bar = StatusBar(status_frame, self)
        
    def _setup_events(self):
        """设置事件处理"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 窗口大小改变事件
        self.root.bind('<Configure>', self.on_window_resize)
        
        # 快捷键绑定
        self._setup_shortcuts()
        
    def _setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+1: 聚焦侧边栏
        self.root.bind('<Control-Key-1>', lambda e: self.focus_sidebar())
        
        # Ctrl+2: 聚焦终端
        self.root.bind('<Control-Key-2>', lambda e: self.focus_terminal())
        
        # Ctrl+3: 聚焦右侧面板
        self.root.bind('<Control-Key-3>', lambda e: self.focus_right_panel())
        
        # Ctrl+`: 切换终端
        self.root.bind('<Control-grave>', lambda e: self.toggle_terminal())
        
        # Ctrl+B: 切换侧边栏
        self.root.bind('<Control-b>', lambda e: self.toggle_sidebar())
        
        # F1: 显示帮助
        self.root.bind('<F1>', lambda e: self.show_help())
        
    def _show_startup_banner(self):
        """显示启动横幅 - 与console模式完全一致"""
        self.logger.debug("_show_startup_banner called")
        
        # 加载游戏信息配置
        game_info = self._load_game_info()
        game_config = game_info.get('game', {})
        banner_config = game_info.get('banner', {})
        
        # 使用配置中的ASCII艺术字或默认的
        ascii_art = banner_config.get('ascii_art', [
            "  ██████╗██╗  ██╗██╗██████╗ ███████╗",
            " ██╔════╝██║  ██║██║██╔══██╗██╔════╝",
            " ██║     ███████║██║██████╔╝███████╗",
            " ██║     ██╔══██║██║██╔═══╝ ╚════██║",
            " ╚██████╗██║  ██║██║██║     ███████║",
            "  ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝"
        ])
        
        # 游戏标题和版本
        game_name = game_config.get('name', 'CHIPS BATTLE REMAKE')
        game_version = game_config.get('version', 'v3.0 Alpha')
        
        # 副标题
        subtitle = game_config.get('subtitle', '命令驱动的金融模拟游戏')
        
        # 面板标题
        panel_title = game_config.get('welcome_title', '欢迎来到 Chips Battle')
        
        # 构建横幅文本
        banner_lines = []
        banner_lines.append("") # Add a blank line for spacing
        for line in ascii_art:
            banner_lines.append(line)
        banner_lines.append("") # Add a blank line for spacing
        banner_lines.append(f"    {game_name} {game_version}")
        banner_lines.append(f"    {subtitle}")
        banner_lines.append("") # Add a blank line for spacing
        
        # 格式化为终端面板可接受的输出
        # 这里我们不能直接使用rich的Panel，因为terminal_panel只接受字符串和类型
        # 我们手动构建一个类似rich Panel的边框和标题
        
        max_line_length = max(len(line) for line in banner_lines) if banner_lines else 0
        panel_width = max(max_line_length + 6, len(panel_title) + 6) # 左右各3个空格，加上标题长度
        
        top_border = "╭" + "─" * (panel_width - 2) + "╮"
        bottom_border = "╰" + "─" * (panel_width - 2) + "╯"
        
        # 居中标题
        title_padding = (panel_width - len(panel_title) - 2) // 2
        title_line = "│ " + " " * title_padding + panel_title + " " * (panel_width - len(panel_title) - 2 - title_padding) + " │"
        
        # 居中横幅内容
        content_lines = []
        for line in banner_lines:
            padding = (panel_width - len(line) - 2) // 2
            content_lines.append("│ " + " " * padding + line + " " * (panel_width - len(line) - 2 - padding) + " │")
        
        full_banner = [top_border, title_line] + content_lines + [bottom_border]
        
        self.terminal_panel.clear_output()
        for line in full_banner:
            self.terminal_panel.append_output(line + "\n", 'system')
        
        self.logger.debug("Startup banner displayed in terminal panel")
        
    def _load_game_info(self):
        """加载游戏信息配置"""
        try:
            import json
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            info_file = project_root / "data" / "config.json"
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[yellow]加载游戏信息配置失败: {e}[/yellow]")
        
        # 返回默认配置
        return {
            "game": {
                "name": "CHIPS BATTLE REMAKE",
                "version": "v3.0 Alpha",
                "subtitle": "命令驱动的金融模拟游戏",
                "welcome_title": "欢迎来到 Chips Battle"
            }
        }
        
    def _save_login_state(self, username: str):
        """保存登录状态"""
        try:
            import json
            import os
            from pathlib import Path
            login_state_file = Path.home() / '.chips_battle_login_state.json'
            
            login_data = {
                'username': username,
                'timestamp': asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0
            }
            with open(login_state_file, 'w', encoding='utf-8') as f:
                json.dump(login_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.terminal_panel.append_output(f"⚠️ 保存登录状态失败: {e}\n", 'warning')
    
    def _load_login_state(self):
        """加载登录状态"""
        try:
            import json
            from pathlib import Path
            login_state_file = Path.home() / '.chips_battle_login_state.json'
            
            if login_state_file.exists():
                with open(login_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.terminal_panel.append_output(f"⚠️ 加载登录状态失败: {e}\n", 'warning')
        return None
    
    def _clear_login_state(self):
        """清除登录状态"""
        try:
            from pathlib import Path
            login_state_file = Path.home() / '.chips_battle_login_state.json'
            
            if login_state_file.exists():
                login_state_file.unlink()
        except Exception as e:
            self.terminal_panel.append_output(f"⚠️ 清除登录状态失败: {e}\n", 'warning')
        
    async def initialize_game_system(self):
        """初始化游戏系统 - 与console模式完全一致，使用真实的数据库和服务初始化"""
        try:
            self.logger.info("开始初始化游戏系统")
            
            # 显示启动画面
            self._show_startup_banner()
            
            # 在终端面板中显示进度条
            self.terminal_panel.append_output("\n🚀 正在初始化游戏系统...\n", 'info')
            
            # 定义初始化步骤
            init_steps = [
                "[yellow]正在初始化数据库...",
                "[yellow]正在设置数据库引擎...",
                "[yellow]正在初始化时间服务...",
                "[yellow]正在初始化货币服务...",
                "[yellow]正在初始化认证服务...",
                "[yellow]正在初始化应用服务...",
                "[yellow]正在初始化股票服务...",
                "[yellow]正在加载股票数据...",
                "[yellow]正在初始化新闻服务...",
                "[yellow]正在创建命令注册器...",
                "[yellow]正在发现和注册命令...",
                "[green]✓ 游戏系统初始化完成!"
            ]
            
            total_steps = len(init_steps)
            
            for i, step_desc in enumerate(init_steps):
                # 更新进度显示
                progress_percent = int((i + 1) / total_steps * 100)
                progress_bar = "█" * (progress_percent // 5) + "░" * (20 - progress_percent // 5)
                self.terminal_panel.append_output(f"  {step_desc} [{progress_bar}] {progress_percent}%\n", 'system')
                
                if i == 0:  # 初始化数据库
                    self.terminal_panel.append_output("    正在初始化数据库引擎...\n", 'system')
                    from config.settings import Settings
                    from dal.database import DatabaseEngine, set_global_engine
                    self.settings = Settings()
                    self.db_engine = DatabaseEngine(self.settings)
                    await self.db_engine.initialize()
                    self.terminal_panel.append_output("    ✓ 数据库引擎初始化完成\n", 'success')
                    
                elif i == 1:  # 设置全局数据库引擎
                    self.terminal_panel.append_output("    设置全局数据库引擎...\n", 'system')
                    from dal.unit_of_work import SqlAlchemyUnitOfWork
                    set_global_engine(self.db_engine)
                    self.uow = SqlAlchemyUnitOfWork(self.db_engine.sessionmaker)
                    self.terminal_panel.append_output("    ✓ 工作单元初始化完成\n", 'success')
                    
                elif i == 2:  # 初始化时间服务
                    self.terminal_panel.append_output("    正在初始化时间服务...\n", 'system')
                    from services.time_service import TimeService
                    from core.game_time import GameTime
                    self.time_service = TimeService(self.event_bus, tick_interval=1)
                    GameTime.set_time_service(self.time_service)
                    self.terminal_panel.append_output("    ✓ 时间服务初始化完成\n", 'success')
                    
                elif i == 3:  # 初始化货币服务
                    self.terminal_panel.append_output("    正在初始化货币服务...\n", 'system')
                    from services.currency_service import CurrencyService
                    self.currency_service = CurrencyService(self.uow, self.event_bus)
                    self.terminal_panel.append_output("    ✓ 货币服务初始化完成\n", 'success')
                    
                elif i == 4:  # 初始化认证服务
                    self.terminal_panel.append_output("    正在初始化认证服务...\n", 'system')
                    from services.auth_service import AuthService
                    self.auth_service = AuthService(self.uow, self.event_bus)
                    self.terminal_panel.append_output("    ✓ 认证服务初始化完成\n", 'success')
                    
                elif i == 5:  # 初始化应用服务
                    self.terminal_panel.append_output("    正在初始化应用服务...\n", 'system')
                    from services.app_service import AppService
                    self.app_service = AppService(self.uow, self.event_bus, self.currency_service)
                    self.terminal_panel.append_output("    ✓ 应用服务初始化完成\n", 'success')
                    
                elif i == 6:  # 初始化股票服务
                    self.terminal_panel.append_output("    正在初始化股票服务...\n", 'system')
                    from services.stock_service import StockService
                    self.stock_service = StockService(self.uow, self.event_bus, self.currency_service, self.time_service)
                    self.terminal_panel.append_output("    ✓ 股票服务初始化完成\n", 'success')
                    
                elif i == 7:  # 加载股票数据
                    self.terminal_panel.append_output("    正在加载股票数据...\n", 'system')
                    await self.stock_service.initialize_stocks()
                    self.terminal_panel.append_output("    ✓ 股票数据加载完成\n", 'success')
                    
                elif i == 8:  # 初始化新闻服务
                    self.terminal_panel.append_output("    正在初始化新闻服务...\n", 'system')
                    from services.news_service import NewsService
                    self.news_service = NewsService(self.event_bus, self.time_service)
                    self.terminal_panel.append_output("    ✓ 新闻服务初始化完成\n", 'success')
                    
                elif i == 9:  # 创建命令注册器
                    self.terminal_panel.append_output("    正在创建命令注册器...\n", 'system')
                    from commands.registry import CommandRegistry
                    command_registry = CommandRegistry(
                        auth_service=self.auth_service,
                        app_service=self.app_service,
                        news_service=self.news_service,
                        stock_service=self.stock_service,
                        time_service=self.time_service
                    )
                    self.terminal_panel.append_output("    ✓ 命令注册器创建完成\n", 'success')
                    
                elif i == 10:  # 发现和注册命令
                    self.terminal_panel.append_output("    正在发现和注册命令...\n", 'system')
                    from services.command_dispatcher import CommandDispatcher
                    await command_registry.discover_commands()
                    self.command_dispatcher = CommandDispatcher(
                        command_registry,
                        self.auth_service,
                        self.event_bus,
                        self.ui_adapter
                    )
                    self.terminal_panel.append_output("    ✓ 命令发现和注册完成\n", 'success')
                    
                # 启动时间服务
                if i == 10:
                    self.terminal_panel.append_output("    正在启动时间服务...\n", 'system')
                    self.time_service.start()
                    self.terminal_panel.append_output("    ✓ 时间服务启动完成\n", 'success')
                
                # 添加短暂延迟，让用户看到进度
                await asyncio.sleep(0.2)
            
            # 显示初始化完成信息
            self.terminal_panel.append_output("\n🎮 Chips Battle 系统已就绪!\n", 'success')
            self.terminal_panel.append_output("所有服务已启动，命令系统已加载完成\n", 'info')
            
            self.logger.info("游戏系统初始化完成")
            
            # 显示登录菜单
            self.root.after(1000, self._show_login_menu)
            
        except Exception as e:
            self.logger.error(f"游戏系统初始化失败: {e}", exc_info=True)
            self.terminal_panel.append_output(f"❌ 初始化失败: {e}\n", 'error')
            # 显示错误后仍然显示登录菜单
            self.root.after(3000, self._show_login_menu)
        
    def _show_login_menu(self):
        """显示登录菜单 - 与console模式完全一致"""
        # 检查是否有保存的登录状态
        login_state = self._load_login_state()
        
        menu_text = "\n🔐 账户系统\n\n"
        menu_text += "请选择操作:\n"
        
        # 如果有保存的登录状态，显示快速登录选项
        if login_state and login_state.get('username'):
            menu_text += f"0. 🔓 登录上次账户 ({login_state['username']})\n"
        
        menu_text += "1. 👤 登录现有账户\n"
        menu_text += "2. 📝 注册新账户\n"
        menu_text += "3. 🚪 退出游戏\n"
        menu_text += "4. 🔬 Debug测试 (hahaha账户)\n\n"
        
        if login_state and login_state.get('username'):
            menu_text += "💡 请输入选项 (0-4): "
        else:
            menu_text += "💡 请输入选项 (1-4): "
        
        self.terminal_panel.append_output(menu_text, 'system')
        self.terminal_panel.set_login_mode(True, callback=self._handle_login_choice)
            
    def _handle_login_choice(self, choice: str):
        """处理登录选择 - 与console模式完全一致"""
        choice = choice.strip()
        
        # 检查是否有保存的登录状态
        login_state = self._load_login_state()
        
        if choice == "0" and login_state and login_state.get('username'):
            # 快速登录上次账户
            self._handle_quick_login(login_state['username'])
        elif choice == "1":
            # 登录现有账户
            self._handle_existing_login()
        elif choice == "2":
            # 注册新账户
            self._handle_registration()
        elif choice == "3":
            # 退出游戏
            self.on_closing()
        elif choice == "4":
            # Debug测试登录
            self._handle_debug_login()
        else:
            if login_state and login_state.get('username'):
                self.terminal_panel.append_output("❌ 无效选项，请输入 0、1、2、3 或 4: ", 'error')
            else:
                self.terminal_panel.append_output("❌ 无效选项，请输入 1、2、3 或 4: ", 'error')
            self.terminal_panel.set_login_mode(True, callback=self._handle_login_choice)
            
    def _handle_quick_login(self, username: str):
        """处理快速登录上次账户 - 与console模式完全一致"""
        self.terminal_panel.append_output(f"\n🔓 快速登录: {username}\n", 'info')
        self.terminal_panel.append_output("密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._complete_quick_login(username, pwd))
        
    def _complete_quick_login(self, username: str, password: str):
        """完成快速登录"""
        password = password.strip()
        if not password:
            self.terminal_panel.append_output("❌ 密码不能为空，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._complete_quick_login(username, pwd))
            return
            
        # 在异步线程中执行认证
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_quick_login(username, password),
                self.loop
            )
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    async def _async_quick_login(self, username: str, password: str):
        """异步执行快速登录"""
        try:
            if self.auth_service:
                auth_result, user = await self.auth_service.authenticate(username, password)
                if auth_result.value == "success" and user:
                    self.root.after(0, lambda: self._complete_user_login(user, save_state=True))
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
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        f"❌ {error_msg}\n", 'error'
                    ))
                    
                    # 如果登录失败，询问是否清除保存的登录状态
                    if auth_result.value in ["user_not_found", "invalid_credentials"]:
                        self.root.after(0, lambda: self.terminal_panel.append_output(
                            "是否清除保存的登录状态? (y/n): ", 'warning'
                        ))
                        self.root.after(0, lambda: self.terminal_panel.set_login_mode(
                            True, callback=lambda choice: self._handle_clear_login_state(choice)
                        ))
                    else:
                        self.root.after(2000, self._show_login_menu)
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "认证服务未初始化\n", 'error'
                ))
                self.root.after(2000, self._show_login_menu)
                
        except Exception as e:
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"❌ 快速登录过程出错: {e}\n", 'error'
            ))
            self.root.after(2000, self._show_login_menu)
            
    def _handle_clear_login_state(self, choice: str):
        """处理清除登录状态的选择"""
        if choice.lower() == 'y':
            self._clear_login_state()
            self.terminal_panel.append_output("✓ 已清除保存的登录状态\n", 'success')
        self.root.after(1500, self._show_login_menu)
        
    def _handle_debug_login(self):
        """处理Debug测试登录 - 使用真实的AuthService"""
        self.terminal_panel.append_output("\n🔬 Debug测试登录\n", 'info')
        self.terminal_panel.append_output("使用预设账户: hahaha\n", 'system')
        
        # 直接使用预设的账户信息
        username = "hahaha"
        password = "hahaha"
        
        # 在异步线程中执行认证
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_debug_login(username, password),
                self.loop
            )
            # 不等待结果，让认证异步执行
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    def _handle_registration(self):
        """处理新用户注册 - 与console模式完全一致"""
        self.terminal_panel.append_output("\n📝 用户注册\n", 'info')
        self.terminal_panel.append_output("请输入用户名: ", 'system')
        self.terminal_panel.set_login_mode(True, callback=self._handle_register_username)
        
    def _handle_register_username(self, username: str):
        """处理注册用户名输入"""
        username = username.strip()
        if not username:
            self.terminal_panel.append_output("❌ 用户名不能为空，请重新输入用户名: ", 'error')
            self.terminal_panel.set_login_mode(True, callback=self._handle_register_username)
            return
            
        self.terminal_panel.append_output("请输入密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_password(username, pwd))
        
    def _handle_register_password(self, username: str, password: str):
        """处理注册密码输入"""
        password = password.strip()
        if not password:
            self.terminal_panel.append_output("❌ 密码不能为空，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_password(username, pwd))
            return
            
        self.terminal_panel.append_output("请确认密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_confirm(username, password, pwd))
        
    def _handle_register_confirm(self, username: str, password: str, confirm: str):
        """处理注册确认密码 - 使用真实的AuthService"""
        confirm = confirm.strip()
        if password != confirm:
            self.terminal_panel.append_output("❌ 两次输入的密码不一致，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_password(username, pwd))
            return
            
        # 在异步线程中执行注册
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_register_user(username, password),
                self.loop
            )
            # 不等待结果，让注册异步执行
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    async def _async_register_user(self, username: str, password: str):
        """异步执行用户注册"""
        try:
            if self.auth_service:
                register_result, created_user = await self.auth_service.register(
                    username, f"{username}@example.com", password
                )
                
                if register_result.value == "success" and created_user:
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        "✓ 注册成功！正在自动登录...\n", 'success'
                    ))
                    # 注册成功后自动登录
                    self.root.after(1500, lambda: self._complete_user_login(created_user, ask_save_state=True))
                else:
                    error_messages = {
                        "username_taken": "用户名已被占用",
                        "email_taken": "邮箱已被使用",
                        "invalid_username": "用户名格式无效",
                        "invalid_email": "邮箱格式无效",
                        "invalid_password": "密码格式无效",
                        "registration_disabled": "注册功能已禁用"
                    }
                    error_msg = error_messages.get(register_result.value, "注册失败")
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        f"❌ 注册失败: {error_msg}\n", 'error'
                    ))
                    self.root.after(2000, self._show_login_menu)
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "认证服务未初始化\n", 'error'
                ))
                self.root.after(2000, self._show_login_menu)
                
        except Exception as e:
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"❌ 注册过程出错: {e}\n", 'error'
            ))
            self.root.after(2000, self._show_login_menu)
            
    def _complete_user_login(self, user, save_state=False, ask_save_state=False):
        """完成用户登录 - 与console模式完全一致"""
        self.terminal_panel.append_output(f"✓ 登录成功! 欢迎回来, {user.username}!\n", 'success')
        
        # 处理登录状态保存
        if ask_save_state:
            self.terminal_panel.append_output("是否保留登录状态以便下次快速登录? (y/n): ", 'info')
            self.terminal_panel.set_login_mode(True, callback=lambda choice: self._handle_save_login_state(user, choice))
        elif save_state:
            self._save_login_state(user.username)
            self.terminal_panel.append_output("✓ 登录状态已保存\n", 'success')
            self._finish_login_process(user)
        else:
            # 如果用户选择不保存，清除可能存在的旧登录状态
            self._clear_login_state()
            self.terminal_panel.append_output("ℹ 登录状态未保存\n", 'info')
            self._finish_login_process(user)
            
    def _handle_save_login_state(self, user, choice: str):
        """处理保存登录状态的选择"""
        if choice.lower() == 'y':
            self._save_login_state(user.username)
            self.terminal_panel.append_output("✓ 登录状态已保存\n", 'success')
        else:
            # 如果用户选择不保存，清除可能存在的旧登录状态
            self._clear_login_state()
            self.terminal_panel.append_output("ℹ 登录状态未保存\n", 'info')
        self._finish_login_process(user)
        
    def _finish_login_process(self, user):
        """完成登录流程，进入游戏主界面"""
        user_data = {
            'username': user.username,
            'user_id': user.user_id,
            'balance': getattr(user, 'balance', 50000),
            'level': getattr(user, 'level', 5),
            'experience': getattr(user, 'experience', 250),
            'email': getattr(user, 'email', f'{user.username}@example.com')
        }
        self.on_login_success(user_data)
            
    def _handle_existing_login(self):
        """处理现有用户登录 - 与console模式完全一致"""
        self.terminal_panel.append_output("\n👤 用户登录\n", 'info')
        self.terminal_panel.append_output("用户名: ", 'system')
        self.terminal_panel.set_login_mode(True, callback=self._handle_existing_username)
        
    def _handle_existing_username(self, username: str):
        """处理现有用户登录的用户名输入"""
        username = username.strip()
        if not username:
            self.terminal_panel.append_output("❌ 用户名不能为空，请重新输入用户名: ", 'error')
            self.terminal_panel.set_login_mode(True, callback=self._handle_existing_username)
            return
            
        self.terminal_panel.append_output("密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_existing_password(username, pwd))
        
    def _handle_existing_password(self, username: str, password: str):
        """处理现有用户登录的密码输入"""
        password = password.strip()
        if not password:
            self.terminal_panel.append_output("❌ 密码不能为空，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_existing_password(username, pwd))
            return
            
        # 在异步线程中执行认证
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_existing_login(username, password),
                self.loop
            )
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    async def _async_existing_login(self, username: str, password: str):
        """异步执行现有用户登录"""
        try:
            if self.auth_service:
                auth_result, user = await self.auth_service.authenticate(username, password)
                if auth_result.value == "success" and user:
                    self.root.after(0, lambda u=user: self._complete_user_login(u, ask_save_state=True))
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
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        f"❌ {error_msg}\n", 'error'
                    ))
                    self.root.after(2000, self._show_login_menu)
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "认证服务未初始化\n", 'error'
                ))
                self.root.after(2000, self._show_login_menu)
                
        except Exception as e:
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"❌ 登录过程出错: {e}\n", 'error'
            ))
            self.root.after(2000, self._show_login_menu)
            
    def _handle_debug_login(self):
        """处理Debug测试登录 - 使用真实的AuthService"""
        self.terminal_panel.append_output("\n🔬 Debug测试登录\n", 'info')
        self.terminal_panel.append_output("使用预设账户: hahaha\n", 'system')
        
        # 直接使用预设的账户信息
        username = "hahaha"
        password = "hahaha"
        
        # 在异步线程中执行认证
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_debug_login(username, password),
                self.loop
            )
            # 不等待结果，让认证异步执行
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    async def _async_debug_login(self, username: str, password: str):
        """异步执行Debug登录"""
        try:
            # 尝试登录
            if self.auth_service:
                auth_result, user = await self.auth_service.authenticate(username, password)
                if auth_result.value == "success" and user:
                    # 在主线程中更新UI
                    self.root.after(0, lambda: self._complete_debug_login(user))
                    return
                else:
                    # 如果账户不存在，尝试注册
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        "Debug账户不存在，正在创建...\n", 'info'
                    ))
                    
                    # 创建Debug账户
                    register_result, created_user = await self.auth_service.register(
                        username, "debug@test.com", password
                    )
                    
                    if register_result.value == "success" and created_user:
                        self.root.after(0, lambda: self.terminal_panel.append_output(
                            "✓ Debug账户创建成功!\n", 'success'
                        ))
                        # 再次尝试登录
                        auth_result, user = await self.auth_service.authenticate(username, password)
                        if auth_result.value == "success" and user:
                            self.root.after(0, lambda: self._complete_debug_login(user))
                            return
                    
                    # 如果都失败了
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        "✗ Debug登录失败\n", 'error'
                    ))
                    self.root.after(2000, self._show_login_menu)
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "认证服务未初始化\n", 'error'
                ))
                self.root.after(2000, self._show_login_menu)
                
        except Exception as e:
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"✗ Debug登录过程出错: {e}\n", 'error'
            ))
            self.root.after(2000, self._show_login_menu)
            
    def _complete_debug_login(self, user):
        """完成Debug登录"""
        self.terminal_panel.append_output(f"✓ Debug登录成功! 欢迎, {user.username}!\n", 'success')
        
        user_data = {
            'username': user.username,
            'user_id': user.user_id,
            'balance': getattr(user, 'balance', 125000),
            'level': getattr(user, 'level', 15),
            'experience': getattr(user, 'experience', 1250),
            'email': getattr(user, 'email', 'debug@test.com')
        }
        self.on_login_success(user_data)
        
    def _handle_username_input(self, username: str):
        """处理用户名输入"""
        username = username.strip()
        if not username:
            self.terminal_panel.append_output("❌ 用户名不能为空，请重新输入: ", 'error')
            self.terminal_panel.set_login_mode(True, callback=self._handle_username_input)
            return
            
        self.terminal_panel.append_output("请输入密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_password_input(username, pwd))
        
    def _handle_password_input(self, username: str, password: str):
        """处理密码输入 - 使用真实的AuthService"""
        password = password.strip()
        if not password:
            self.terminal_panel.append_output("❌ 密码不能为空，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_password_input(username, pwd))
            return
            
        # 在异步线程中执行认证
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_authenticate_login(username, password),
                self.loop
            )
            # 不等待结果，让认证异步执行
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    async def _async_authenticate_login(self, username: str, password: str):
        """异步执行用户认证"""
        try:
            if self.auth_service:
                auth_result, user = await self.auth_service.authenticate(username, password)
                if auth_result.value == "success" and user:
                    # 在主线程中更新UI
                    self.root.after(0, lambda: self._complete_user_login(user))
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
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        f"❌ {error_msg}\n", 'error'
                    ))
                    self.root.after(2000, self._show_login_menu)
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "认证服务未初始化\n", 'error'
                ))
                self.root.after(2000, self._show_login_menu)
                
        except Exception as e:
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"❌ 登录过程出错: {e}\n", 'error'
            ))
            self.root.after(2000, self._show_login_menu)
            
    def _handle_register_username(self, username: str):
        """处理注册用户名输入"""
        username = username.strip()
        if not username:
            self.terminal_panel.append_output("❌ 用户名不能为空，请重新输入: ", 'error')
            self.terminal_panel.set_login_mode(True, callback=self._handle_register_username)
            return
            
        self.terminal_panel.append_output("请输入密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_password(username, pwd))
        
    def _handle_register_password(self, username: str, password: str):
        """处理注册密码输入"""
        password = password.strip()
        if not password:
            self.terminal_panel.append_output("❌ 密码不能为空，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_password(username, pwd))
            return
            
        self.terminal_panel.append_output("请确认密码: ", 'system')
        self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_confirm(username, password, pwd))
        
    def _handle_register_confirm(self, username: str, password: str, confirm: str):
        """处理注册确认密码 - 使用真实的AuthService"""
        confirm = confirm.strip()
        if password != confirm:
            self.terminal_panel.append_output("❌ 两次输入的密码不一致，请重新输入密码: ", 'error')
            self.terminal_panel.set_login_mode(True, password_mode=True, callback=lambda pwd: self._handle_register_password(username, pwd))
            return
            
        # 在异步线程中执行注册
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._async_register_user(username, password),
                self.loop
            )
            # 不等待结果，让注册异步执行
        else:
            self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...\n", 'warning')
            
    async def _async_register_user(self, username: str, password: str):
        """异步执行用户注册"""
        try:
            if self.auth_service:
                register_result, created_user = await self.auth_service.register(
                    username, f"{username}@example.com", password
                )
                
                if register_result.value == "success" and created_user:
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        "✓ 注册成功！正在自动登录...\n", 'success'
                    ))
                    # 注册成功后自动登录
                    self.root.after(1500, lambda: self._complete_user_login(created_user))
                else:
                    error_messages = {
                        "username_taken": "用户名已被占用",
                        "email_taken": "邮箱已被使用",
                        "invalid_username": "用户名格式无效",
                        "invalid_email": "邮箱格式无效",
                        "invalid_password": "密码格式无效",
                        "registration_disabled": "注册功能已禁用"
                    }
                    error_msg = error_messages.get(register_result.value, "注册失败")
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        f"❌ 注册失败: {error_msg}\n", 'error'
                    ))
                    self.root.after(2000, self._show_login_menu)
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "认证服务未初始化\n", 'error'
                ))
                self.root.after(2000, self._show_login_menu)
                
        except Exception as e:
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"❌ 注册过程出错: {e}\n", 'error'
            ))
            self.root.after(2000, self._show_login_menu)
        
    def on_login_success(self, user_data: Dict[str, Any]):
        """登录成功回调"""
        self.current_user = user_data
        self.is_logged_in = True
        
        # 更新界面状态
        self.header_bar.update_user_info(user_data)
        self.status_bar.update_user_status("已登录")
        
        # 清空终端并显示欢迎信息
        self.terminal_panel.clear_output()
        self.terminal_panel.append_output("\n🎉 登录成功！欢迎回来，{}！\n".format(user_data['username']), 'success')
        self.terminal_panel.append_output("🚀 系统正在初始化游戏服务...\n", 'info')
        
        # 退出登录模式
        self.terminal_panel.set_login_mode(False)
        
        # 启动游戏后台服务
        self._start_game_services()
        
    def _initialize_game_services(self):
        """初始化游戏服务"""
        try:
            # 初始化核心组件
            self.settings = Settings()
            self.event_bus = EventBus()
            
            # 初始化数据库
            self.db_engine = DatabaseEngine(self.settings)
            set_global_engine(self.db_engine)
            # 需要等待数据库初始化完成后获取sessionmaker
            # 这里先设为None，在异步初始化中设置
            self.uow = None
            
            # 所有服务都将在异步初始化中创建，避免主线程事件循环问题
            self.time_service = None
            self.auth_service = None
            self.currency_service = None
            self.app_service = None
            self.news_service = None
            self.stock_service = None
            
            # 命令分发器将在异步初始化中创建
            self.command_dispatcher = None
            
            # 更新状态栏
            if self.status_bar:
                self.status_bar.update_connection_status('connected', '游戏服务已就绪')
                
        except Exception as e:
            print(f"游戏服务初始化失败: {e}")
            if self.status_bar:
                self.status_bar.update_connection_status('disconnected', f'初始化失败: {e}')
            
    def _start_game_services(self):
        """启动游戏后台服务"""
        # 在新线程中启动异步事件循环
        if not self.loop_thread or not self.loop_thread.is_alive():
            self.loop_thread = threading.Thread(target=self._run_async_loop, daemon=True)
            self.loop_thread.start()
            
        # 异步初始化数据库和服务
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._async_initialize_services(),
                self.loop
            )
            
    async def _async_initialize_services(self):
        """异步初始化服务"""
        try:
            # 初始化数据库
            await self.db_engine.initialize()
            
            # 创建UnitOfWork
            self.uow = SqlAlchemyUnitOfWork(self.db_engine.sessionmaker)
            
            # 初始化时间服务（在异步线程中，避免主线程事件循环问题）
            self.time_service = TimeService(self.event_bus)
            
            # 设置GameTime（在异步线程中安全进行）
            from core.game_time import GameTime
            GameTime.set_time_service(self.time_service)
            
            # 重新初始化需要UnitOfWork的服务
            self.auth_service = AuthService(self.uow, self.event_bus)
            self.currency_service = CurrencyService(self.uow, self.event_bus)
            self.app_service = AppService(self.uow, self.event_bus, self.currency_service)
            self.news_service = NewsService(self.event_bus, self.time_service)
            self.stock_service = StockService(self.uow, self.event_bus, self.currency_service, self.time_service)
            
            # 重新初始化命令分发器（先不传递time_service，避免TimeCommands初始化问题）
            command_registry = CommandRegistry(
                auth_service=self.auth_service,
                app_service=self.app_service,
                news_service=self.news_service,
                stock_service=self.stock_service
                # 暂时不传递time_service
            )
            await command_registry.discover_commands()
            
            # 现在手动注册TimeCommands，确保GameTime已经设置
            if self.time_service:
                from commands.time_commands import TimeCommands
                time_commands = TimeCommands(time_service=self.time_service)
                command_registry.register_command(time_commands)
            
            self.command_dispatcher = CommandDispatcher(
                command_registry,
                self.auth_service,
                self.event_bus
            )
            
            # 启动时间服务
            if self.time_service:
                self.time_service.start()  # 移除await，因为start方法不是异步的
                
            print("游戏服务异步初始化完成")
            
            # 在主线程中通知用户系统就绪
            self.root.after(0, lambda: self.terminal_panel.append_output(
                "🎮 游戏服务已完全就绪！现在可以使用所有命令功能。", 'success'
            ))
            
        except Exception as e:
            print(f"异步服务初始化失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 在主线程中通知用户初始化失败
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"❌ 游戏服务初始化失败: {e}\n", 'error'
            ))
                
    def _run_async_loop(self):
        """运行异步事件循环"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            # 启动游戏的异步服务
            self.loop.run_forever()
        except Exception as e:
            print(f"异步循环错误: {e}")
        finally:
            self.loop.close()
            
    def execute_command(self, command: str):
        """执行游戏命令"""
        if not command.strip():
            return
            
        if not self.is_logged_in:
            # 未登录状态下，处理登录菜单选择
            if hasattr(self.terminal_panel, '_login_mode') and self.terminal_panel._login_mode:
                # 处理登录输入
                if hasattr(self.terminal_panel, '_login_callback') and self.terminal_panel._login_callback:
                    callback = self.terminal_panel._login_callback
                    self.terminal_panel.set_login_mode(False)  # 先退出登录模式
                    callback(command)
                else:
                    self._handle_login_choice(command)
            else:
                self.terminal_panel.append_output("❌ 错误: 请先登录系统", 'error')
                self.root.after(1000, self._show_login_menu)
            return
            
        try:
            # 使用实际的命令分发器
            if self.command_dispatcher and self.current_user:
                # 在异步循环中执行命令
                if self.loop and self.loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._execute_command_async(command),
                        self.loop
                    )
                    # 不等待结果，让命令异步执行
                else:
                    self.terminal_panel.append_output("⏳ 游戏服务正在初始化，请稍后再试...", 'warning')
            else:
                # 回退到基本命令处理
                self._handle_basic_commands(command)
                
        except Exception as e:
            self.terminal_panel.append_output(f"❌ 命令执行错误: {e}", 'error')
            
    async def _execute_command_async(self, command: str):
        """异步执行命令"""
        try:
            # 在主线程中更新UI
            self.root.after(0, lambda: self.terminal_panel.append_output(
                f"⚡ 执行命令: {command}", 'command', timestamp=False
            ))
            
            # 执行命令
            result = await self.command_dispatcher.dispatch(
                command,  # 传递完整的命令字符串
                self.current_user
            )
            
            # 在主线程中显示结果
            if result:
                if hasattr(result, 'success') and result.success:
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        result.message or "✅ 命令执行成功", 'success'
                    ))
                else:
                    self.root.after(0, lambda: self.terminal_panel.append_output(
                        result.message or "❌ 命令执行失败", 'error'
                    ))
            else:
                self.root.after(0, lambda: self.terminal_panel.append_output(
                    "✅ 命令执行完成", 'success'
                ))
                
        except Exception as e:
            # 在主线程中显示错误
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.terminal_panel.append_output(
                f"❌ 命令执行异常: {msg}", 'error'
            ))
            
    def _handle_basic_commands(self, command: str):
        """处理基本命令（回退方案）"""
        command = command.strip().lower()
        
        if command == "help":
            help_text = """
📋 可用命令:
  portfolio  - 查看投资组合
  market     - 查看市场行情
  news       - 查看财经新闻
  bank       - 银行操作
  stock      - 股票操作
  app        - 应用商店
  balance    - 查看余额
  status     - 系统状态
  quit/exit  - 退出系统
  clear      - 清空终端
            """
            self.terminal_panel.append_output(help_text, 'system')
            
        elif command in ['quit', 'exit']:
            self.on_closing()
            
        elif command == 'clear':
            self.terminal_panel.clear_output()
            
        elif command == 'portfolio':
            self.terminal_panel.append_output("📊 投资组合: 总价值 ¥125,000", 'success')
            
        elif command == 'market':
            self.terminal_panel.append_output("📈 市场状态: 开盘交易中", 'success')
            
        elif command == 'balance':
            self.terminal_panel.append_output("💰 账户余额: ¥50,000", 'success')
            
        elif command == 'status':
            self.terminal_panel.append_output("🟢 系统状态: 正常运行", 'success')
            
        else:
            self.terminal_panel.append_output(
                f"❓ 未知命令: {command}\n💡 输入 'help' 查看可用命令", 
                'warning'
            )
            
    def focus_sidebar(self):
        """聚焦侧边栏"""
        if self.sidebar:
            self.sidebar.focus()
            
    def focus_terminal(self):
        """聚焦终端"""
        if self.terminal_panel:
            self.terminal_panel.focus()
            
    def focus_right_panel(self):
        """聚焦右侧面板"""
        if self.right_panel_manager:
            self.right_panel_manager.focus()
            
    def toggle_terminal(self):
        """切换终端显示"""
        if self.terminal_panel:
            self.terminal_panel.toggle_visibility()
            
    def toggle_sidebar(self):
        """切换侧边栏显示"""
        if self.sidebar:
            self.sidebar.toggle_visibility()
            
    def show_help(self):
        """显示帮助信息"""
        help_text = """
Chips Battle Remake v3.0 Alpha - 快捷键帮助

Ctrl+1: 聚焦侧边栏
Ctrl+2: 聚焦终端
Ctrl+3: 聚焦右侧面板
Ctrl+`: 切换终端显示
Ctrl+B: 切换侧边栏显示
F1: 显示此帮助

游戏命令:
help - 显示命令帮助
portfolio - 查看投资组合
market - 查看市场信息
news - 查看新闻
bank - 银行操作
quit - 退出游戏
"""
        messagebox.showinfo("帮助", help_text)
        
    def on_window_resize(self, event):
        """窗口大小改变事件处理"""
        if event.widget == self.root:
            # 重新计算布局
            self.layout_manager.update_layout()
            
    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出游戏吗？"):
            # 停止异步循环
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
                
            # 关闭窗口
            self.root.destroy()
            
    def run(self):
        """运行GUI应用 - 与console模式完全一致"""
        print("[DEBUG] GUI run method called")
        # 先启动主循环
        # 通知状态栏主循环已启动
        if self.status_bar:
            self.status_bar.set_mainloop_started()
            print("[DEBUG] Status bar mainloop started")
        # 通知右侧面板管理器主循环已启动
        if self.right_panel_manager:
            self.right_panel_manager.set_mainloop_started()
            print("[DEBUG] Right panel manager mainloop started")
        
        # 启动异步事件循环
        print("[DEBUG] Starting async loop")
        self._start_async_loop()
        
        # 等待异步循环启动
        import time
        time.sleep(1)
        
        # 在异步循环中初始化游戏系统
        if self.loop and self.loop.is_running():
            print("[DEBUG] Scheduling game system initialization")
            asyncio.run_coroutine_threadsafe(self.initialize_game_system(), self.loop)
        else:
            print("[DEBUG] Async loop not running, initialization failed")
        
        # 启动主循环
        print("[DEBUG] Starting mainloop")
        self.root.mainloop()
        
    def _start_async_loop(self):
        """启动异步事件循环"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
            
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()

def run_gui():
    """启动GUI模式"""
    app = ChipsBattleGUI()
    app.run()

if __name__ == "__main__":
    run_gui()