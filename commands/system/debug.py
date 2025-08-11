# -*- coding: utf-8 -*-
"""
调试命令

提供游戏调试功能，包括内存监控、变量查看、调用栈追踪等。
"""

import gc
import sys
import psutil
import traceback
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from commands.base import Command, CommandResult, CommandContext
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax


class DebugCommand(Command):
    """调试系统主命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.debug_enabled = False
    
    @property
    def name(self) -> str:
        return "debug"
    
    @property
    def aliases(self) -> List[str]:
        return ["dbg"]
    
    @property
    def description(self) -> str:
        return "调试系统管理命令"
    
    @property
    def category(self) -> str:
        return "系统"
    
    @property
    def usage(self) -> str:
        return f"{self.name} [on|off|status|memory|vars|trace|dump|gc] [参数]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行调试命令"""
        try:
            if not args:
                # 默认显示调试状态
                return await self._show_debug_status()
            
            subcommand = args[0].lower()
            sub_args = args[1:] if len(args) > 1 else []
            
            if subcommand in ["help", "h", "?"]:
                return await self._show_help()
            elif subcommand in ["on", "enable", "start"]:
                return await self._enable_debug()
            elif subcommand in ["off", "disable", "stop"]:
                return await self._disable_debug()
            elif subcommand in ["status", "info"]:
                return await self._show_debug_status()
            elif subcommand in ["memory", "mem"]:
                return await self._show_memory_info()
            elif subcommand in ["vars", "variables"]:
                return await self._show_variables(context)
            elif subcommand in ["trace", "stack"]:
                return await self._show_call_stack()
            elif subcommand in ["dump", "export"]:
                return await self._dump_debug_info(context, sub_args)
            elif subcommand in ["gc", "garbage"]:
                return await self._show_gc_info()
            else:
                return self.format_error(f"未知的调试子命令: {subcommand}")
                
        except Exception as e:
            return self.format_error(f"调试命令执行失败: {str(e)}")
    
    async def _enable_debug(self) -> CommandResult:
        """开启调试模式"""
        try:
            self.debug_enabled = True
            return self.format_success("调试模式已开启")
        except Exception as e:
            return self.format_error(f"开启调试模式失败: {str(e)}")
    
    async def _disable_debug(self) -> CommandResult:
        """关闭调试模式"""
        try:
            self.debug_enabled = False
            return self.format_success("调试模式已关闭")
        except Exception as e:
            return self.format_error(f"关闭调试模式失败: {str(e)}")
    
    async def _show_debug_status(self) -> CommandResult:
        """显示调试状态"""
        try:
            # 创建调试状态表格
            table = Table(title="🐛 调试状态信息", show_header=True, header_style="bold magenta")
            table.add_column("项目", style="cyan", no_wrap=True)
            table.add_column("状态", style="white")
            
            # 调试模式状态
            debug_status = "开启" if self.debug_enabled else "关闭"
            debug_color = "green" if self.debug_enabled else "red"
            table.add_row("调试模式", Text(debug_status, style=debug_color))
            
            # Python调试信息
            table.add_row("Python版本", sys.version.split()[0])
            table.add_row("调试标志", str(sys.flags.debug))
            table.add_row("优化标志", str(sys.flags.optimize))
            
            # 系统信息
            process = psutil.Process()
            table.add_row("进程ID", str(process.pid))
            table.add_row("线程数", str(process.num_threads()))
            
            self.console.print(table)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"获取调试状态失败: {str(e)}")
    
    async def _show_memory_info(self) -> CommandResult:
        """显示内存使用情况"""
        try:
            # 获取进程内存信息
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # 获取系统内存信息
            system_memory = psutil.virtual_memory()
            
            # 创建内存信息表格
            table = Table(title="💾 内存使用情况", show_header=True, header_style="bold blue")
            table.add_column("类型", style="cyan", no_wrap=True)
            table.add_column("使用量", style="white")
            table.add_column("百分比", style="yellow")
            
            # 进程内存
            rss_mb = memory_info.rss / 1024 / 1024
            vms_mb = memory_info.vms / 1024 / 1024
            
            table.add_row(
                "进程物理内存", 
                f"{rss_mb:.1f} MB",
                f"{memory_percent:.1f}%"
            )
            table.add_row(
                "进程虚拟内存", 
                f"{vms_mb:.1f} MB",
                "-"
            )
            
            # 系统内存
            system_total_gb = system_memory.total / 1024 / 1024 / 1024
            system_used_gb = system_memory.used / 1024 / 1024 / 1024
            system_available_gb = system_memory.available / 1024 / 1024 / 1024
            
            table.add_row(
                "系统总内存",
                f"{system_total_gb:.1f} GB",
                "100%"
            )
            table.add_row(
                "系统已用内存",
                f"{system_used_gb:.1f} GB",
                f"{system_memory.percent:.1f}%"
            )
            table.add_row(
                "系统可用内存",
                f"{system_available_gb:.1f} GB",
                f"{(system_memory.available / system_memory.total * 100):.1f}%"
            )
            
            # 垃圾回收信息
            gc_stats = gc.get_stats()
            if gc_stats:
                table.add_row(
                    "GC对象数量",
                    str(sum(stat['collections'] for stat in gc_stats)),
                    "-"
                )
            
            self.console.print(table)
            
            return CommandResult(
                success=True,
                message="",
                data={
                    "rss_mb": rss_mb,
                    "vms_mb": vms_mb,
                    "memory_percent": memory_percent
                }
            )
            
        except Exception as e:
            return self.format_error(f"获取内存信息失败: {str(e)}")
    
    async def _show_variables(self, context: CommandContext) -> CommandResult:
        """显示关键游戏变量"""
        try:
            # 创建变量信息表格
            table = Table(title="📊 关键游戏变量", show_header=True, header_style="bold green")
            table.add_column("变量名", style="cyan", no_wrap=True)
            table.add_column("值", style="white")
            table.add_column("类型", style="yellow")
            
            # 用户信息
            if context.user:
                table.add_row("当前用户", str(context.user.username), "User")
                if hasattr(context.user, 'id'):
                    table.add_row("用户ID", str(context.user.id), "int")
            else:
                table.add_row("当前用户", "未登录", "None")
            
            # 游戏时间
            if context.game_time:
                table.add_row(
                    "游戏时间", 
                    context.game_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "datetime"
                )
            else:
                table.add_row("游戏时间", "未设置", "None")
            
            # 系统时间
            table.add_row(
                "系统时间",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "datetime"
            )
            
            # 命令注册信息
            if hasattr(context, 'registry') and context.registry:
                command_count = len(context.registry._commands)
                table.add_row("已注册命令数", str(command_count), "int")
                
                alias_count = len(context.registry._aliases)
                table.add_row("命令别名数", str(alias_count), "int")
            
            # 会话数据
            if context.session_data:
                session_keys = list(context.session_data.keys())
                table.add_row(
                    "会话数据键", 
                    ", ".join(session_keys) if session_keys else "无",
                    "list"
                )
            
            # Python环境变量
            table.add_row("Python路径", sys.executable, "str")
            table.add_row("模块搜索路径数", str(len(sys.path)), "int")
            
            self.console.print(table)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"获取变量信息失败: {str(e)}")
    
    async def _show_call_stack(self) -> CommandResult:
        """显示当前调用栈"""
        try:
            # 获取当前调用栈
            stack = traceback.extract_stack()
            
            # 创建调用栈树
            tree = Tree("📞 当前调用栈")
            
            # 显示最近10个调用
            recent_stack = stack[-10:] if len(stack) > 10 else stack
            
            for i, frame in enumerate(recent_stack):
                frame_info = f"{frame.filename}:{frame.lineno} in {frame.name}()"
                if frame.line:
                    frame_info += f"\n    {frame.line.strip()}"
                
                tree.add(Text(frame_info, style="cyan" if i == len(recent_stack)-1 else "white"))
            
            self.console.print(tree)
            
            return CommandResult(
                success=True,
                message="",
                data={"stack_depth": len(stack)}
            )
            
        except Exception as e:
            return self.format_error(f"获取调用栈失败: {str(e)}")
    
    async def _dump_debug_info(self, context: CommandContext, args: List[str]) -> CommandResult:
        """导出完整调试信息"""
        try:
            # 生成调试报告
            debug_info = {
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "executable": sys.executable
                },
                "memory_info": {},
                "process_info": {},
                "game_state": {},
                "error_summary": []
            }
            
            # 内存信息
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                debug_info["memory_info"] = {
                    "rss_mb": memory_info.rss / 1024 / 1024,
                    "vms_mb": memory_info.vms / 1024 / 1024,
                    "memory_percent": process.memory_percent()
                }
            except Exception as e:
                debug_info["error_summary"].append(f"获取内存信息失败: {e}")
            
            # 进程信息
            try:
                process = psutil.Process()
                debug_info["process_info"] = {
                    "pid": process.pid,
                    "num_threads": process.num_threads(),
                    "cpu_percent": process.cpu_percent()
                }
            except Exception as e:
                debug_info["error_summary"].append(f"获取进程信息失败: {e}")
            
            # 游戏状态
            try:
                debug_info["game_state"] = {
                    "user": str(context.user) if context.user else None,
                    "game_time": context.game_time.isoformat() if context.game_time else None,
                    "session_data_keys": list(context.session_data.keys()) if context.session_data else [],
                    "debug_enabled": self.debug_enabled
                }
            except Exception as e:
                debug_info["error_summary"].append(f"获取游戏状态失败: {e}")
            
            # 生成文件名
            if args:
                filename = args[0]
            else:
                filename = f"debug_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 保存调试信息
            dump_path = Path(filename)
            with open(dump_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2, ensure_ascii=False)
            
            return self.format_success(f"调试信息已导出到: {dump_path.absolute()}")
            
        except Exception as e:
            return self.format_error(f"导出调试信息失败: {str(e)}")
    
    async def _show_gc_info(self) -> CommandResult:
        """显示垃圾回收统计"""
        try:
            # 获取垃圾回收统计
            gc_stats = gc.get_stats()
            gc_counts = gc.get_count()
            
            # 创建GC信息表格
            table = Table(title="🗑️ 垃圾回收统计", show_header=True, header_style="bold yellow")
            table.add_column("项目", style="cyan", no_wrap=True)
            table.add_column("值", style="white")
            
            # 基础GC信息
            table.add_row("GC是否启用", "是" if gc.isenabled() else "否")
            table.add_row("GC阈值", str(gc.get_threshold()))
            table.add_row("当前计数", str(gc_counts))
            
            # 各代统计
            if gc_stats:
                for i, stat in enumerate(gc_stats):
                    table.add_row(f"第{i}代回收次数", str(stat['collections']))
                    table.add_row(f"第{i}代回收对象", str(stat['collected']))
                    table.add_row(f"第{i}代未回收对象", str(stat['uncollectable']))
            
            # 手动触发GC并显示结果
            collected = gc.collect()
            table.add_row("本次回收对象数", str(collected))
            
            self.console.print(table)
            
            return CommandResult(
                success=True,
                message="",
                data={
                    "collected": collected,
                    "gc_enabled": gc.isenabled(),
                    "gc_counts": gc_counts
                }
            )
            
        except Exception as e:
            return self.format_error(f"获取垃圾回收信息失败: {str(e)}")
    
    async def _show_help(self) -> CommandResult:
        """显示调试命令帮助"""
        try:
            help_table = Table(title="🔧 调试系统命令帮助", show_header=True, header_style="bold green")
            help_table.add_column("命令", style="cyan", no_wrap=True)
            help_table.add_column("描述", style="white")
            help_table.add_column("示例", style="yellow")
            
            # 系统状态命令
            help_table.add_row("debug help", "显示此帮助信息", "debug help")
            help_table.add_row("debug on/off", "开启/关闭调试模式", "debug on")
            help_table.add_row("debug status", "显示调试状态信息", "debug status")
            help_table.add_row("debug memory", "显示内存使用情况", "debug memory")
            help_table.add_row("debug vars", "显示关键游戏变量", "debug vars")
            help_table.add_row("debug trace", "显示当前调用栈", "debug trace")
            help_table.add_row("debug dump [文件]", "导出完整调试信息", "debug dump debug.json")
            help_table.add_row("debug gc", "显示垃圾回收统计", "debug gc")
            
            # 添加别名说明
            help_table.add_section()
            help_table.add_row("[bold yellow]别名说明[/bold yellow]", "", "")
            help_table.add_row("help", "h, ?", "")
            help_table.add_row("on", "enable, start", "")
            help_table.add_row("off", "disable, stop", "")
            help_table.add_row("status", "info", "")
            help_table.add_row("memory", "mem", "")
            help_table.add_row("vars", "variables", "")
            help_table.add_row("trace", "stack", "")
            help_table.add_row("dump", "export", "")
            help_table.add_row("gc", "garbage", "")
            
            panel = Panel(help_table, title="🔧 调试命令帮助", border_style="green")
            self.console.print(panel)
            
            return CommandResult(success=True, message="")
            
        except Exception as e:
            return self.format_error(f"显示帮助信息失败: {str(e)}")