# -*- coding: utf-8 -*-
"""
游戏时间管理器

核心时间系统，负责管理游戏虚拟时间的流动、倍率控制和时间操作。
"""

import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class TimeType(Enum):
    """时间类型"""
    GAME_TIME = "game_time"      # 游戏时间
    REAL_TIME = "real_time"      # 实际时间
    SYSTEM_TIME = "system_time"  # 系统时间（用于日志、统计等）


@dataclass
class TimeContext:
    """时间上下文"""
    game_time: datetime          # 当前游戏时间
    real_time: datetime          # 当前实际时间
    time_scale: float           # 时间倍率
    is_paused: bool            # 是否暂停
    total_game_hours: float    # 总游戏时长（小时）
    session_duration: float    # 会话时长（实际秒数）


class GameTimeManager:
    """游戏时间管理器 - 系统核心"""
    
    def __init__(self, start_time: Optional[datetime] = None):
        """
        初始化游戏时间管理器
        
        Args:
            start_time: 游戏开始时间，默认为2024-01-01 09:00:00
        """
        self._logger = logging.getLogger(__name__)
        
        # 时间状态
        if start_time is None:
            start_time = datetime(2024, 1, 1, 9, 0, 0)
        
        self._game_time: datetime = start_time
        self._start_time: datetime = start_time
        self._time_scale: float = 1.0  # 时间流速倍率
        self._is_paused: bool = False  # 是否暂停
        
        # 实际时间跟踪
        self._last_real_time: float = time.time()  # 上次更新的实际时间
        self._accumulated_time: float = 0.0  # 累积的游戏时间（秒）
        self._session_start_time: float = time.time()  # 会话开始时间
        
        # 统计信息
        self._total_ticks: int = 0
        self._last_hour: int = self._game_time.hour
        self._last_day: int = self._game_time.day
        
        self._logger.info(f"游戏时间管理器已初始化，开始时间: {self._game_time}")
    
    def get_current_time(self) -> datetime:
        """获取当前游戏时间"""
        return self._game_time
    
    def get_start_time(self) -> datetime:
        """获取游戏开始时间"""
        return self._start_time
    
    def get_time_scale(self) -> float:
        """获取当前时间倍率"""
        return self._time_scale
    
    def is_paused(self) -> bool:
        """检查时间是否暂停"""
        return self._is_paused
    
    def get_total_game_hours(self) -> float:
        """获取总游戏时长（小时）"""
        time_diff = self._game_time - self._start_time
        return time_diff.total_seconds() / 3600
    
    def get_session_duration(self) -> float:
        """获取会话时长（实际秒数）"""
        return time.time() - self._session_start_time
    
    def get_time_context(self) -> TimeContext:
        """获取完整的时间上下文"""
        return TimeContext(
            game_time=self._game_time,
            real_time=datetime.now(),
            time_scale=self._time_scale,
            is_paused=self._is_paused,
            total_game_hours=self.get_total_game_hours(),
            session_duration=self.get_session_duration()
        )
    
    def set_time_scale(self, scale: float):
        """设置时间流速（1.0=正常，2.0=2倍速，0.5=半速）"""
        if scale < 0:
            raise ValueError("时间倍率不能为负数")
        
        old_scale = self._time_scale
        self._time_scale = scale
        
        self._logger.info(f"时间流速已更改: {old_scale}x -> {scale}x")
    
    def pause(self):
        """暂停时间"""
        if self._is_paused:
            self._logger.warning("时间已经处于暂停状态")
            return
        
        self._is_paused = True
        self._logger.info("游戏时间已暂停")
    
    def resume(self):
        """恢复时间"""
        if not self._is_paused:
            self._logger.warning("时间未处于暂停状态")
            return
        
        self._is_paused = False
        # 重置实际时间基准，避免暂停期间的时间跳跃
        self._last_real_time = time.time()
        self._logger.info("游戏时间已恢复")
    
    def advance_time(self, hours: float):
        """手动推进时间"""
        if hours < 0:
            raise ValueError("推进时间不能为负数")
        
        old_time = self._game_time
        self._game_time += timedelta(hours=hours)
        self._accumulated_time += hours * 3600  # 转换为秒
        
        # 检查是否跨越了重要时间节点
        if old_time.day != self._game_time.day:
            self._logger.info(f"手动推进时间跨越日期: {old_time.strftime('%Y-%m-%d')} -> {self._game_time.strftime('%Y-%m-%d')}")
        
        self._logger.info(f"手动推进时间: {old_time.strftime('%Y-%m-%d %H:%M')} -> {self._game_time.strftime('%Y-%m-%d %H:%M')} (+{hours}小时)")
    
    def set_time(self, new_time: datetime):
        """设置游戏时间"""
        old_time = self._game_time
        self._game_time = new_time
        
        # 重新计算累积时间
        time_diff = new_time - self._start_time
        self._accumulated_time = time_diff.total_seconds()
        
        self._logger.info(f"游戏时间已设置: {old_time} -> {new_time}")
    
    def update(self) -> Dict[str, Any]:
        """更新时间状态，返回变化信息"""
        if self._is_paused:
            return {'updated': False, 'reason': 'paused'}
        
        current_real_time = time.time()
        real_delta = current_real_time - self._last_real_time
        
        if real_delta <= 0:
            return {'updated': False, 'reason': 'no_time_passed'}
        
        # 应用时间倍率
        game_delta_seconds = real_delta * self._time_scale
        
        # 更新游戏时间
        old_time = self._game_time
        self._game_time += timedelta(seconds=game_delta_seconds)
        self._accumulated_time += game_delta_seconds
        self._last_real_time = current_real_time
        self._total_ticks += 1
        
        # 检查时间变化
        changes = {
            'updated': True,
            'old_time': old_time,
            'new_time': self._game_time,
            'delta_seconds': game_delta_seconds,
            'delta_hours': game_delta_seconds / 3600,
            'hour_changed': self._game_time.hour != self._last_hour,
            'day_changed': self._game_time.day != self._last_day,
            'total_ticks': self._total_ticks
        }
        
        # 记录重要时间变化
        if changes['hour_changed']:
            self._logger.debug(f"游戏时间进入新小时: {self._game_time.strftime('%Y-%m-%d %H:00')}")
        
        if changes['day_changed']:
            self._logger.info(f"游戏时间进入新一天: {self._game_time.strftime('%Y-%m-%d')}")
        
        # 更新变化跟踪
        self._last_hour = self._game_time.hour
        self._last_day = self._game_time.day
        
        return changes
    
    def format_time(self, include_seconds: bool = False) -> str:
        """格式化游戏时间为字符串"""
        if include_seconds:
            time_str = self._game_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = self._game_time.strftime("%Y-%m-%d %H:%M")
        
        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        day_name = day_names[self._game_time.weekday()]
        
        return f"{time_str} ({day_name})"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取时间管理器统计信息"""
        return {
            'current_game_time': self._game_time.isoformat(),
            'start_time': self._start_time.isoformat(),
            'time_scale': self._time_scale,
            'is_paused': self._is_paused,
            'total_game_hours': self.get_total_game_hours(),
            'session_duration_seconds': self.get_session_duration(),
            'total_ticks': self._total_ticks,
            'accumulated_time_seconds': self._accumulated_time
        }
    
    def is_market_hours(self) -> bool:
        """判断是否为市场交易时间 (9:00-16:00, 周一到周五)"""
        if self._game_time.weekday() >= 5:  # 周末
            return False
        return 9 <= self._game_time.hour < 16
    
    def is_business_hours(self) -> bool:
        """判断是否为营业时间 (8:00-18:00, 周一到周五)"""
        if self._game_time.weekday() >= 5:  # 周末
            return False
        return 8 <= self._game_time.hour < 18