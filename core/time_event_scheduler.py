# -*- coding: utf-8 -*-
"""
时间事件调度器

基于游戏时间的事件调度系统，支持定时、延时和周期性事件调度。
"""

import asyncio
import logging
import heapq
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict, Any, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import uuid


class EventType(Enum):
    """事件类型"""
    ONE_TIME = "one_time"        # 一次性事件
    RECURRING = "recurring"      # 周期性事件
    DELAYED = "delayed"          # 延时事件


@dataclass
class ScheduledEvent:
    """调度事件"""
    event_id: str
    target_time: datetime
    callback: Callable[[], Awaitable[None]]
    event_type: EventType
    interval_hours: Optional[float] = None  # 周期性事件的间隔（小时）
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        """用于优先队列排序"""
        return self.target_time < other.target_time


class TimeEventScheduler:
    """基于游戏时间的事件调度器"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._events: List[ScheduledEvent] = []  # 优先队列
        self._event_registry: Dict[str, ScheduledEvent] = {}  # 事件注册表
        self._stats = {
            'total_scheduled': 0,
            'total_executed': 0,
            'total_cancelled': 0,
            'active_events': 0
        }
        
        self._logger.info("时间事件调度器已初始化")
    
    def schedule_at(self, target_time: datetime, callback: Callable[[], Awaitable[None]], 
                   description: str = "") -> str:
        """在指定游戏时间执行回调
        
        Args:
            target_time: 目标执行时间
            callback: 回调函数
            description: 事件描述
            
        Returns:
            事件ID
        """
        event_id = str(uuid.uuid4())
        event = ScheduledEvent(
            event_id=event_id,
            target_time=target_time,
            callback=callback,
            event_type=EventType.ONE_TIME,
            description=description
        )
        
        heapq.heappush(self._events, event)
        self._event_registry[event_id] = event
        
        self._stats['total_scheduled'] += 1
        self._stats['active_events'] += 1
        
        self._logger.debug(f"已调度一次性事件: {description} at {target_time}")
        return event_id
    
    def schedule_after(self, hours: float, callback: Callable[[], Awaitable[None]], 
                      current_time: datetime, description: str = "") -> str:
        """在指定游戏时间后执行回调
        
        Args:
            hours: 延迟小时数
            callback: 回调函数
            current_time: 当前游戏时间
            description: 事件描述
            
        Returns:
            事件ID
        """
        target_time = current_time + timedelta(hours=hours)
        return self.schedule_at(target_time, callback, description)
    
    def schedule_recurring(self, interval_hours: float, callback: Callable[[], Awaitable[None]], 
                          current_time: datetime, description: str = "") -> str:
        """定期执行回调
        
        Args:
            interval_hours: 执行间隔（小时）
            callback: 回调函数
            current_time: 当前游戏时间
            description: 事件描述
            
        Returns:
            事件ID
        """
        event_id = str(uuid.uuid4())
        target_time = current_time + timedelta(hours=interval_hours)
        
        event = ScheduledEvent(
            event_id=event_id,
            target_time=target_time,
            callback=callback,
            event_type=EventType.RECURRING,
            interval_hours=interval_hours,
            description=description
        )
        
        heapq.heappush(self._events, event)
        self._event_registry[event_id] = event
        
        self._stats['total_scheduled'] += 1
        self._stats['active_events'] += 1
        
        self._logger.debug(f"已调度周期性事件: {description}, 间隔: {interval_hours}小时")
        return event_id
    
    def cancel_event(self, event_id: str) -> bool:
        """取消事件
        
        Args:
            event_id: 事件ID
            
        Returns:
            是否成功取消
        """
        if event_id not in self._event_registry:
            self._logger.warning(f"尝试取消不存在的事件: {event_id}")
            return False
        
        event = self._event_registry[event_id]
        
        # 从注册表中移除
        del self._event_registry[event_id]
        
        # 标记事件为已取消（不能直接从堆中移除，会在执行时跳过）
        event.event_id = f"CANCELLED_{event.event_id}"
        
        self._stats['total_cancelled'] += 1
        self._stats['active_events'] -= 1
        
        self._logger.debug(f"已取消事件: {event.description}")
        return True
    
    async def check_and_fire_events(self, current_time: datetime) -> List[str]:
        """检查并触发到期的事件
        
        Args:
            current_time: 当前游戏时间
            
        Returns:
            已执行的事件ID列表
        """
        executed_events = []
        
        while self._events and self._events[0].target_time <= current_time:
            event = heapq.heappop(self._events)
            
            # 检查事件是否已被取消
            if event.event_id.startswith("CANCELLED_"):
                continue
            
            # 检查事件是否仍在注册表中
            if event.event_id not in self._event_registry:
                continue
            
            try:
                # 执行回调
                await event.callback()
                executed_events.append(event.event_id)
                self._stats['total_executed'] += 1
                
                self._logger.debug(f"已执行事件: {event.description}")
                
                # 处理周期性事件
                if event.event_type == EventType.RECURRING and event.interval_hours:
                    # 重新调度下一次执行
                    next_time = event.target_time + timedelta(hours=event.interval_hours)
                    event.target_time = next_time
                    heapq.heappush(self._events, event)
                    self._logger.debug(f"周期性事件已重新调度: {event.description} at {next_time}")
                else:
                    # 一次性事件，从注册表中移除
                    del self._event_registry[event.event_id]
                    self._stats['active_events'] -= 1
                
            except Exception as e:
                self._logger.error(f"执行事件回调失败 {event.description}: {e}", exc_info=True)
                # 即使失败也要清理一次性事件
                if event.event_type != EventType.RECURRING:
                    if event.event_id in self._event_registry:
                        del self._event_registry[event.event_id]
                        self._stats['active_events'] -= 1
        
        return executed_events
    
    def get_pending_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取待执行的事件列表
        
        Args:
            limit: 返回的事件数量限制
            
        Returns:
            事件信息列表
        """
        events = []
        
        # 获取前N个事件（不移除）
        sorted_events = sorted(self._events, key=lambda x: x.target_time)
        
        for event in sorted_events[:limit]:
            if not event.event_id.startswith("CANCELLED_"):
                events.append({
                    'event_id': event.event_id,
                    'target_time': event.target_time.isoformat(),
                    'event_type': event.event_type.value,
                    'description': event.description,
                    'interval_hours': event.interval_hours,
                    'created_at': event.created_at.isoformat()
                })
        
        return events
    
    def get_event_info(self, event_id: str) -> Optional[Dict[str, Any]]:
        """获取特定事件的信息
        
        Args:
            event_id: 事件ID
            
        Returns:
            事件信息或None
        """
        if event_id not in self._event_registry:
            return None
        
        event = self._event_registry[event_id]
        return {
            'event_id': event.event_id,
            'target_time': event.target_time.isoformat(),
            'event_type': event.event_type.value,
            'description': event.description,
            'interval_hours': event.interval_hours,
            'created_at': event.created_at.isoformat()
        }
    
    def clear_all_events(self):
        """清除所有事件"""
        cancelled_count = len(self._event_registry)
        
        self._events.clear()
        self._event_registry.clear()
        
        self._stats['total_cancelled'] += cancelled_count
        self._stats['active_events'] = 0
        
        self._logger.info(f"已清除所有事件，共 {cancelled_count} 个")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        return {
            **self._stats,
            'pending_events': len([e for e in self._events if not e.event_id.startswith("CANCELLED_")]),
            'heap_size': len(self._events)
        }
    
    def cleanup_cancelled_events(self):
        """清理已取消的事件（优化堆大小）"""
        # 重建堆，排除已取消的事件
        active_events = [e for e in self._events if not e.event_id.startswith("CANCELLED_")]
        self._events = active_events
        heapq.heapify(self._events)
        
        self._logger.debug(f"已清理取消的事件，当前堆大小: {len(self._events)}")