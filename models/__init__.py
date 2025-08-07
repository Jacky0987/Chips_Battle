# -*- coding: utf-8 -*-
"""
数据模型模块

包含游戏中所有的数据模型定义。
"""

from models.base import BaseModel, Base
from models.auth.user import User
from models.auth.role import Role
from models.auth.permission import Permission

# 导出所有模型
__all__ = [
    'BaseModel',
    'Base', 
    'User',
    'Role',
    'Permission'
]