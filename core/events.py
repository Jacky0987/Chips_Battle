# -*- coding: utf-8 -*-
"""
事件定义模块

定义系统中使用的所有事件类。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List
import uuid
from .game_time import GameTime


def get_current_time():
    """获取当前时间（游戏时间或真实时间）"""
    # 在事件系统中使用系统时间，避免GUI事件循环问题
    return datetime.now()


@dataclass
class Event:
    """事件基类"""
    timestamp: datetime = field(default_factory=get_current_time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "unknown"
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeTickEvent(Event):
    """时间流逝事件"""
    game_time: datetime = field(default_factory=get_current_time)
    tick_number: int = 0
    hours_elapsed: int = 0


@dataclass
class TimeHourEvent(Event):
    """小时变化事件"""
    game_time: datetime = field(default_factory=get_current_time)
    hour: int = 0
    day: int = 0


@dataclass
class TimeDayEvent(Event):
    """日期变化事件"""
    game_time: datetime = field(default_factory=get_current_time)
    day: int = 0
    week: int = 0


@dataclass
class NewsPublishedEvent(Event):
    """新闻发布事件"""
    news_id: str = ""
    headline: str = ""
    impact_tags: List[str] = field(default_factory=list)
    severity: float = 0.0  # 0.0 - 1.0


@dataclass
class UserActionEvent(Event):
    """用户行为事件"""
    user_id: str = ""
    action: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandExecutedEvent(Event):
    """命令执行事件"""
    user_id: str = ""
    command: str = ""
    result: str = ""
    success: bool = True


@dataclass
class MarketUpdateEvent(Event):
    """市场更新事件"""
    market_type: str = ""  # "stock", "currency", etc.
    symbol: str = ""
    old_price: float = 0.0
    new_price: float = 0.0
    change_percent: float = 0.0