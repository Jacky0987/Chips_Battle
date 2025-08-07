# -*- coding: utf-8 -*-
"""
事件定义模块

定义系统中使用的所有事件类。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List
import uuid


@dataclass
class Event:
    """事件基类"""
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "unknown"
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeTickEvent(Event):
    """时间流逝事件"""
    game_time: datetime = field(default_factory=datetime.now)
    tick_number: int = 0
    hours_elapsed: int = 0


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
class MarketUpdateEvent(Event):
    """市场更新事件"""
    market_type: str = ""  # "stock", "currency", etc.
    symbol: str = ""
    old_price: float = 0.0
    new_price: float = 0.0
    change_percent: float = 0.0