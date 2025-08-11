# -*- coding: utf-8 -*-
"""
CLI适配器

实现控制台模式的UI适配器，基于rich和prompt_toolkit。
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import confirm, button_dialog

from interfaces.ui_interface import (
    GameUIInterface, UIType, MessageType, InputType, Message, InputRequest, ProgressInfo, UIAdapter
)


class ConsoleUIAdapter(GameUIInterface):
    """控制台UI适配器
    
    基于rich和prompt_toolkit实现的控制台界面适配器。
    提供丰富的终端显示和交互功能。
    """
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.session = PromptSession(history=FileHistory(os.path.expanduser('~/.chips_battle_history')))
        self.progress: Optional[Progress] = None
        self.progress_task_id: Optional[str] = None
        self._command_history: List[str] = []
        self._max_history = 1000
        
        # 颜色映射
        self._color_map = {
            MessageType.INFO: "dim",
            MessageType.SUCCESS: "green",
            MessageType.WARNING: "yellow",
            MessageType.ERROR: "red",
            MessageType.DEBUG: "blue",
            MessageType.COMMAND: "cyan",
            MessageType.SYSTEM: "bold"
        }
        
        # 符号映射
        self._symbol_map = {
            MessageType.INFO: "ℹ",
            MessageType.SUCCESS: "✓",
            MessageType.WARNING: "⚠",
            MessageType.ERROR: "✗",
            MessageType.DEBUG: "🐛",
            MessageType.COMMAND: "⚡",
            MessageType.SYSTEM: "🎮"
        }
    
    @property
    def ui_type(self) -> UIType:
        """获取UI类型
        
        Returns:
            UI类型
        """
        return UIType.CONSOLE
    
    async def initialize(self) -> bool:
        """初始化控制台UI
        
        Returns:
            是否初始化成功
        """
        try:
            self.logger.info("正在初始化控制台UI适配器")
            
            # 检查终端支持
            if not self._check_terminal_support():
                self.logger.error("终端不支持必要的功能")
                return False
            
            # 清空屏幕
            self.clear_screen()
            
            # 显示欢迎信息
            self._show_welcome_banner()
            
            self._is_running = True
            self.logger.info("控制台UI适配器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"控制台UI适配器初始化失败: {e}", exc_info=True)
            return False
    
    async def cleanup(self):
        """清理控制台UI资源"""
        try:
            self.logger.info("正在清理控制台UI适配器")
            
            # 隐藏进度条
            self.hide_progress()
            
            # 显示退出信息
            self.display_system("\n感谢使用 Chips Battle！再见！")
            
            self._is_running = False
            self.logger.info("控制台UI适配器清理完成")
            
        except Exception as e:
            self.logger.error(f"控制台UI适配器清理失败: {e}", exc_info=True)
    
    def _check_terminal_support(self) -> bool:
        """检查终端支持
        
        Returns:
            终端是否支持必要功能
        """
        try:
            # 检查是否支持颜色输出
            self.console.print("[green]测试颜色输出[/green]")
            
            # 检查是否支持Unicode
            self.console.print("🎮 测试Unicode输出")
            
            return True
        except Exception:
            return False
    
    def _show_welcome_banner(self):
        """显示欢迎横幅"""
        try:
            # 尝试加载配置文件
            config_file = Path(__file__).parent.parent / "data" / "config.json"
            game_config = {}
            banner_config = {}
            
            if config_file.exists():
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    game_config = config_data.get('game', {})
                    banner_config = config_data.get('banner', {})
            
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
            
        except Exception as e:
            self.logger.error(f"显示欢迎横幅失败: {e}", exc_info=True)
            # 显示简化的欢迎信息
            self.console.print("\n[bold green]🎮 欢迎来到 Chips Battle![/bold green]\n")
    
    def display_message(self, message: Message):
        """显示消息
        
        Args:
            message: 消息内容
        """
        try:
            # 构建消息文本
            text_parts = []
            
            # 添加时间戳
            if message.timestamp:
                timestamp = datetime.now().strftime("%H:%M:%S")
                text_parts.append(f"[{message.style}]{timestamp}[/]")
            
            # 添加符号
            symbol = self._symbol_map.get(message.type, "•")
            text_parts.append(f"[{message.style}]{symbol}[/]")
            
            # 添加消息内容
            text_parts.append(f"[{message.style}]{message.content}[/]")
            
            # 组合并显示
            message_text = " ".join(text_parts)
            self.console.print(message_text)
            
        except Exception as e:
            self.logger.error(f"显示消息失败: {e}", exc_info=True)
            # 简化显示
            print(message.content)
    
    async def get_input(self, request: InputRequest) -> str:
        """获取用户输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户输入的值
        """
        try:
            if request.input_type == InputType.TEXT:
                return await self._get_text_input(request)
            elif request.input_type == InputType.PASSWORD:
                return await self._get_password_input(request)
            elif request.input_type == InputType.NUMBER:
                return await self._get_number_input(request)
            elif request.input_type == InputType.CHOICE:
                return await self._get_choice_input(request)
            elif request.input_type == InputType.CONFIRM:
                return await self._get_confirm_input(request)
            else:
                raise ValueError(f"不支持的输入类型: {request.input_type}")
                
        except Exception as e:
            self.logger.error(f"获取用户输入失败: {e}", exc_info=True)
            return ""
    
    async def _get_text_input(self, request: InputRequest) -> str:
        """获取文本输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户输入的文本
        """
        prompt = request.prompt
        if request.default:
            prompt += f" [{request.default}]"
        
        result = await self.session.prompt_async(prompt + ": ")
        
        # 如果用户没有输入且存在默认值，则使用默认值
        if not result and request.default:
            return request.default
        
        return result
    
    async def _get_password_input(self, request: InputRequest) -> str:
        """获取密码输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户输入的密码
        """
        return await self.session.prompt_async(request.prompt + ": ", password=True)
    
    async def _get_number_input(self, request: InputRequest) -> str:
        """获取数字输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户输入的数字
        """
        while True:
            result = await self._get_text_input(request)
            
            # 验证是否为数字
            if result.isdigit():
                return result
            else:
                self.display_error("请输入有效的数字")
    
    async def _get_choice_input(self, request: InputRequest) -> str:
        """获取选择输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户选择的结果
        """
        if not request.choices:
            raise ValueError("选择输入必须提供选项列表")
        
        # 显示选项
        self.display_info("请选择:")
        for i, choice in enumerate(request.choices, 1):
            self.display_info(f"  {i}. {choice}")
        
        # 获取用户选择
        while True:
            result = await self._get_text_input(InputRequest("请输入选项序号"))
            
            try:
                index = int(result) - 1
                if 0 <= index < len(request.choices):
                    return request.choices[index]
                else:
                    self.display_error(f"请输入 1-{len(request.choices)} 之间的数字")
            except ValueError:
                self.display_error("请输入有效的数字")
    
    async def _get_confirm_input(self, request: InputRequest) -> str:
        """获取确认输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户确认的结果
        """
        default_yes = request.default and request.default.lower() in ['y', 'yes']
        
        result = await confirm(
            request.prompt,
            default=default_yes
        )
        
        return 'y' if result else 'n'
    
    def show_progress(self, progress: ProgressInfo):
        """显示进度
        
        Args:
            progress: 进度信息
        """
        try:
            # 如果已经有进度条，先隐藏
            if self.progress:
                self.hide_progress()
            
            # 创建新的进度条
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            )
            
            # 添加任务
            self.progress_task_id = self.progress.add_task(
                progress.description,
                total=progress.total,
                completed=progress.current
            )
            
            # 启动进度条
            self.progress.start()
            
        except Exception as e:
            self.logger.error(f"显示进度失败: {e}", exc_info=True)
            # 简化显示
            self.display_info(f"{progress.description}: {progress.current}/{progress.total}")
    
    def hide_progress(self):
        """隐藏进度条"""
        try:
            if self.progress:
                self.progress.stop()
                self.progress = None
                self.progress_task_id = None
        except Exception as e:
            self.logger.error(f"隐藏进度条失败: {e}", exc_info=True)
    
    def update_progress(self, current: int, total: int = None):
        """更新进度
        
        Args:
            current: 当前进度
            total: 总进度（可选）
        """
        try:
            if self.progress and self.progress_task_id is not None:
                if total is not None:
                    self.progress.update(self.progress_task_id, total=total)
                self.progress.update(self.progress_task_id, completed=current)
        except Exception as e:
            self.logger.error(f"更新进度失败: {e}", exc_info=True)
    
    def clear_screen(self):
        """清空屏幕"""
        try:
            # 使用rich清空屏幕
            self.console.clear()
        except Exception:
            # 回退到系统清屏
            os.system('cls' if os.name == 'nt' else 'clear')
    
    async def run_main_loop(self):
        """运行主循环
        
        控制台模式的主循环通常由外部控制，这里只做标记
        """
        self._is_running = True
        self.logger.info("控制台主循环开始")
        
        # 触发主循环开始事件
        self.emit_event("main_loop_started")
    
    def stop_main_loop(self):
        """停止主循环"""
        self._is_running = False
        self.logger.info("控制台主循环停止")
        
        # 触发主循环停止事件
        self.emit_event("main_loop_stopped")
    
    def add_to_history(self, command: str):
        """添加命令到历史记录
        
        Args:
            command: 命令内容
        """
        if command.strip():
            self._command_history.append(command)
            if len(self._command_history) > self._max_history:
                self._command_history.pop(0)
    
    def get_history(self) -> List[str]:
        """获取命令历史记录
        
        Returns:
            命令历史记录列表
        """
        return self._command_history.copy()
    
    def clear_history(self):
        """清空命令历史记录"""
        self._command_history.clear()
        
        # 清空历史文件
        history_file = os.path.expanduser('~/.chips_battle_history')
        try:
            if os.path.exists(history_file):
                os.remove(history_file)
        except Exception as e:
            self.logger.error(f"清空历史文件失败: {e}", exc_info=True)


class ConsoleAdapter(UIAdapter):
    """控制台适配器
    
    为控制台模式提供便捷的适配器类。
    """
    
    def __init__(self):
        ui_interface = ConsoleUIAdapter()
        super().__init__(ui_interface)
    
    async def get_command_input(self, prompt: str = "") -> str:
        """获取命令输入
        
        Args:
            prompt: 提示信息
            
        Returns:
            用户输入的命令
        """
        result = await self.ui.session.prompt_async(prompt)
        
        # 添加到历史记录
        self.ui.add_to_history(result)
        
        return result
    
    def show_startup_banner(self):
        """显示启动横幅"""
        self.ui._show_welcome_banner()
    
    def show_login_menu(self, has_saved_login: bool = False) -> str:
        """显示登录菜单
        
        Args:
            has_saved_login: 是否有保存的登录状态
            
        Returns:
            用户选择的结果
        """
        # 显示选项
        self.ui.display_info("\n请选择操作:")
        
        options = []
        if has_saved_login:
            options.append("0. 登录上次账户")
        options.extend([
            "1. 登录现有账户",
            "2. 注册新账户",
            "3. 退出游戏",
            "4. Debug测试 (hahaha账户)"
        ])
        
        for option in options:
            self.ui.display_info(option)
        
        # 获取用户选择
        if has_saved_login:
            return asyncio.run(self.ui.get_choice_input(
                "请输入选项 (0-4)",
                ["0", "1", "2", "3", "4"]
            ))
        else:
            return asyncio.run(self.ui.get_choice_input(
                "请输入选项 (1-4)",
                ["1", "2", "3", "4"]
            ))
    
    def show_command_prompt(self, username: str) -> str:
        """显示命令提示符
        
        Args:
            username: 用户名
            
        Returns:
            用户输入的命令
        """
        prompt = f"{username}@ChipsBattle$ "
        return asyncio.run(self.get_command_input(prompt))
    
    def show_game_over(self):
        """显示游戏结束信息"""
        self.ui.display_system("\n游戏结束，感谢游玩！")
    
    def show_error_exit(self, error: str):
        """显示错误退出信息
        
        Args:
            error: 错误信息
        """
        self.ui.display_error(f"\n程序错误退出: {error}")