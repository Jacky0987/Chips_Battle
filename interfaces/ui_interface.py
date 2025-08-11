# -*- coding: utf-8 -*-
"""
UI接口抽象层

定义统一的UI接口，支持CLI和GUI两种模式的适配器模式。
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass


class UIType(Enum):
    """UI类型枚举"""
    CONSOLE = "console"
    GUI = "gui"


class MessageType(Enum):
    """消息类型枚举"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    COMMAND = "command"
    SYSTEM = "system"


class InputType(Enum):
    """输入类型枚举"""
    TEXT = "text"
    PASSWORD = "password"
    NUMBER = "number"
    CHOICE = "choice"
    CONFIRM = "confirm"


@dataclass
class Message:
    """UI消息数据类"""
    content: str
    type: MessageType = MessageType.INFO
    timestamp: bool = True
    style: Optional[str] = None
    
    def __post_init__(self):
        if self.style is None:
            # 根据消息类型设置默认样式
            self.style = {
                MessageType.INFO: "dim",
                MessageType.SUCCESS: "green",
                MessageType.WARNING: "yellow",
                MessageType.ERROR: "red",
                MessageType.DEBUG: "blue",
                MessageType.COMMAND: "cyan",
                MessageType.SYSTEM: "bold"
            }.get(self.type, "dim")


@dataclass
class InputRequest:
    """输入请求数据类"""
    prompt: str
    input_type: InputType = InputType.TEXT
    default: Optional[str] = None
    choices: Optional[List[str]] = None
    validator: Optional[Callable[[str], bool]] = None
    error_message: Optional[str] = None


@dataclass
class ProgressInfo:
    """进度信息数据类"""
    description: str
    current: int = 0
    total: int = 100
    unit: str = "%"
    
    @property
    def percentage(self) -> float:
        """获取进度百分比"""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100


class GameUIInterface(ABC):
    """游戏UI接口基类
    
    定义了所有UI模式必须实现的基本方法。
    支持CLI和GUI两种模式的统一接口。
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_running = False
        self._event_handlers: Dict[str, List[Callable]] = {}
    
    @property
    @abstractmethod
    def ui_type(self) -> UIType:
        """获取UI类型
        
        Returns:
            UI类型
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化UI
        
        Returns:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """清理UI资源"""
        pass
    
    @abstractmethod
    def display_message(self, message: Message):
        """显示消息
        
        Args:
            message: 消息内容
        """
        pass
    
    @abstractmethod
    async def get_input(self, request: InputRequest) -> str:
        """获取用户输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户输入的值
        """
        pass
    
    @abstractmethod
    def show_progress(self, progress: ProgressInfo):
        """显示进度
        
        Args:
            progress: 进度信息
        """
        pass
    
    @abstractmethod
    def hide_progress(self):
        """隐藏进度条"""
        pass
    
    @abstractmethod
    def clear_screen(self):
        """清空屏幕"""
        pass
    
    @abstractmethod
    async def run_main_loop(self):
        """运行主循环"""
        pass
    
    @abstractmethod
    def stop_main_loop(self):
        """停止主循环"""
        pass
    
    def display_info(self, content: str, timestamp: bool = True):
        """显示信息消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.INFO, timestamp))
    
    def display_success(self, content: str, timestamp: bool = True):
        """显示成功消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.SUCCESS, timestamp))
    
    def display_warning(self, content: str, timestamp: bool = True):
        """显示警告消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.WARNING, timestamp))
    
    def display_error(self, content: str, timestamp: bool = True):
        """显示错误消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.ERROR, timestamp))
    
    def display_debug(self, content: str, timestamp: bool = True):
        """显示调试消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.DEBUG, timestamp))
    
    def display_command(self, content: str, timestamp: bool = False):
        """显示命令消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.COMMAND, timestamp))
    
    def display_system(self, content: str, timestamp: bool = True):
        """显示系统消息
        
        Args:
            content: 消息内容
            timestamp: 是否显示时间戳
        """
        self.display_message(Message(content, MessageType.SYSTEM, timestamp))
    
    async def get_text_input(self, prompt: str, default: str = None) -> str:
        """获取文本输入
        
        Args:
            prompt: 提示信息
            default: 默认值
            
        Returns:
            用户输入的文本
        """
        return await self.get_input(InputRequest(prompt, InputType.TEXT, default))
    
    async def get_password_input(self, prompt: str) -> str:
        """获取密码输入
        
        Args:
            prompt: 提示信息
            
        Returns:
            用户输入的密码
        """
        return await self.get_input(InputRequest(prompt, InputType.PASSWORD))
    
    async def get_number_input(self, prompt: str, default: int = None) -> str:
        """获取数字输入
        
        Args:
            prompt: 提示信息
            default: 默认值
            
        Returns:
            用户输入的数字
        """
        return await self.get_input(InputRequest(prompt, InputType.NUMBER, str(default) if default is not None else None))
    
    async def get_choice_input(self, prompt: str, choices: List[str], default: str = None) -> str:
        """获取选择输入
        
        Args:
            prompt: 提示信息
            choices: 选择列表
            default: 默认值
            
        Returns:
            用户选择的结果
        """
        return await self.get_input(InputRequest(prompt, InputType.CHOICE, default, choices))
    
    async def get_confirm_input(self, prompt: str, default: bool = False) -> str:
        """获取确认输入
        
        Args:
            prompt: 提示信息
            default: 默认值
            
        Returns:
            用户确认的结果
        """
        return await self.get_input(InputRequest(prompt, InputType.CONFIRM, "y" if default else "n"))
    
    def show_progress_bar(self, description: str, current: int = 0, total: int = 100):
        """显示进度条
        
        Args:
            description: 描述信息
            current: 当前进度
            total: 总进度
        """
        self.show_progress(ProgressInfo(description, current, total))
    
    def update_progress(self, current: int, total: int = None):
        """更新进度
        
        Args:
            current: 当前进度
            total: 总进度（可选）
        """
        # 这里需要保存当前的进度信息，简化实现
        pass
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """添加事件处理器
        
        Args:
            event_type: 事件类型
            handler: 事件处理器
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable):
        """移除事件处理器
        
        Args:
            event_type: 事件类型
            handler: 事件处理器
        """
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def emit_event(self, event_type: str, *args, **kwargs):
        """触发事件
        
        Args:
            event_type: 事件类型
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(*args, **kwargs))
                    else:
                        handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"事件处理器执行失败: {e}", exc_info=True)
    
    def is_running(self) -> bool:
        """检查UI是否在运行
        
        Returns:
            是否在运行
        """
        return self._is_running
    
    def __str__(self):
        return f"{self.__class__.__name__}(type={self.ui_type.value}, running={self._is_running})"


class UIAdapter:
    """UI适配器基类
    
    提供UI接口的默认实现，子类可以重写需要的方法。
    """
    
    def __init__(self, ui_interface: GameUIInterface):
        self.ui = ui_interface
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self) -> bool:
        """初始化适配器
        
        Returns:
            是否初始化成功
        """
        return await self.ui.initialize()
    
    async def cleanup(self):
        """清理适配器资源"""
        await self.ui.cleanup()
    
    def display_message(self, message: Message):
        """显示消息"""
        self.ui.display_message(message)
    
    async def get_input(self, request: InputRequest) -> str:
        """获取用户输入"""
        return await self.ui.get_input(request)
    
    def show_progress(self, progress: ProgressInfo):
        """显示进度"""
        self.ui.show_progress(progress)
    
    def hide_progress(self):
        """隐藏进度条"""
        self.ui.hide_progress()
    
    def clear_screen(self):
        """清空屏幕"""
        self.ui.clear_screen()
    
    async def run_main_loop(self):
        """运行主循环"""
        await self.ui.run_main_loop()
    
    def stop_main_loop(self):
        """停止主循环"""
        self.ui.stop_main_loop()
    
    # 便捷方法
    def display_info(self, content: str, timestamp: bool = True):
        """显示信息消息"""
        self.ui.display_info(content, timestamp)
    
    def display_success(self, content: str, timestamp: bool = True):
        """显示成功消息"""
        self.ui.display_success(content, timestamp)
    
    def display_warning(self, content: str, timestamp: bool = True):
        """显示警告消息"""
        self.ui.display_warning(content, timestamp)
    
    def display_error(self, content: str, timestamp: bool = True):
        """显示错误消息"""
        self.ui.display_error(content, timestamp)
    
    def display_debug(self, content: str, timestamp: bool = True):
        """显示调试消息"""
        self.ui.display_debug(content, timestamp)
    
    def display_command(self, content: str, timestamp: bool = False):
        """显示命令消息"""
        self.ui.display_command(content, timestamp)
    
    def display_system(self, content: str, timestamp: bool = True):
        """显示系统消息"""
        self.ui.display_system(content, timestamp)
    
    async def get_text_input(self, prompt: str, default: str = None) -> str:
        """获取文本输入"""
        return await self.ui.get_text_input(prompt, default)
    
    async def get_password_input(self, prompt: str) -> str:
        """获取密码输入"""
        return await self.ui.get_password_input(prompt)
    
    async def get_number_input(self, prompt: str, default: int = None) -> str:
        """获取数字输入"""
        return await self.ui.get_number_input(prompt, default)
    
    async def get_choice_input(self, prompt: str, choices: List[str], default: str = None) -> str:
        """获取选择输入"""
        return await self.ui.get_choice_input(prompt, choices, default)
    
    async def get_confirm_input(self, prompt: str, default: bool = False) -> str:
        """获取确认输入"""
        return await self.ui.get_confirm_input(prompt, default)
    
    def show_progress_bar(self, description: str, current: int = 0, total: int = 100):
        """显示进度条"""
        self.ui.show_progress_bar(description, current, total)
    
    def update_progress(self, current: int, total: int = None):
        """更新进度"""
        self.ui.update_progress(current, total)
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """添加事件处理器"""
        self.ui.add_event_handler(event_type, handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable):
        """移除事件处理器"""
        self.ui.remove_event_handler(event_type, handler)
    
    def emit_event(self, event_type: str, *args, **kwargs):
        """触发事件"""
        self.ui.emit_event(event_type, *args, **kwargs)
    
    def is_running(self) -> bool:
        """检查UI是否在运行"""
        return self.ui.is_running()
    
    def __str__(self):
        return f"{self.__class__.__name__}(ui={self.ui})"