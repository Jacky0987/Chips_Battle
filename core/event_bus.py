# -*- coding: utf-8 -*-
"""
全局事件总线

实现发布-订阅模式，允许系统各部分进行低耦合通信。
支持同步和异步事件处理。
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Type, Union
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import weakref
import inspect

from .events import Event, TimeTickEvent, NewsPublishedEvent, UserActionEvent, MarketUpdateEvent


class EventHandler:
    """事件处理器包装类"""
    
    def __init__(self, handler: Callable, is_async: bool = False, priority: int = 0):
        self.handler = handler
        self.is_async = is_async
        self.priority = priority  # 数字越大优先级越高
        self.call_count = 0
        self.last_called = None
        
        # 使用弱引用避免内存泄漏
        if hasattr(handler, '__self__'):
            self.handler_ref = weakref.WeakMethod(handler)
        else:
            self.handler_ref = weakref.ref(handler)
    
    def is_valid(self) -> bool:
        """检查处理器是否仍然有效"""
        return self.handler_ref() is not None
    
    def get_handler(self) -> Callable:
        """获取处理器函数"""
        return self.handler_ref()
    
    async def call(self, event: Event) -> Any:
        """调用处理器"""
        handler = self.get_handler()
        if not handler:
            return None
        
        self.call_count += 1
        self.last_called = datetime.now()
        
        try:
            if self.is_async:
                return await handler(event)
            else:
                return handler(event)
        except Exception as e:
            logging.error(f"事件处理器执行失败: {e}", exc_info=True)
            raise


class EventBus:
    """全局事件总线"""
    
    def __init__(self, max_history: int = 1000):
        self._handlers: Dict[Type[Event], List[EventHandler]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._logger = logging.getLogger(__name__)
        self._stats = {
            'events_published': 0,
            'events_handled': 0,
            'handlers_registered': 0,
            'handlers_removed': 0
        }
    
    def subscribe(self, 
                  event_type: Type[Event], 
                  handler: Callable[[Event], Any],
                  priority: int = 0) -> str:
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
            priority: 优先级，数字越大优先级越高
            
        Returns:
            处理器ID，用于取消订阅
        """
        # 检查处理器是否为异步函数
        is_async = inspect.iscoroutinefunction(handler)
        
        event_handler = EventHandler(handler, is_async, priority)
        self._handlers[event_type].append(event_handler)
        
        # 按优先级排序
        self._handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
        
        self._stats['handlers_registered'] += 1
        self._logger.debug(f"注册事件处理器: {event_type.__name__} -> {handler.__name__}")
        
        return id(event_handler)
    
    def unsubscribe(self, event_type: Type[Event], handler_id: str) -> bool:
        """取消订阅事件
        
        Args:
            event_type: 事件类型
            handler_id: 处理器ID
            
        Returns:
            是否成功取消订阅
        """
        handlers = self._handlers.get(event_type, [])
        for i, handler in enumerate(handlers):
            if id(handler) == int(handler_id):
                handlers.pop(i)
                self._stats['handlers_removed'] += 1
                self._logger.debug(f"取消订阅事件处理器: {event_type.__name__}")
                return True
        return False
    
    async def publish(self, event: Event) -> List[Any]:
        """发布事件
        
        Args:
            event: 要发布的事件
            
        Returns:
            所有处理器的返回值列表
        """
        self._stats['events_published'] += 1
        
        # 添加到历史记录
        self._add_to_history(event)
        
        # 获取事件类型的所有处理器
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        # 清理无效的处理器
        valid_handlers = [h for h in handlers if h.is_valid()]
        if len(valid_handlers) != len(handlers):
            self._handlers[event_type] = valid_handlers
        
        if not valid_handlers:
            self._logger.debug(f"没有找到事件处理器: {event_type.__name__}")
            return []
        
        self._logger.debug(f"发布事件: {event_type.__name__} (处理器数量: {len(valid_handlers)})")
        
        # 执行所有处理器
        results = []
        for handler in valid_handlers:
            try:
                result = await handler.call(event)
                results.append(result)
                self._stats['events_handled'] += 1
            except Exception as e:
                self._logger.error(f"事件处理失败: {e}", exc_info=True)
                results.append(None)
        
        return results
    
    def publish_sync(self, event: Event) -> List[Any]:
        """同步发布事件（仅适用于同步处理器）
        
        Args:
            event: 要发布的事件
            
        Returns:
            所有同步处理器的返回值列表
        """
        self._stats['events_published'] += 1
        self._add_to_history(event)
        
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        # 只处理同步处理器
        sync_handlers = [h for h in handlers if h.is_valid() and not h.is_async]
        
        results = []
        for handler in sync_handlers:
            try:
                result = handler.get_handler()(event)
                results.append(result)
                self._stats['events_handled'] += 1
            except Exception as e:
                self._logger.error(f"同步事件处理失败: {e}", exc_info=True)
                results.append(None)
        
        return results
    
    def _add_to_history(self, event: Event):
        """添加事件到历史记录"""
        self._event_history.append(event)
        
        # 限制历史记录大小
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_event_history(self, 
                         event_type: Type[Event] = None, 
                         limit: int = None) -> List[Event]:
        """获取事件历史记录
        
        Args:
            event_type: 过滤特定事件类型
            limit: 限制返回数量
            
        Returns:
            事件历史记录列表
        """
        history = self._event_history
        
        if event_type:
            history = [e for e in history if isinstance(e, event_type)]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_stats(self) -> Dict[str, Any]:
        """获取事件总线统计信息"""
        return {
            **self._stats,
            'active_handlers': sum(len(handlers) for handlers in self._handlers.values()),
            'event_types': len(self._handlers),
            'history_size': len(self._event_history)
        }
    
    def clear_history(self):
        """清空事件历史记录"""
        self._event_history.clear()
        self._logger.info("事件历史记录已清空")
    
    def clear_handlers(self, event_type: Type[Event] = None):
        """清空事件处理器
        
        Args:
            event_type: 特定事件类型，如果为None则清空所有
        """
        if event_type:
            if event_type in self._handlers:
                count = len(self._handlers[event_type])
                del self._handlers[event_type]
                self._stats['handlers_removed'] += count
                self._logger.info(f"清空事件处理器: {event_type.__name__} ({count}个)")
        else:
            total_count = sum(len(handlers) for handlers in self._handlers.values())
            self._handlers.clear()
            self._stats['handlers_removed'] += total_count
            self._logger.info(f"清空所有事件处理器 ({total_count}个)")


# 全局事件总线实例
_global_event_bus = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def set_event_bus(event_bus: EventBus):
    """设置全局事件总线实例"""
    global _global_event_bus
    _global_event_bus = event_bus