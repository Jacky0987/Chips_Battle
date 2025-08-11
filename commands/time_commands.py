# -*- coding: utf-8 -*-
"""
时间控制命令

提供游戏内时间控制功能，包括：
- 时间倍率调整
- 暂停/恢复时间
- 查看时间状态
- 手动推进时间
"""

import logging
from typing import Optional, List

from core.game_time import GameTime
from services.time_service import TimeService
from commands.base import Command, CommandResult, CommandContext


class TimeCommands(Command):
    """时间控制命令类"""
    
    def __init__(self, time_service: TimeService):
        super().__init__()
        self.time_service = time_service
        self.logger = logging.getLogger(__name__)
        
    @property
    def name(self) -> str:
        return "time"
        
    @property
    def description(self) -> str:
        return "时间控制命令"
        
    @property
    def usage(self) -> str:
        return "time [status|scale|pause|resume|advance|help] [参数]"
        
    @property
    def category(self) -> str:
        return "系统"
        
    @property
    def aliases(self) -> List[str]:
        return ["jctime", "t", "时间", "tm", "clock"]
        
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行时间命令"""
        if not args:
            return CommandResult(success=True, message=self.time_status())
            
        action = args[0].lower()
        
        if action == "status":
            return CommandResult(success=True, message=self.time_status())
        elif action == "scale" and len(args) > 1:
            try:
                scale = float(args[1])
                return CommandResult(success=True, message=self.set_time_scale(scale))
            except ValueError:
                return CommandResult(success=False, message="无效的时间倍率")
        elif action == "pause":
            return CommandResult(success=True, message=self.pause_time())
        elif action == "resume":
            return CommandResult(success=True, message=self.resume_time())
        elif action == "advance" and len(args) > 1:
            try:
                hours = int(args[1])
                return CommandResult(success=True, message=self.advance_time(hours))
            except ValueError:
                return CommandResult(success=False, message="无效的小时数")
        elif action == "help":
            return CommandResult(success=True, message=self.time_help())
        else:
            return CommandResult(success=False, message="未知的时间操作，输入 'time help' 查看帮助")
    
    def time_status(self) -> str:
        """显示时间状态
        
        Returns:
            时间状态信息
        """
        try:
            current_time = self.time_service.format_game_time(include_seconds=True)
            time_scale = self.time_service.get_time_scale()
            is_paused = self.time_service.is_paused()
            is_market = self.time_service.is_market_hours()
            is_business = self.time_service.is_business_hours()
            
            status_lines = [
                "=== 时间状态 ===",
                f"当前游戏时间: {current_time}",
                f"时间倍率: {time_scale}x",
                f"状态: {'暂停' if is_paused else '运行中'}",
                f"市场时间: {'是' if is_market else '否'} (9:00-15:00)",
                f"营业时间: {'是' if is_business else '否'} (8:00-18:00)"
            ]
            
            return "\n".join(status_lines)
            
        except Exception as e:
            self.logger.error(f"获取时间状态失败: {e}")
            return f"获取时间状态失败: {e}"
    
    def set_time_scale(self, scale: float) -> str:
        """设置时间倍率
        
        Args:
            scale: 时间倍率
            
        Returns:
            操作结果
        """
        try:
            if scale <= 0:
                return "时间倍率必须大于0"
            
            if scale > 100:
                return "时间倍率不能超过100x"
            
            old_scale = self.time_service.get_time_scale()
            self.time_service.set_time_speed(scale)
            
            return f"时间倍率已调整: {old_scale}x -> {scale}x"
            
        except Exception as e:
            self.logger.error(f"设置时间倍率失败: {e}")
            return f"设置时间倍率失败: {e}"
    
    def pause_time(self) -> str:
        """暂停时间
        
        Returns:
            操作结果
        """
        try:
            if self.time_service.is_paused():
                return "时间已经暂停"
            
            self.time_service.pause()
            return "时间已暂停"
            
        except Exception as e:
            self.logger.error(f"暂停时间失败: {e}")
            return f"暂停时间失败: {e}"
    
    def resume_time(self) -> str:
        """恢复时间
        
        Returns:
            操作结果
        """
        try:
            if not self.time_service.is_paused():
                return "时间未暂停"
            
            self.time_service.resume()
            return "时间已恢复"
            
        except Exception as e:
            self.logger.error(f"恢复时间失败: {e}")
            return f"恢复时间失败: {e}"
    
    def advance_time(self, hours: int) -> str:
        """手动推进时间
        
        Args:
            hours: 要推进的小时数
            
        Returns:
            操作结果
        """
        try:
            if hours <= 0:
                return "推进时间必须大于0小时"
            
            if hours > 24:
                return "一次最多只能推进24小时"
            
            old_time = self.time_service.format_game_time()
            
            # 使用TimeService的advance_time方法
            self.time_service.advance_time(hours)
            
            new_time_str = self.time_service.format_game_time()
            
            return f"时间已推进 {hours} 小时\n从: {old_time}\n到: {new_time_str}"
            
        except Exception as e:
            self.logger.error(f"推进时间失败: {e}")
            return f"推进时间失败: {e}"
    
    def time_help(self) -> str:
        """显示时间命令帮助
        
        Returns:
            帮助信息
        """
        help_lines = [
            "=== 时间控制命令 ===",
            "jctime status - 查看时间状态",
            "jctime scale <倍率> - 设置时间倍率 (0.1-100)",
            "jctime pause - 暂停时间",
            "jctime resume - 恢复时间",
            "jctime advance <小时> - 手动推进时间 (1-24小时)",
            "jctime help - 显示此帮助",
            "",
            "示例:",
            "  jctime scale 2.0  # 设置2倍速",
            "  jctime advance 3  # 推进3小时"
        ]
        
        return "\n".join(help_lines)


# 注册函数已移除，新的命令系统会自动发现和注册TimeCommands类