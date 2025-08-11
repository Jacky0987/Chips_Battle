# -*- coding: utf-8 -*-
"""
游戏时间工具类

提供统一的时间获取接口，确保所有游戏逻辑使用同一个时间源。
"""

import logging
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.time_service import TimeService


class GameTime:
    """游戏时间工具类"""
    
    _time_service: Optional['TimeService'] = None
    _logger = logging.getLogger(__name__)
    
    @classmethod
    def set_time_service(cls, time_service: 'TimeService'):
        """设置时间服务实例
        
        Args:
            time_service: 时间服务实例
        """
        cls._time_service = time_service
        cls._logger.info("游戏时间服务已设置")
    
    @classmethod
    def now(cls) -> datetime:
        """获取当前游戏时间
        
        Returns:
            当前游戏时间
            
        Raises:
            RuntimeError: 如果时间服务未初始化
        """
        if cls._time_service is None:
            raise RuntimeError("时间服务未初始化，请先调用 GameTime.set_time_service()")
        return cls._time_service.get_game_time()
    
    @classmethod
    def real_now(cls) -> datetime:
        """获取当前实际时间（仅用于系统级操作）
        
        注意：此方法仅应用于日志记录、性能统计等系统级操作，
        游戏逻辑应始终使用 GameTime.now()
        
        Returns:
            当前实际时间
        """
        return datetime.now()
    
    @classmethod
    def is_initialized(cls) -> bool:
        """检查时间服务是否已初始化
        
        Returns:
            是否已初始化
        """
        return cls._time_service is not None
    
    @classmethod
    def get_time_service(cls) -> Optional['TimeService']:
        """获取时间服务实例
        
        Returns:
            时间服务实例或None
        """
        return cls._time_service
    
    @classmethod
    def format_time(cls, include_seconds: bool = False) -> str:
        """格式化当前游戏时间为字符串
        
        Args:
            include_seconds: 是否包含秒数
            
        Returns:
            格式化的时间字符串
            
        Raises:
            RuntimeError: 如果时间服务未初始化
        """
        if cls._time_service is None:
            raise RuntimeError("时间服务未初始化")
        return cls._time_service.format_game_time(include_seconds)
    
    @classmethod
    def get_time_scale(cls) -> float:
        """获取当前时间倍率
        
        Returns:
            时间倍率
            
        Raises:
            RuntimeError: 如果时间服务未初始化
        """
        if cls._time_service is None:
            raise RuntimeError("时间服务未初始化")
        return cls._time_service.get_time_scale()
    
    @classmethod
    def is_paused(cls) -> bool:
        """检查时间是否暂停
        
        Returns:
            是否暂停
            
        Raises:
            RuntimeError: 如果时间服务未初始化
        """
        if cls._time_service is None:
            raise RuntimeError("时间服务未初始化")
        return cls._time_service.is_paused()
    
    @classmethod
    def is_market_hours(cls) -> bool:
        """判断是否为市场交易时间
        
        Returns:
            是否为市场时间
            
        Raises:
            RuntimeError: 如果时间服务未初始化
        """
        if cls._time_service is None:
            raise RuntimeError("时间服务未初始化")
        return cls._time_service.is_market_hours()
    
    @classmethod
    def is_business_hours(cls) -> bool:
        """判断是否为营业时间
        
        Returns:
            是否为营业时间
            
        Raises:
            RuntimeError: 如果时间服务未初始化
        """
        if cls._time_service is None:
            raise RuntimeError("时间服务未初始化")
        return cls._time_service.is_business_hours()


# 便捷函数，用于向后兼容
def game_now() -> datetime:
    """获取当前游戏时间的便捷函数
    
    Returns:
        当前游戏时间
    """
    return GameTime.now()


def real_now() -> datetime:
    """获取当前实际时间的便捷函数
    
    Returns:
        当前实际时间
    """
    return GameTime.real_now()