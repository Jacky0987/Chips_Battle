# -*- coding: utf-8 -*-
"""
日志系统命令

提供日志查看、管理和配置功能。
"""

import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from commands.base import Command, CommandResult, CommandContext
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax


class LogCommand(Command):
    """日志系统主命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.log_file = "logs/game.log"  # 默认日志文件路径
        self.max_lines = 50  # 默认显示行数
    
    @property
    def name(self) -> str:
        return "log"
    
    @property
    def aliases(self) -> List[str]:
        return ["logs"]
    
    @property
    def description(self) -> str:
        return "日志系统管理命令"
    
    @property
    def category(self) -> str:
        return "系统"
    
    @property
    def usage(self) -> str:
        return f"{self.name} [show|error|warn|info|debug|clear|save|level|filter|search|config] [参数]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行日志命令"""
        try:
            if not args:
                # 默认显示最新日志
                return await self._show_logs()
            
            subcommand = args[0].lower()
            sub_args = args[1:] if len(args) > 1 else []
            
            if subcommand in ["help", "h", "?"]:
                return await self._show_help()
            
            if subcommand in ["show", "tail"]:
                return await self._show_logs(sub_args)
            elif subcommand in ["error", "err"]:
                return await self._show_logs_by_level("ERROR")
            elif subcommand in ["warn", "warning"]:
                return await self._show_logs_by_level("WARNING")
            elif subcommand == "info":
                return await self._show_logs_by_level("INFO")
            elif subcommand in ["debug", "dbg"]:
                return await self._show_logs_by_level("DEBUG")
            elif subcommand in ["clear", "clean", "cls"]:
                return await self._clear_logs()
            elif subcommand in ["save", "export"]:
                return await self._save_logs(sub_args)
            elif subcommand in ["level", "setlevel"]:
                return await self._set_log_level(sub_args)
            elif subcommand in ["filter", "grep"]:
                return await self._filter_logs(sub_args)
            elif subcommand in ["search", "find"]:
                return await self._search_logs(sub_args)
            elif subcommand in ["config", "settings"]:
                return await self._show_config()
            elif subcommand in ["rotate", "roll"]:
                return await self._rotate_logs()
            elif subcommand == "size":
                return await self._show_log_size()
            else:
                return self.format_error(f"未知的日志子命令: {subcommand}")
                
        except Exception as e:
            return self.format_error(f"日志命令执行失败: {str(e)}")
    
    async def _show_logs(self, args: List[str] = None) -> CommandResult:
        """显示日志"""
        try:
            lines = self.max_lines
            if args and args[0].isdigit():
                lines = int(args[0])
                lines = min(lines, 200)  # 限制最大行数
            
            # 尝试读取日志文件
            log_content = self._read_log_file(lines)
            
            if not log_content:
                return self.format_info("暂无日志内容")
            
            # 显示日志
            panel = Panel(
                log_content,
                title=f"📋 最新 {lines} 行日志",
                border_style="blue"
            )
            self.console.print(panel)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"读取日志失败: {str(e)}")
    
    async def _show_logs_by_level(self, level: str) -> CommandResult:
        """按级别显示日志"""
        try:
            log_content = self._read_log_file(self.max_lines)
            
            if not log_content:
                return self.format_info("暂无日志内容")
            
            # 过滤指定级别的日志
            filtered_lines = []
            for line in log_content.split('\n'):
                if level in line:
                    filtered_lines.append(line)
            
            if not filtered_lines:
                return self.format_info(f"暂无 {level} 级别的日志")
            
            filtered_content = '\n'.join(filtered_lines[-self.max_lines:])
            
            # 根据级别设置颜色
            color = {
                "ERROR": "red",
                "WARNING": "yellow", 
                "INFO": "green",
                "DEBUG": "blue"
            }.get(level, "white")
            
            panel = Panel(
                filtered_content,
                title=f"📋 {level} 级别日志",
                border_style=color
            )
            self.console.print(panel)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"读取 {level} 日志失败: {str(e)}")
    
    async def _clear_logs(self) -> CommandResult:
        """清空日志"""
        try:
            # 清空日志文件
            log_path = Path(self.log_file)
            if log_path.exists():
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write("")
                
                return self.format_success("日志已清空")
            else:
                return self.format_info("日志文件不存在")
                
        except Exception as e:
            return self.format_error(f"清空日志失败: {str(e)}")
    
    async def _save_logs(self, args: List[str]) -> CommandResult:
        """保存日志到文件"""
        try:
            if not args:
                filename = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            else:
                filename = args[0]
            
            log_content = self._read_log_file(1000)  # 导出更多行
            
            if not log_content:
                return self.format_error("暂无日志内容可导出")
            
            # 保存到文件
            export_path = Path(filename)
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            return self.format_success(f"日志已导出到: {export_path.absolute()}")
            
        except Exception as e:
            return self.format_error(f"导出日志失败: {str(e)}")
    
    async def _set_log_level(self, args: List[str]) -> CommandResult:
        """设置日志级别"""
        try:
            if not args:
                # 显示当前日志级别
                current_level = logging.getLogger().getEffectiveLevel()
                level_name = logging.getLevelName(current_level)
                return self.format_info(f"当前日志级别: {level_name}")
            
            level = args[0].upper()
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL
            }
            
            if level not in level_map:
                return self.format_error(f"无效的日志级别: {level}")
            
            # 设置日志级别
            logging.getLogger().setLevel(level_map[level])
            
            return self.format_success(f"日志级别已设置为: {level}")
            
        except Exception as e:
            return self.format_error(f"设置日志级别失败: {str(e)}")
    
    async def _filter_logs(self, args: List[str]) -> CommandResult:
        """过滤日志内容"""
        try:
            if not args:
                return self.format_error("请提供过滤关键词")
            
            keyword = " ".join(args)
            log_content = self._read_log_file(self.max_lines)
            
            if not log_content:
                return self.format_info("暂无日志内容")
            
            # 过滤包含关键词的行
            filtered_lines = []
            for line in log_content.split('\n'):
                if keyword.lower() in line.lower():
                    filtered_lines.append(line)
            
            if not filtered_lines:
                return self.format_info(f"未找到包含 '{keyword}' 的日志")
            
            filtered_content = '\n'.join(filtered_lines)
            
            panel = Panel(
                filtered_content,
                title=f"📋 包含 '{keyword}' 的日志",
                border_style="yellow"
            )
            self.console.print(panel)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"过滤日志失败: {str(e)}")
    
    async def _search_logs(self, args: List[str]) -> CommandResult:
        """搜索日志内容"""
        # 搜索功能与过滤类似，但可以添加更多搜索选项
        return await self._filter_logs(args)
    
    async def _show_config(self) -> CommandResult:
        """显示日志配置"""
        try:
            # 创建配置信息表格
            table = Table(title="📋 日志配置信息", show_header=True, header_style="bold magenta")
            table.add_column("配置项", style="cyan", no_wrap=True)
            table.add_column("值", style="white")
            
            # 添加配置信息
            current_level = logging.getLogger().getEffectiveLevel()
            level_name = logging.getLevelName(current_level)
            
            table.add_row("日志级别", level_name)
            table.add_row("日志文件", self.log_file)
            table.add_row("默认显示行数", str(self.max_lines))
            
            # 检查日志文件状态
            log_path = Path(self.log_file)
            if log_path.exists():
                file_size = log_path.stat().st_size
                table.add_row("文件大小", f"{file_size} 字节")
                table.add_row("文件状态", "存在")
            else:
                table.add_row("文件状态", "不存在")
            
            self.console.print(table)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"获取日志配置失败: {str(e)}")
    
    async def _rotate_logs(self) -> CommandResult:
        """日志轮转"""
        try:
            log_path = Path(self.log_file)
            if not log_path.exists():
                return self.format_info("日志文件不存在")
            
            # 创建备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{log_path.stem}_{timestamp}{log_path.suffix}"
            backup_path = log_path.parent / backup_name
            
            # 重命名当前日志文件
            log_path.rename(backup_path)
            
            # 创建新的空日志文件
            log_path.touch()
            
            return self.format_success(f"日志已轮转，备份文件: {backup_name}")
            
        except Exception as e:
            return self.format_error(f"日志轮转失败: {str(e)}")
    
    async def _show_log_size(self) -> CommandResult:
        """显示日志文件大小"""
        try:
            log_path = Path(self.log_file)
            if not log_path.exists():
                return self.format_info("日志文件不存在")
            
            file_size = log_path.stat().st_size
            
            # 格式化文件大小
            if file_size < 1024:
                size_str = f"{file_size} 字节"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            return self.format_info(f"日志文件大小: {size_str}")
            
        except Exception as e:
            return self.format_error(f"获取日志文件大小失败: {str(e)}")
    
    def _read_log_file(self, max_lines: int = None) -> str:
        """读取日志文件内容"""
        try:
            log_path = Path(self.log_file)
            if not log_path.exists():
                # 尝试从Python日志系统获取
                return self._get_python_logs(max_lines or self.max_lines)
            
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if max_lines and len(lines) > max_lines:
                lines = lines[-max_lines:]
            
            return ''.join(lines).strip()
            
        except Exception as e:
            self.logger.error(f"读取日志文件失败: {e}")
            return ""
    
    def _get_python_logs(self, max_lines: int) -> str:
        """从Python日志系统获取日志（备用方案）"""
        try:
            # 这里可以实现从内存中的日志处理器获取日志
            # 目前返回示例日志
            sample_logs = [
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: 游戏系统启动",
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: 命令系统初始化完成",
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DEBUG: 用户执行日志命令"
            ]
            
            return '\n'.join(sample_logs[-max_lines:])
            
        except Exception:
            return "暂无日志内容"
    
    async def _show_help(self) -> CommandResult:
        """显示日志命令帮助"""
        try:
            help_table = Table(title="📋 日志系统命令帮助", show_header=True, header_style="bold green")
            help_table.add_column("命令", style="cyan", no_wrap=True)
            help_table.add_column("描述", style="white")
            help_table.add_column("示例", style="yellow")
            
            # 日志查看命令
            help_table.add_row("log show [行数]", "显示最新日志", "log show 50")
            help_table.add_row("log tail", "实时显示日志", "log tail")
            help_table.add_row("log error", "显示错误日志", "log error")
            help_table.add_row("log warn", "显示警告日志", "log warn")
            help_table.add_row("log info", "显示信息日志", "log info")
            help_table.add_row("log debug", "显示调试日志", "log debug")
            
            # 日志管理命令
            help_table.add_row("log clear", "清空日志", "log clear")
            help_table.add_row("log save <文件>", "导出日志", "log save backup.log")
            help_table.add_row("log level <级别>", "设置日志级别", "log level DEBUG")
            help_table.add_row("log filter <关键词>", "过滤日志", "log filter ERROR")
            help_table.add_row("log search <关键词>", "搜索日志", "log search 用户")
            
            # 日志配置命令
            help_table.add_row("log config", "显示日志配置", "log config")
            help_table.add_row("log rotate", "轮转日志文件", "log rotate")
            help_table.add_row("log size", "显示日志文件大小", "log size")
            help_table.add_row("log help", "显示此帮助信息", "log help")
            
            panel = Panel(help_table, title="📋 日志命令帮助", border_style="green")
            self.console.print(panel)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"显示帮助信息失败: {str(e)}")