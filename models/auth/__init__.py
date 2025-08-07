# -*- coding: utf-8 -*-
"""
认证模块

包含用户认证、角色和权限相关的数据模型。
"""

from models.auth.user import User
from models.auth.role import Role, user_roles, role_permissions
from models.auth.permission import Permission, PermissionType, PermissionScope

# 导出所有认证相关模型
__all__ = [
    'User',
    'Role',
    'Permission',
    'PermissionType',
    'PermissionScope',
    'user_roles',
    'role_permissions'
]