# -*- coding: utf-8 -*-
"""
界面控制命令

提供控制台界面相关的命令功能。
"""

import os
import sys
from typing import List
from commands.base import Command, CommandResult, CommandContext
from rich.console import Console
from rich.text import Text


class UICommand(Command):
    """界面控制命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "cls"
    
    @property
    def aliases(self) -> List[str]:
        return ["clear", "clean", "clr"]
    
    @property
    def description(self) -> str:
        return "清屏命令 - 清除控制台内容"
    
    @property
    def category(self) -> str:
        return "系统"
    
    @property
    def usage(self) -> str:
        return f"{self.name} [--verbose]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行清屏命令"""
        try:
            # 清除控制台内容
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Unix/Linux/MacOS
                os.system('clear')
            
            # 使用Rich清屏（备用方案）
            self.console.clear()
            
            # 可选：显示清屏完成提示
            if args and ("--verbose" in args or "-v" in args):
                success_text = Text("✨ 控制台已清屏", style="green")
                self.console.print(success_text)
                return CommandResult(
                    success=True,
                    message="✨ 控制台已清屏"
                )
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"清屏失败: {str(e)}")


class EchoCommand(Command):
    """输出文本命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "echo"
    
    @property
    def aliases(self) -> List[str]:
        return ["print", "say"]
    
    @property
    def description(self) -> str:
        return "输出文本到控制台"
    
    @property
    def category(self) -> str:
        return "系统"
    
    @property
    def usage(self) -> str:
        return f"{self.name} <文本内容>"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行输出命令"""
        try:
            if not args:
                return self.format_error("请提供要输出的文本内容")
            
            # 合并所有参数为文本
            text = " ".join(args)
            
            # 输出文本
            self.console.print(text)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"输出失败: {str(e)}")


class ColorCommand(Command):
    """设置控制台颜色命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "color"
    
    @property
    def aliases(self) -> List[str]:
        return ["colour"]
    
    @property
    def description(self) -> str:
        return "设置控制台文本颜色"
    
    @property
    def category(self) -> str:
        return "系统"
    
    @property
    def usage(self) -> str:
        return f"{self.name} <颜色名称>"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行颜色设置命令"""
        try:
            if not args:
                # 显示可用颜色
                colors = ["red", "green", "blue", "yellow", "magenta", "cyan", "white", "black"]
                color_text = Text("可用颜色: ", style="bold")
                for color in colors:
                    color_text.append(f"{color} ", style=color)
                
                self.console.print(color_text)
                return CommandResult(success=True, message="")
            
            color = args[0].lower()
            
            # 测试颜色输出
            test_text = Text(f"当前颜色设置为: {color}", style=color)
            self.console.print(test_text)
            
            return CommandResult(
                success=True,
                message=f"颜色已设置为: {color}"
            )
            
        except Exception as e:
            return self.format_error(f"颜色设置失败: {str(e)}")