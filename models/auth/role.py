# -*- coding: utf-8 -*-
"""
角色模型

定义用户角色和权限管理相关的数据结构。
"""

from sqlalchemy import Column, String, Boolean, Text, Integer, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Any, Optional
from models.base import BaseModel, get_game_time_now


# 用户-角色关联表
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', String(36), ForeignKey('users.user_id'), primary_key=True),
    Column('role_id', String(36), ForeignKey('roles.role_id'), primary_key=True),
    Column('assigned_at', DateTime, default=get_game_time_now, nullable=False),
    Column('assigned_by', String(36), nullable=True),
    comment='用户角色关联表'
)


# 角色-权限关联表
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', String(36), ForeignKey('roles.role_id'), primary_key=True),
    Column('permission_id', String(36), ForeignKey('permissions.permission_id'), primary_key=True),
    Column('granted_at', DateTime, default=get_game_time_now, nullable=False),
    Column('granted_by', String(36), nullable=True),
    comment='角色权限关联表'
)


class Role(BaseModel):
    """角色模型"""
    
    __tablename__ = 'roles'
    
    # 基本信息
    role_id = Column(String(36), primary_key=True, comment='角色唯一标识')
    name = Column(String(50), unique=True, nullable=False, index=True, comment='角色名称')
    display_name = Column(String(100), nullable=False, comment='显示名称')
    description = Column(Text, nullable=True, comment='角色描述')
    
    # 角色属性
    is_system = Column(Boolean, default=False, nullable=False, comment='是否为系统角色')
    is_default = Column(Boolean, default=False, nullable=False, comment='是否为默认角色')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否激活')
    
    # 层级和优先级
    level = Column(Integer, default=0, nullable=False, comment='角色等级')
    priority = Column(Integer, default=0, nullable=False, comment='优先级')
    
    # 限制
    max_users = Column(Integer, nullable=True, comment='最大用户数限制')
    
    # 关联关系
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.display_name:
            self.display_name = self.name.title()
    
    def __repr__(self):
        return f"<Role(role_id='{self.role_id}', name='{self.name}', level={self.level})>"
    
    def to_dict(self, include_permissions: bool = False, include_users: bool = False) -> Dict[str, Any]:
        """转换为字典
        
        Args:
            include_permissions: 是否包含权限信息
            include_users: 是否包含用户信息
            
        Returns:
            角色信息字典
        """
        data = {
            'role_id': self.role_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'is_system': self.is_system,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'level': self.level,
            'priority': self.priority,
            'max_users': self.max_users,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_permissions and self.permissions:
            data['permissions'] = [
                perm.to_dict() for perm in self.permissions
            ]
        
        if include_users and self.users:
            data['users'] = [
                user.get_display_info() for user in self.users
            ]
            data['user_count'] = len(self.users)
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """从字典创建角色对象
        
        Args:
            data: 角色数据字典
            
        Returns:
            角色对象
        """
        # 处理时间字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # 移除关联关系字段
        role_data = {k: v for k, v in data.items() 
                    if k not in ['permissions', 'users', 'user_count']}
        
        return cls(**role_data)
    
    def has_permission(self, permission_name: str) -> bool:
        """检查角色是否有特定权限
        
        Args:
            permission_name: 权限名称
            
        Returns:
            是否有权限
        """
        if not self.permissions:
            return False
        
        return any(perm.name == permission_name for perm in self.permissions)
    
    def get_permission_names(self) -> List[str]:
        """获取角色的所有权限名称
        
        Returns:
            权限名称列表
        """
        if not self.permissions:
            return []
        
        return [perm.name for perm in self.permissions]
    
    def can_assign_to_user(self) -> tuple[bool, str]:
        """检查是否可以分配给用户
        
        Returns:
            (是否可以分配, 原因)
        """
        if not self.is_active:
            return False, "角色未激活"
        
        if self.max_users and len(self.users) >= self.max_users:
            return False, f"角色用户数已达上限({self.max_users})"
        
        return True, "可以分配"
    
    def get_user_count(self) -> int:
        """获取拥有此角色的用户数量
        
        Returns:
            用户数量
        """
        return len(self.users) if self.users else 0
    
    def is_higher_than(self, other_role: 'Role') -> bool:
        """检查是否比另一个角色等级更高
        
        Args:
            other_role: 另一个角色
            
        Returns:
            是否等级更高
        """
        if self.level != other_role.level:
            return self.level > other_role.level
        
        return self.priority > other_role.priority
    
    def can_manage_role(self, target_role: 'Role') -> bool:
        """检查是否可以管理目标角色
        
        Args:
            target_role: 目标角色
            
        Returns:
            是否可以管理
        """
        # 系统角色只能由系统管理
        if target_role.is_system and not self.is_system:
            return False
        
        # 只能管理等级更低的角色
        return self.is_higher_than(target_role)
    
    def get_effective_permissions(self) -> List['Permission']:
        """获取有效权限（包括继承的权限）
        
        Returns:
            权限列表
        """
        # 目前只返回直接权限，后续可以实现权限继承
        return list(self.permissions) if self.permissions else []
    
    def add_permission(self, permission: 'Permission') -> bool:
        """添加权限
        
        Args:
            permission: 权限对象
            
        Returns:
            是否成功添加
        """
        if not self.permissions:
            self.permissions = []
        
        if permission not in self.permissions:
            self.permissions.append(permission)
            return True
        
        return False
    
    def remove_permission(self, permission: 'Permission') -> bool:
        """移除权限
        
        Args:
            permission: 权限对象
            
        Returns:
            是否成功移除
        """
        if self.permissions and permission in self.permissions:
            self.permissions.remove(permission)
            return True
        
        return False
    
    def clear_permissions(self):
        """清空所有权限"""
        if self.permissions:
            self.permissions.clear()
    
    def clone(self, new_name: str, **overrides) -> 'Role':
        """克隆角色
        
        Args:
            new_name: 新角色名称
            **overrides: 要覆盖的字段
            
        Returns:
            新角色对象
        """
        import uuid
        
        data = self.to_dict()
        data.update({
            'role_id': str(uuid.uuid4()),
            'name': new_name,
            'is_system': False,  # 克隆的角色不是系统角色
            'is_default': False,  # 克隆的角色不是默认角色
            **overrides
        })
        
        return self.from_dict(data)
    
    def get_status(self) -> str:
        """获取角色状态
        
        Returns:
            状态字符串
        """
        if not self.is_active:
            return "inactive"
        elif self.is_system:
            return "system"
        elif self.is_default:
            return "default"
        else:
            return "active"
    
    def get_display_info(self) -> Dict[str, Any]:
        """获取用于显示的角色信息
        
        Returns:
            显示信息字典
        """
        return {
            'role_id': self.role_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'level': self.level,
            'status': self.get_status(),
            'user_count': self.get_user_count(),
            'permission_count': len(self.permissions) if self.permissions else 0
        }
    
    def validate(self) -> tuple[bool, List[str]]:
        """验证角色数据
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 基础验证
        is_valid, base_errors = super().is_valid()
        errors.extend(base_errors)
        
        # 角色特定验证
        if not self.name or len(self.name.strip()) == 0:
            errors.append("角色名称不能为空")
        
        if len(self.name) > 50:
            errors.append("角色名称不能超过50个字符")
        
        if not self.display_name or len(self.display_name.strip()) == 0:
            errors.append("显示名称不能为空")
        
        if self.level < 0:
            errors.append("角色等级不能为负数")
        
        if self.max_users is not None and self.max_users < 0:
            errors.append("最大用户数不能为负数")
        
        return len(errors) == 0, errors
    
    def activate(self):
        """激活角色"""
        self.is_active = True
        self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def deactivate(self):
        """停用角色"""
        self.is_active = False
        self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def set_as_default(self):
        """设置为默认角色"""
        self.is_default = True
        self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def unset_as_default(self):
        """取消默认角色"""
        self.is_default = False
        self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    @classmethod
    def create_system_defaults(cls) -> List['Role']:
        """创建系统默认角色（别名方法）
        
        Returns:
            系统角色列表
        """
        return cls.create_system_roles()
    
    @classmethod
    def create_system_roles(cls) -> List['Role']:
        """创建系统默认角色
        
        Returns:
            系统角色列表
        """
        import uuid
        
        roles = [
            cls(
                role_id=str(uuid.uuid4()),
                name='admin',
                display_name='管理员',
                description='系统管理员，拥有所有权限',
                is_system=True,
                is_active=True,
                level=100,
                priority=1000
            ),
            cls(
                role_id=str(uuid.uuid4()),
                name='moderator',
                display_name='版主',
                description='版主，拥有内容管理权限',
                is_system=True,
                is_active=True,
                level=50,
                priority=500
            ),
            cls(
                role_id=str(uuid.uuid4()),
                name='user',
                display_name='普通用户',
                description='普通用户，拥有基本权限',
                is_system=True,
                is_default=True,
                is_active=True,
                level=1,
                priority=100
            ),
            cls(
                role_id=str(uuid.uuid4()),
                name='guest',
                display_name='访客',
                description='访客用户，只有查看权限',
                is_system=True,
                is_active=True,
                level=0,
                priority=10
            )
        ]
        
        return roles