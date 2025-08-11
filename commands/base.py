# -*- coding: utf-8 -*-
"""
命令系统基类

定义所有命令的抽象基类和通用功能。
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    message: str = ""
    data: Dict[str, Any] = None
    action: Optional[str] = None  # 特殊操作，如 'quit', 'login', etc.
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class CommandContext:
    """命令执行上下文"""
    user: Any  # User对象
    session_data: Dict[str, Any] = None
    game_time: Optional[datetime] = None
    registry: Any = None  # CommandRegistry对象
    
    def __post_init__(self):
        if self.session_data is None:
            self.session_data = {}


class Command(ABC):
    """命令抽象基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """命令名称"""
        pass
    
    @property
    def aliases(self) -> List[str]:
        """命令别名列表"""
        return []
    
    @property
    @abstractmethod
    def description(self) -> str:
        """命令描述"""
        pass
    
    @property
    def usage(self) -> str:
        """命令使用方法"""
        return f"{self.name}"
    
    @property
    def category(self) -> str:
        """命令分类"""
        return "general"
    
    @property
    def required_permissions(self) -> List[str]:
        """所需权限列表"""
        return []
    
    @property
    def is_admin_only(self) -> bool:
        """是否仅管理员可用"""
        return False
    
    @abstractmethod
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行命令
        
        Args:
            args: 命令参数列表
            context: 命令执行上下文
            
        Returns:
            命令执行结果
        """
        pass
    
    def validate_args(self, args: List[str]) -> bool:
        """验证命令参数
        
        Args:
            args: 命令参数列表
            
        Returns:
            参数是否有效
        """
        return True
    
    def get_help(self) -> str:
        """获取命令帮助信息"""
        help_text = f"**{self.name}** - {self.description}\n"
        help_text += f"用法: {self.usage}\n"
        
        if self.aliases:
            help_text += f"别名: {', '.join(self.aliases)}\n"
        
        if self.required_permissions:
            help_text += f"所需权限: {', '.join(self.required_permissions)}\n"
        
        if self.is_admin_only:
            help_text += "⚠️ 仅管理员可用\n"
        
        return help_text
    
    def format_error(self, message: str) -> CommandResult:
        """格式化错误结果
        
        Args:
            message: 错误消息
            
        Returns:
            错误结果
        """
        self.logger.warning(f"命令执行失败: {message}")
        return CommandResult(success=False, message=f"❌ {message}")
    
    def format_success(self, message: str, data: Dict[str, Any] = None) -> CommandResult:
        """格式化成功结果
        
        Args:
            message: 成功消息
            data: 附加数据
            
        Returns:
            成功结果
        """
        self.logger.info(f"命令执行成功: {message}")
        return CommandResult(success=True, message=f"✅ {message}", data=data or {})
    
    def format_info(self, message: str, data: Dict[str, Any] = None) -> CommandResult:
        """格式化信息结果
        
        Args:
            message: 信息消息
            data: 附加数据
            
        Returns:
            信息结果
        """
        return CommandResult(success=True, message=message, data=data or {})
    
    # Convenience methods for easier usage
    def error(self, message: str) -> CommandResult:
        """便捷错误方法"""
        return self.format_error(message)
    
    def success(self, message: str, data: Dict[str, Any] = None) -> CommandResult:
        """便捷成功方法"""
        return self.format_success(message, data)
    
    def info(self, message: str, data: Dict[str, Any] = None) -> CommandResult:
        """便捷信息方法"""
        return self.format_info(message, data)


class AdminCommand(Command):
    """管理员命令基类"""
    
    @property
    def is_admin_only(self) -> bool:
        return True
    
    @property
    def required_permissions(self) -> List[str]:
        return ["admin"]
    
    @property
    def category(self) -> str:
        return "admin"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行管理员命令，先检查权限"""
        # 检查管理员权限
        if hasattr(context, 'user_manager') and context.user_manager:
            is_admin = await context.user_manager.is_admin(context.user)
            if not is_admin:
                return CommandResult(
                    success=False,
                    message="权限不足"
                )
        
        # 调用子类的具体实现
        return await self._execute_admin_command(args, context)
    
    @abstractmethod
    async def _execute_admin_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """子类需要实现的具体管理员命令逻辑"""
        pass


class FinanceCommand(Command):
    """金融命令基类"""
    
    @property
    def category(self) -> str:
        return "finance"


class AppCommand(Command):
    """应用命令基类"""
    
    @property
    def category(self) -> str:
        return "apps"


class StockCommand(Command):
    """股票命令基类"""
    
    @property
    def category(self) -> str:
        return "stock"


class NewsCommand(Command):
    """新闻命令基类"""
    
    @property
    def category(self) -> str:
        return "news"


class BasicCommand(Command):
    """基础命令基类"""
    
    @property
    def category(self) -> str:
        return "basic"




class CommandParser:
    """命令解析器"""
    
    @staticmethod
    def parse(command_input: str) -> tuple[str, List[str]]:
        """解析命令输入
        
        Args:
            command_input: 用户输入的命令字符串
            
        Returns:
            (命令名, 参数列表)
        """
        if not command_input.strip():
            return "", []
        
        parts = command_input.strip().split()
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command_name, args
    
    @staticmethod
    def parse_flags(args: List[str]) -> tuple[List[str], Dict[str, Union[str, bool]]]:
        """解析命令标志
        
        Args:
            args: 参数列表
            
        Returns:
            (位置参数列表, 标志字典)
        """
        positional_args = []
        flags = {}
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--'):
                # 长标志 --flag=value 或 --flag value
                if '=' in arg:
                    flag_name, flag_value = arg[2:].split('=', 1)
                    flags[flag_name] = flag_value
                else:
                    flag_name = arg[2:]
                    if i + 1 < len(args) and not args[i + 1].startswith('-'):
                        flags[flag_name] = args[i + 1]
                        i += 1
                    else:
                        flags[flag_name] = True
            elif arg.startswith('-') and len(arg) > 1:
                # 短标志 -f value 或 -f
                flag_name = arg[1:]
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    flags[flag_name] = args[i + 1]
                    i += 1
                else:
                    flags[flag_name] = True
            else:
                # 位置参数
                positional_args.append(arg)
            
            i += 1
        
        return positional_args, flags
    
    @staticmethod
    def format_args_help(required_args: List[str], optional_args: List[str] = None) -> str:
        """格式化参数帮助信息
        
        Args:
            required_args: 必需参数列表
            optional_args: 可选参数列表
            
        Returns:
            格式化的参数帮助
        """
        help_parts = []
        
        for arg in required_args:
            help_parts.append(f"<{arg}>")
        
        if optional_args:
            for arg in optional_args:
                help_parts.append(f"[{arg}]")
        
        return " ".join(help_parts)