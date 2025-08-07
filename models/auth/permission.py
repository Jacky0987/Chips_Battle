# -*- coding: utf-8 -*-
"""
权限模型

定义系统权限和访问控制相关的数据结构。
"""

from sqlalchemy import Column, String, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from models.base import BaseModel
from models.auth.role import role_permissions


class PermissionType(Enum):
    """权限类型枚举"""
    SYSTEM = "system"          # 系统权限
    CONTENT = "content"        # 内容权限
    FINANCE = "finance"        # 财务权限
    SOCIAL = "social"          # 社交权限
    ADMIN = "admin"            # 管理权限
    API = "api"                # API权限
    FEATURE = "feature"        # 功能权限


class PermissionScope(Enum):
    """权限范围枚举"""
    GLOBAL = "global"          # 全局权限
    PERSONAL = "personal"      # 个人权限
    GROUP = "group"            # 群组权限
    RESOURCE = "resource"      # 资源权限


class Permission(BaseModel):
    """权限模型"""
    
    __tablename__ = 'permissions'
    
    # 基本信息
    permission_id = Column(String(36), primary_key=True, comment='权限唯一标识')
    name = Column(String(100), unique=True, nullable=False, index=True, comment='权限名称')
    display_name = Column(String(150), nullable=False, comment='显示名称')
    description = Column(Text, nullable=True, comment='权限描述')
    
    # 权限属性
    permission_type = Column(SQLEnum(PermissionType), nullable=False, comment='权限类型')
    scope = Column(SQLEnum(PermissionScope), default=PermissionScope.GLOBAL, nullable=False, comment='权限范围')
    
    # 权限控制
    is_system = Column(Boolean, default=False, nullable=False, comment='是否为系统权限')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否激活')
    is_dangerous = Column(Boolean, default=False, nullable=False, comment='是否为危险权限')
    
    # 层级和分组
    category = Column(String(50), nullable=True, comment='权限分类')
    subcategory = Column(String(50), nullable=True, comment='权限子分类')
    level = Column(Integer, default=0, nullable=False, comment='权限等级')
    
    # 依赖关系
    parent_permission = Column(String(36), nullable=True, comment='父权限ID')
    required_permissions = Column(Text, nullable=True, comment='依赖权限列表(JSON)')
    
    # 限制条件
    max_usage_per_day = Column(Integer, nullable=True, comment='每日最大使用次数')
    cooldown_seconds = Column(Integer, nullable=True, comment='冷却时间(秒)')
    
    # 关联关系
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.display_name:
            self.display_name = self.name.replace('_', ' ').title()
    
    def __repr__(self):
        return f"<Permission(permission_id='{self.permission_id}', name='{self.name}', type='{self.permission_type.value}')>"
    
    def to_dict(self, include_roles: bool = False) -> Dict[str, Any]:
        """转换为字典
        
        Args:
            include_roles: 是否包含角色信息
            
        Returns:
            权限信息字典
        """
        data = {
            'permission_id': self.permission_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'permission_type': self.permission_type.value,
            'scope': self.scope.value,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'is_dangerous': self.is_dangerous,
            'category': self.category,
            'subcategory': self.subcategory,
            'level': self.level,
            'parent_permission': self.parent_permission,
            'required_permissions': self.get_required_permissions(),
            'max_usage_per_day': self.max_usage_per_day,
            'cooldown_seconds': self.cooldown_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_roles and self.roles:
            data['roles'] = [
                role.get_display_info() for role in self.roles
            ]
            data['role_count'] = len(self.roles)
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Permission':
        """从字典创建权限对象
        
        Args:
            data: 权限数据字典
            
        Returns:
            权限对象
        """
        # 处理枚举字段
        if 'permission_type' in data and isinstance(data['permission_type'], str):
            data['permission_type'] = PermissionType(data['permission_type'])
        
        if 'scope' in data and isinstance(data['scope'], str):
            data['scope'] = PermissionScope(data['scope'])
        
        # 处理时间字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # 处理依赖权限
        if 'required_permissions' in data and isinstance(data['required_permissions'], list):
            import json
            data['required_permissions'] = json.dumps(data['required_permissions'])
        
        # 移除关联关系字段
        perm_data = {k: v for k, v in data.items() 
                    if k not in ['roles', 'role_count']}
        
        return cls(**perm_data)
    
    def get_required_permissions(self) -> List[str]:
        """获取依赖权限列表
        
        Returns:
            依赖权限名称列表
        """
        if not self.required_permissions:
            return []
        
        try:
            import json
            return json.loads(self.required_permissions)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_required_permissions(self, permissions: List[str]):
        """设置依赖权限
        
        Args:
            permissions: 权限名称列表
        """
        import json
        self.required_permissions = json.dumps(permissions) if permissions else None
        self.updated_at = datetime.now()
    
    def add_required_permission(self, permission_name: str):
        """添加依赖权限
        
        Args:
            permission_name: 权限名称
        """
        required = self.get_required_permissions()
        if permission_name not in required:
            required.append(permission_name)
            self.set_required_permissions(required)
    
    def remove_required_permission(self, permission_name: str):
        """移除依赖权限
        
        Args:
            permission_name: 权限名称
        """
        required = self.get_required_permissions()
        if permission_name in required:
            required.remove(permission_name)
            self.set_required_permissions(required)
    
    def is_granted_to_role(self, role_name: str) -> bool:
        """检查是否已授予指定角色
        
        Args:
            role_name: 角色名称
            
        Returns:
            是否已授予
        """
        if not self.roles:
            return False
        
        return any(role.name == role_name for role in self.roles)
    
    def get_role_names(self) -> List[str]:
        """获取拥有此权限的角色名称列表
        
        Returns:
            角色名称列表
        """
        if not self.roles:
            return []
        
        return [role.name for role in self.roles]
    
    def can_be_granted(self) -> tuple[bool, str]:
        """检查是否可以被授予
        
        Returns:
            (是否可以授予, 原因)
        """
        if not self.is_active:
            return False, "权限未激活"
        
        return True, "可以授予"
    
    def get_full_name(self) -> str:
        """获取完整权限名称
        
        Returns:
            完整权限名称
        """
        parts = []
        
        if self.category:
            parts.append(self.category)
        
        if self.subcategory:
            parts.append(self.subcategory)
        
        parts.append(self.name)
        
        return '.'.join(parts)
    
    def get_hierarchy_level(self) -> int:
        """获取权限层级深度
        
        Returns:
            层级深度
        """
        level = 0
        if self.category:
            level += 1
        if self.subcategory:
            level += 1
        return level
    
    def is_child_of(self, parent_permission: 'Permission') -> bool:
        """检查是否为指定权限的子权限
        
        Args:
            parent_permission: 父权限
            
        Returns:
            是否为子权限
        """
        return self.parent_permission == parent_permission.permission_id
    
    def get_status(self) -> str:
        """获取权限状态
        
        Returns:
            状态字符串
        """
        if not self.is_active:
            return "inactive"
        elif self.is_dangerous:
            return "dangerous"
        elif self.is_system:
            return "system"
        else:
            return "active"
    
    def get_display_info(self) -> Dict[str, Any]:
        """获取用于显示的权限信息
        
        Returns:
            显示信息字典
        """
        return {
            'permission_id': self.permission_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'type': self.permission_type.value,
            'scope': self.scope.value,
            'category': self.category,
            'level': self.level,
            'status': self.get_status(),
            'role_count': len(self.roles) if self.roles else 0,
            'full_name': self.get_full_name()
        }
    
    def validate(self) -> tuple[bool, List[str]]:
        """验证权限数据
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 基础验证
        is_valid, base_errors = super().is_valid()
        errors.extend(base_errors)
        
        # 权限特定验证
        if not self.name or len(self.name.strip()) == 0:
            errors.append("权限名称不能为空")
        
        if len(self.name) > 100:
            errors.append("权限名称不能超过100个字符")
        
        if not self.display_name or len(self.display_name.strip()) == 0:
            errors.append("显示名称不能为空")
        
        if self.level < 0:
            errors.append("权限等级不能为负数")
        
        if self.max_usage_per_day is not None and self.max_usage_per_day < 0:
            errors.append("每日最大使用次数不能为负数")
        
        if self.cooldown_seconds is not None and self.cooldown_seconds < 0:
            errors.append("冷却时间不能为负数")
        
        # 检查权限名称格式
        if not self.name.replace('_', '').replace('.', '').isalnum():
            errors.append("权限名称只能包含字母、数字、下划线和点号")
        
        return len(errors) == 0, errors
    
    def activate(self):
        """激活权限"""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self):
        """停用权限"""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def mark_as_dangerous(self):
        """标记为危险权限"""
        self.is_dangerous = True
        self.updated_at = datetime.now()
    
    def unmark_as_dangerous(self):
        """取消危险权限标记"""
        self.is_dangerous = False
        self.updated_at = datetime.now()
    
    @classmethod
    def create_system_defaults(cls) -> List['Permission']:
        """创建系统默认权限（别名方法）
        
        Returns:
            系统权限列表
        """
        return cls.create_system_permissions()
    
    @classmethod
    def create_system_permissions(cls) -> List['Permission']:
        """创建系统默认权限
        
        Returns:
            系统权限列表
        """
        import uuid
        
        permissions = [
            # 系统管理权限
            cls(
                permission_id=str(uuid.uuid4()),
                name='system.admin.full',
                display_name='系统完全管理',
                description='拥有系统的完全管理权限',
                permission_type=PermissionType.SYSTEM,
                scope=PermissionScope.GLOBAL,
                is_system=True,
                is_dangerous=True,
                category='system',
                subcategory='admin',
                level=100
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='system.user.manage',
                display_name='用户管理',
                description='管理用户账户',
                permission_type=PermissionType.ADMIN,
                scope=PermissionScope.GLOBAL,
                is_system=True,
                category='system',
                subcategory='user',
                level=80
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='system.role.manage',
                display_name='角色管理',
                description='管理用户角色和权限',
                permission_type=PermissionType.ADMIN,
                scope=PermissionScope.GLOBAL,
                is_system=True,
                is_dangerous=True,
                category='system',
                subcategory='role',
                level=90
            ),
            
            # 内容管理权限
            cls(
                permission_id=str(uuid.uuid4()),
                name='content.news.create',
                display_name='创建新闻',
                description='创建和发布新闻文章',
                permission_type=PermissionType.CONTENT,
                scope=PermissionScope.GLOBAL,
                is_system=True,
                category='content',
                subcategory='news',
                level=30
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='content.news.edit',
                display_name='编辑新闻',
                description='编辑新闻文章',
                permission_type=PermissionType.CONTENT,
                scope=PermissionScope.GLOBAL,
                is_system=True,
                category='content',
                subcategory='news',
                level=40
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='content.news.delete',
                display_name='删除新闻',
                description='删除新闻文章',
                permission_type=PermissionType.CONTENT,
                scope=PermissionScope.GLOBAL,
                is_system=True,
                category='content',
                subcategory='news',
                level=50
            ),
            
            # 财务权限
            cls(
                permission_id=str(uuid.uuid4()),
                name='finance.wallet.view',
                display_name='查看钱包',
                description='查看自己的钱包余额',
                permission_type=PermissionType.FINANCE,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='finance',
                subcategory='wallet',
                level=10
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='finance.transfer.send',
                display_name='转账',
                description='向其他用户转账',
                permission_type=PermissionType.FINANCE,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='finance',
                subcategory='transfer',
                level=20
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='finance.stock.trade',
                display_name='股票交易',
                description='买卖股票',
                permission_type=PermissionType.FINANCE,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='finance',
                subcategory='stock',
                level=25
            ),
            
            # 应用权限
            cls(
                permission_id=str(uuid.uuid4()),
                name='app.create',
                display_name='创建应用',
                description='在应用市场创建应用',
                permission_type=PermissionType.FEATURE,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='app',
                level=30
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='app.publish',
                display_name='发布应用',
                description='发布应用到市场',
                permission_type=PermissionType.FEATURE,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='app',
                level=35
            ),
            
            # 基础权限
            cls(
                permission_id=str(uuid.uuid4()),
                name='basic.login',
                display_name='登录',
                description='登录系统',
                permission_type=PermissionType.SYSTEM,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='basic',
                level=1
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='basic.profile.view',
                display_name='查看个人资料',
                description='查看自己的个人资料',
                permission_type=PermissionType.SOCIAL,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='basic',
                subcategory='profile',
                level=5
            ),
            cls(
                permission_id=str(uuid.uuid4()),
                name='basic.profile.edit',
                display_name='编辑个人资料',
                description='编辑自己的个人资料',
                permission_type=PermissionType.SOCIAL,
                scope=PermissionScope.PERSONAL,
                is_system=True,
                category='basic',
                subcategory='profile',
                level=10
            )
        ]
        
        return permissions
    
    @classmethod
    def get_permissions_by_category(cls, permissions: List['Permission'], category: str) -> List['Permission']:
        """按分类获取权限
        
        Args:
            permissions: 权限列表
            category: 分类名称
            
        Returns:
            指定分类的权限列表
        """
        return [perm for perm in permissions if perm.category == category]
    
    @classmethod
    def get_permissions_by_type(cls, permissions: List['Permission'], permission_type: PermissionType) -> List['Permission']:
        """按类型获取权限
        
        Args:
            permissions: 权限列表
            permission_type: 权限类型
            
        Returns:
            指定类型的权限列表
        """
        return [perm for perm in permissions if perm.permission_type == permission_type]