# -*- coding: utf-8 -*-
"""
游戏时间服务

作为游戏世界的主时钟，以固定的"tick"推进游戏时间，
每tick代表游戏中的1小时，并广播TimeTickEvent。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, List
from dataclasses import dataclass
from core.event_bus import EventBus, TimeTickEvent


@dataclass
class GameTime:
    """游戏时间数据类"""
    current_time: datetime
    start_time: datetime
    tick_count: int
    total_hours_elapsed: int
    is_paused: bool = False
    
    def get_elapsed_days(self) -> int:
        """获取经过的游戏天数"""
        return self.total_hours_elapsed // 24
    
    def get_current_hour(self) -> int:
        """获取当前小时 (0-23)"""
        return self.current_time.hour
    
    def get_current_day_of_week(self) -> int:
        """获取当前星期几 (0=周一, 6=周日)"""
        return self.current_time.weekday()
    
    def is_market_hours(self) -> bool:
        """判断是否为市场交易时间 (9:00-16:00, 周一到周五)"""
        if self.get_current_day_of_week() >= 5:  # 周末
            return False
        return 9 <= self.get_current_hour() < 16
    
    def is_business_hours(self) -> bool:
        """判断是否为营业时间 (8:00-18:00, 周一到周五)"""
        if self.get_current_day_of_week() >= 5:  # 周末
            return False
        return 8 <= self.get_current_hour() < 18


class TimeService:
    """游戏时间服务"""
    
    def __init__(self, event_bus: EventBus, tick_interval: int = 60, hours_per_tick: int = 1):
        """
        初始化时间服务
        
        Args:
            event_bus: 事件总线
            tick_interval: tick间隔（秒），默认60秒
            hours_per_tick: 每tick代表的游戏小时数，默认1小时
        """
        self.event_bus = event_bus
        self.tick_interval = tick_interval
        self.hours_per_tick = hours_per_tick
        
        # 游戏时间状态
        self.game_time = GameTime(
            current_time=datetime(2024, 1, 1, 9, 0, 0),  # 游戏开始时间
            start_time=datetime(2024, 1, 1, 9, 0, 0),
            tick_count=0,
            total_hours_elapsed=0
        )
        
        # 服务状态
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._logger = logging.getLogger(__name__)
        
        # 事件回调
        self._tick_callbacks: List[Callable[[GameTime], None]] = []
        self._hour_callbacks: List[Callable[[GameTime], None]] = []
        self._day_callbacks: List[Callable[[GameTime], None]] = []
        
        # 统计信息
        self._stats = {
            'total_ticks': 0,
            'events_published': 0,
            'service_start_time': None,
            'last_tick_time': None
        }
    
    def start(self):
        """启动时间服务"""
        if self._running:
            self._logger.warning("时间服务已经在运行")
            return
        
        self._running = True
        self._stats['service_start_time'] = datetime.now()
        self._task = asyncio.create_task(self._time_loop())
        self._logger.info(f"时间服务已启动 (tick间隔: {self.tick_interval}秒, 每tick: {self.hours_per_tick}小时)")
    
    def stop(self):
        """停止时间服务"""
        if not self._running:
            self._logger.warning("时间服务未在运行")
            return
        
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        
        self._logger.info("时间服务已停止")
    
    def pause(self):
        """暂停游戏时间"""
        self.game_time.is_paused = True
        self._logger.info("游戏时间已暂停")
    
    def resume(self):
        """恢复游戏时间"""
        self.game_time.is_paused = False
        self._logger.info("游戏时间已恢复")
    
    def set_time_speed(self, hours_per_tick: int):
        """设置时间流逝速度
        
        Args:
            hours_per_tick: 每tick代表的游戏小时数
        """
        old_speed = self.hours_per_tick
        self.hours_per_tick = hours_per_tick
        self._logger.info(f"时间流逝速度已更改: {old_speed}小时/tick -> {hours_per_tick}小时/tick")
    
    def set_tick_interval(self, interval: int):
        """设置tick间隔
        
        Args:
            interval: tick间隔（秒）
        """
        old_interval = self.tick_interval
        self.tick_interval = interval
        self._logger.info(f"Tick间隔已更改: {old_interval}秒 -> {interval}秒")
    
    def advance_time(self, hours: int = None):
        """手动推进时间
        
        Args:
            hours: 要推进的小时数，默认为hours_per_tick
        """
        if hours is None:
            hours = self.hours_per_tick
        
        old_time = self.game_time.current_time
        self._advance_game_time(hours)
        
        self._logger.info(f"手动推进时间: {old_time} -> {self.game_time.current_time} (+{hours}小时)")
    
    def set_game_time(self, new_time: datetime):
        """设置游戏时间
        
        Args:
            new_time: 新的游戏时间
        """
        old_time = self.game_time.current_time
        self.game_time.current_time = new_time
        
        # 重新计算总小时数
        time_diff = new_time - self.game_time.start_time
        self.game_time.total_hours_elapsed = int(time_diff.total_seconds() // 3600)
        
        self._logger.info(f"游戏时间已设置: {old_time} -> {new_time}")
    
    def get_game_time(self) -> GameTime:
        """获取当前游戏时间"""
        return self.game_time
    
    def add_tick_callback(self, callback: Callable[[GameTime], None]):
        """添加tick回调函数
        
        Args:
            callback: 每次tick时调用的函数
        """
        self._tick_callbacks.append(callback)
        self._logger.debug(f"添加tick回调: {callback.__name__}")
    
    def add_hour_callback(self, callback: Callable[[GameTime], None]):
        """添加小时回调函数
        
        Args:
            callback: 每小时调用的函数
        """
        self._hour_callbacks.append(callback)
        self._logger.debug(f"添加小时回调: {callback.__name__}")
    
    def add_day_callback(self, callback: Callable[[GameTime], None]):
        """添加日回调函数
        
        Args:
            callback: 每天调用的函数
        """
        self._day_callbacks.append(callback)
        self._logger.debug(f"添加日回调: {callback.__name__}")
    
    async def _time_loop(self):
        """时间循环主逻辑"""
        self._logger.info("时间循环开始")
        
        try:
            while self._running:
                await asyncio.sleep(self.tick_interval)
                
                if not self._running:
                    break
                
                if not self.game_time.is_paused:
                    await self._process_tick()
                
        except asyncio.CancelledError:
            self._logger.info("时间循环被取消")
        except Exception as e:
            self._logger.error(f"时间循环异常: {e}", exc_info=True)
        finally:
            self._logger.info("时间循环结束")
    
    async def _process_tick(self):
        """处理单次tick"""
        try:
            # 记录tick开始时间
            tick_start = datetime.now()
            
            # 推进游戏时间
            old_hour = self.game_time.current_time.hour
            old_day = self.game_time.current_time.day
            
            self._advance_game_time(self.hours_per_tick)
            
            # 创建并发布时间事件
            time_event = TimeTickEvent(
                timestamp=datetime.now(),
                event_id=f"tick_{self.game_time.tick_count}",
                source="time_service",
                game_time=self.game_time.current_time,
                tick_number=self.game_time.tick_count,
                hours_elapsed=self.hours_per_tick
            )
            
            await self.event_bus.publish(time_event)
            
            # 调用回调函数
            await self._call_callbacks(old_hour, old_day)
            
            # 更新统计信息
            self._stats['total_ticks'] += 1
            self._stats['events_published'] += 1
            self._stats['last_tick_time'] = tick_start
            
            # 记录性能信息
            tick_duration = (datetime.now() - tick_start).total_seconds()
            if tick_duration > 1.0:  # 如果tick处理超过1秒，记录警告
                self._logger.warning(f"Tick处理耗时过长: {tick_duration:.2f}秒")
            
        except Exception as e:
            self._logger.error(f"处理tick时发生错误: {e}", exc_info=True)
    
    def _advance_game_time(self, hours: int):
        """推进游戏时间
        
        Args:
            hours: 要推进的小时数
        """
        self.game_time.current_time += timedelta(hours=hours)
        self.game_time.tick_count += 1
        self.game_time.total_hours_elapsed += hours
    
    async def _call_callbacks(self, old_hour: int, old_day: int):
        """调用相应的回调函数
        
        Args:
            old_hour: 之前的小时
            old_day: 之前的日期
        """
        try:
            # 总是调用tick回调
            for callback in self._tick_callbacks:
                try:
                    callback(self.game_time)
                except Exception as e:
                    self._logger.error(f"Tick回调执行失败 {callback.__name__}: {e}")
            
            # 如果小时发生变化，调用小时回调
            if self.game_time.current_time.hour != old_hour:
                for callback in self._hour_callbacks:
                    try:
                        callback(self.game_time)
                    except Exception as e:
                        self._logger.error(f"小时回调执行失败 {callback.__name__}: {e}")
            
            # 如果日期发生变化，调用日回调
            if self.game_time.current_time.day != old_day:
                for callback in self._day_callbacks:
                    try:
                        callback(self.game_time)
                    except Exception as e:
                        self._logger.error(f"日回调执行失败 {callback.__name__}: {e}")
                        
        except Exception as e:
            self._logger.error(f"调用回调函数时发生错误: {e}", exc_info=True)
    
    def get_stats(self) -> dict:
        """获取时间服务统计信息"""
        current_time = datetime.now()
        service_uptime = None
        
        if self._stats['service_start_time']:
            service_uptime = (current_time - self._stats['service_start_time']).total_seconds()
        
        return {
            **self._stats,
            'service_uptime_seconds': service_uptime,
            'is_running': self._running,
            'is_paused': self.game_time.is_paused,
            'current_game_time': self.game_time.current_time.isoformat(),
            'game_days_elapsed': self.game_time.get_elapsed_days(),
            'tick_interval': self.tick_interval,
            'hours_per_tick': self.hours_per_tick,
            'callbacks_registered': {
                'tick': len(self._tick_callbacks),
                'hour': len(self._hour_callbacks),
                'day': len(self._day_callbacks)
            }
        }
    
    def format_game_time(self, include_seconds: bool = False) -> str:
        """格式化游戏时间为字符串
        
        Args:
            include_seconds: 是否包含秒数
            
        Returns:
            格式化的时间字符串
        """
        if include_seconds:
            time_str = self.game_time.current_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = self.game_time.current_time.strftime("%Y-%m-%d %H:%M")
        
        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        day_name = day_names[self.game_time.get_current_day_of_week()]
        
        return f"{time_str} ({day_name})"