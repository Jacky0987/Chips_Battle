# -*- coding: utf-8 -*-
"""
时间服务

管理游戏内的时间流逝，包括：
- 游戏时间的推进
- 时间相关事件的触发
- 时间倍率控制
- 暂停/恢复功能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, List
from dataclasses import dataclass
from core.event_bus import EventBus
from core.events import TimeTickEvent, TimeHourEvent, TimeDayEvent
from core.game_time_manager import GameTimeManager
from core.time_event_scheduler import TimeEventScheduler
from core.game_time import GameTime


@dataclass
class GameTimeData:
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
        
        # 初始化时间管理器
        self.time_manager = GameTimeManager(
            start_time=datetime(2024, 1, 1, 9, 0, 0)  # 游戏开始时间：2024年1月1日 9:00
        )
        
        # 初始化事件调度器
        self.event_scheduler = TimeEventScheduler()
        
        # 游戏时间状态（保持向后兼容）
        self.game_time = GameTimeData(
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
        self._tick_callbacks: List[Callable[[GameTimeData], None]] = []
        self._hour_callbacks: List[Callable[[GameTimeData], None]] = []
        self._day_callbacks: List[Callable[[GameTimeData], None]] = []
        
        # 统计信息
        self._stats = {
            'total_ticks': 0,
            'events_published': 0,
            'service_start_time': None,
            'last_tick_time': None
        }
    
    def _get_current_time(self) -> datetime:
        """获取当前时间，在异步线程中使用系统时间
        
        Returns:
            当前时间
        """
        # 在时间服务中始终使用系统时间，避免GUI事件循环问题
        # GameTime.now()只能在主线程中调用
        return datetime.now()
    
    def _sync_game_time_state(self, current_time: datetime):
        """同步GameTime状态以保持向后兼容
        
        Args:
            current_time: 当前游戏时间
        """
        # 计算时间差
        time_diff = current_time - self.game_time.current_time
        hours_elapsed = int(time_diff.total_seconds() // 3600)
        
        # 更新GameTime状态
        self.game_time.current_time = current_time
        self.game_time.tick_count += 1
        self.game_time.total_hours_elapsed += hours_elapsed
    
    def start(self):
        """启动时间服务"""
        if self._running:
            self._logger.warning("时间服务已经在运行")
            return
        
        self._running = True
        # 使用系统时间而不是GameTime.now()，避免事件循环问题
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
        if not self._running:
            self._logger.warning("时间服务未运行，无法暂停")
            return
        
        if self.game_time.is_paused:
            self._logger.warning("时间已经暂停")
            return
        
        self.game_time.is_paused = True
        self.time_manager.pause()
        self._logger.info("游戏时间已暂停")
    
    def resume(self):
        """恢复游戏时间"""
        if not self._running:
            self._logger.warning("时间服务未运行，无法恢复")
            return
        
        if not self.game_time.is_paused:
            self._logger.warning("时间未暂停")
            return
        
        self.game_time.is_paused = False
        self.time_manager.resume()
        self._logger.info("游戏时间已恢复")
    
    def is_paused(self) -> bool:
        """检查时间是否暂停
        
        Returns:
            是否暂停
        """
        return self.game_time.is_paused
    
    def set_time_speed(self, speed: float):
        """设置时间流逝速度
        
        Args:
            speed: 时间倍率，1.0为正常速度，2.0为2倍速
        """
        if speed <= 0:
            raise ValueError("时间速度必须大于0")
        
        old_speed = self.time_manager.get_time_scale()
        self.time_manager.set_time_scale(speed)
        # 保持向后兼容
        self.hours_per_tick = speed
        self._logger.info(f"时间速度已调整: {old_speed}x -> {speed}x")
    
    def set_time_scale(self, scale: float):
        """设置时间倍率（别名方法）
        
        Args:
            scale: 时间倍率
        """
        self.set_time_speed(scale)
    
    def get_time_scale(self) -> float:
        """获取当前时间倍率
        
        Returns:
            当前时间倍率
        """
        return self.time_manager.get_time_scale()
    
    def set_tick_interval(self, interval: float):
        """设置tick间隔
        
        Args:
            interval: tick间隔（秒）
        """
        if interval <= 0:
            raise ValueError("tick间隔必须大于0")
        
        old_interval = self.tick_interval
        self.tick_interval = interval
        self._logger.info(f"Tick间隔已调整: {old_interval}s -> {interval}s")
    
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
    
    def get_game_time(self) -> datetime:
        """获取当前游戏时间
        
        Returns:
            当前游戏时间
        """
        return self.time_manager.get_current_time()
    
    def get_game_time_state(self) -> GameTime:
        """获取游戏时间状态（向后兼容）
        
        Returns:
            当前游戏时间状态
        """
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
        last_real_time = self._get_current_time()
        
        try:
            while self._running:
                await asyncio.sleep(self.tick_interval)
                
                if not self._running:
                    break
                
                if not self.game_time.is_paused:
                    # 计算实际时间差
                    current_real_time = self._get_current_time()
                    real_delta = (current_real_time - last_real_time).total_seconds()
                    last_real_time = current_real_time
                    
                    # 使用时间管理器更新游戏时间
                    self.time_manager.update()
                    
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
            tick_start = self._get_current_time()
            
            # 获取当前游戏时间
            current_game_time = self.time_manager.get_current_time()
            old_hour = self.game_time.current_time.hour
            old_day = self.game_time.current_time.day
            
            # 同步更新旧的GameTime状态（向后兼容）
            self._sync_game_time_state(current_game_time)
            
            # 处理事件调度器
            executed_events = await self.event_scheduler.check_and_fire_events(current_game_time)
            
            # 创建并发布时间事件
            current_time = self._get_current_time()
            time_event = TimeTickEvent(
                timestamp=current_time,
                event_id=f"tick_{self.game_time.tick_count}",
                source="time_service",
                game_time=self.game_time.current_time,
                tick_number=self.game_time.tick_count,
                hours_elapsed=self.hours_per_tick
            )
            
            await self.event_bus.publish(time_event)
            
            # 发布小时和日事件
            await self._publish_time_events(old_hour, old_day, current_game_time)
            
            # 调用回调函数
            await self._call_callbacks(old_hour, old_day)
            
            # 更新统计信息
            self._stats['total_ticks'] += 1
            self._stats['events_published'] += 1
            self._stats['last_tick_time'] = tick_start
            
            # 记录性能信息
            current_end_time = self._get_current_time()
            tick_duration = (current_end_time - tick_start).total_seconds()
            if tick_duration > 1.0:  # 如果tick处理超过1秒，记录警告
                self._logger.warning(f"Tick处理耗时过长: {tick_duration:.2f}秒")
            
        except Exception as e:
            self._logger.error(f"处理tick时发生错误: {e}", exc_info=True)
    
    async def _publish_time_events(self, old_hour: int, old_day: int, current_game_time: datetime):
        """发布时间相关事件
        
        Args:
            old_hour: 之前的小时
            old_day: 之前的日期
            current_game_time: 当前游戏时间
        """
        try:
            current_time = self._get_current_time()
            
            # 如果小时发生变化，发布小时事件
            if current_game_time.hour != old_hour:
                hour_event = TimeHourEvent(
                    timestamp=current_time,
                    event_id=f"hour_{current_game_time.hour}_{self.game_time.tick_count}",
                    source="time_service",
                    game_time=current_game_time,
                    hour=current_game_time.hour,
                    day=current_game_time.day
                )
                await self.event_bus.publish(hour_event)
                self._stats['events_published'] += 1
                self._logger.debug(f"发布小时事件: {current_game_time.hour}:00")
            
            # 如果日期发生变化，发布日事件
            if current_game_time.day != old_day:
                day_event = TimeDayEvent(
                    timestamp=current_time,
                    event_id=f"day_{current_game_time.day}_{self.game_time.tick_count}",
                    source="time_service",
                    game_time=current_game_time,
                    day=current_game_time.day,
                    week=current_game_time.isocalendar()[1]  # ISO周数
                )
                await self.event_bus.publish(day_event)
                self._stats['events_published'] += 1
                self._logger.debug(f"发布日事件: {current_game_time.strftime('%Y-%m-%d')}")
                
        except Exception as e:
            self._logger.error(f"发布时间事件失败: {e}", exc_info=True)
    
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
        # 使用系统时间而不是GameTime.now()，避免GUI事件循环问题
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
        current_time = self.time_manager.get_current_time()
        if include_seconds:
            return current_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return current_time.strftime("%Y-%m-%d %H:%M")
    
    def is_market_hours(self) -> bool:
        """判断是否为市场交易时间
        
        Returns:
            是否为市场时间（9:00-15:00）
        """
        current_time = self.time_manager.get_current_time()
        hour = current_time.hour
        return 9 <= hour < 15
    
    def is_business_hours(self) -> bool:
        """判断是否为营业时间
        
        Returns:
            是否为营业时间（8:00-18:00）
        """
        current_time = self.time_manager.get_current_time()
        hour = current_time.hour
        return 8 <= hour < 18
    
    def schedule_event(self, callback: Callable[[], None], delay_hours: float = 0, recurring_hours: float = None, description: str = "") -> str:
        """调度事件
        
        Args:
            callback: 要调度的回调函数
            delay_hours: 延迟小时数
            recurring_hours: 重复间隔小时数（None表示不重复）
            description: 事件描述
            
        Returns:
            事件ID
        """
        current_time = self.time_manager.get_current_time()
        
        if recurring_hours:
            return self.event_scheduler.schedule_recurring(
                recurring_hours, callback, current_time, description
            )
        else:
            return self.event_scheduler.schedule_after(
                delay_hours, callback, current_time, description
            )
    
    def format_game_time_with_day(self, include_seconds: bool = False) -> str:
        """格式化游戏时间为包含星期的字符串
        
        Args:
            include_seconds: 是否包含秒数
            
        Returns:
            格式化的时间字符串
        """
        time_str = self.format_game_time(include_seconds)
        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        day_name = day_names[self.game_time.get_current_day_of_week()]
        
        return f"{time_str} ({day_name})"