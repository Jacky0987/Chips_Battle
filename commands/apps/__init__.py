# -*- coding: utf-8 -*-
"""
应用命令模块

提供各种应用和工具相关的命令。
"""

from .calculator import CalculatorCommand
from .news import NewsCommand
from .weather import WeatherCommand

__all__ = [
    'CalculatorCommand',
    'NewsCommand', 
    'WeatherCommand'
]