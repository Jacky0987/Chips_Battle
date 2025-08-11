# -*- coding: utf-8 -*-
"""
认证服务

负责用户认证、权限管理和角色管理。
"""

import logging
import hashlib
import secrets
import uuid
from typing import Optional, List, Dict, Any, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from sqlalchemy import select
from dal.unit_of_work import AbstractUnitOfWork
from models.auth.user import User
from models.auth.role import Role
from models.auth.permission import Permission
from core.event_bus import EventBus, UserActionEvent
from core.game_time import GameTime


class AuthResult(Enum):
    """认证结果枚举"""
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_NOT_FOUND = "user_not_found"
    USER_DISABLED = "user_disabled"
    PASSWORD_EXPIRED = "password_expired"
    ACCOUNT_LOCKED = "account_locked"
    TOO_MANY_ATTEMPTS = "too_many_attempts"


@dataclass
class LoginAttempt:
    """登录尝试记录"""
    user_id: str
    ip_address: str
    timestamp: datetime
    success: bool
    failure_reason: Optional[str] = None


@dataclass
class Session:
    """用户会话"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    is_active: bool = True
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class AuthService:
    """认证服务"""
    
    def __init__(self, uow: AbstractUnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus
        self._logger = logging.getLogger(__name__)
        
        # 会话管理
        self._sessions: Dict[str, Session] = {}  # session_id -> Session
        self._user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        
        # 登录尝试跟踪
        self._login_attempts: List[LoginAttempt] = []
        self._failed_attempts: Dict[str, List[datetime]] = {}  # user_id -> failed_attempt_times
        
        # 配置
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.session_timeout = timedelta(hours=24)
        self.password_min_length = 6
        self.require_special_chars = False
        
        # 统计信息
        self._stats = {
            'total_logins': 0,
            'successful_logins': 0,
            'failed_logins': 0,
            'active_sessions': 0,
            'users_created': 0,
            'start_time': GameTime.now() if GameTime.is_initialized() else datetime.now()
        }
    
    async def register_user(self, username: str, password: str, email: str = None) -> tuple[bool, str, Optional[User]]:
        """注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            
        Returns:
            (是否成功, 消息, 用户对象)
        """
        try:
            # 验证输入
            if not username or not password:
                return False, "用户名和密码不能为空", None
            
            if len(username) < 3:
                return False, "用户名至少需要3个字符", None
            
            if not self._validate_password(password):
                return False, f"密码至少需要{self.password_min_length}个字符", None
            
            async with self.uow:
                # 检查用户名是否已存在
                result = await self.uow.session.execute(select(User).filter_by(username=username))
                existing_user = result.scalars().first()
                
                if existing_user:
                    return False, "用户名已存在", None
                
                # 创建新用户
                user_id = str(uuid.uuid4())
                password_hash = self._hash_password(password)
                
                user = User(
                    user_id=user_id,
                    username=username,
                    password_hash=password_hash,
                    email=email,
                    created_at=GameTime.now() if GameTime.is_initialized() else datetime.now(),
                    is_active=True,
                    last_login=None
                )
                
                self.uow.add(user)
                
                # 分配默认角色
                await self._assign_default_role(user)
                
                await self.uow.commit()
                
                self._stats['users_created'] += 1
                self._logger.info(f"新用户注册成功: {username} (ID: {user_id})")
                
                # 发布用户注册事件
                await self._publish_user_event(user, "user_registered")
                
                return True, "注册成功", user
                
        except Exception as e:
            self._logger.error(f"用户注册失败: {e}", exc_info=True)
            return False, f"注册失败: {str(e)}", None
    
    async def authenticate(self, username: str, password: str, ip_address: str = "unknown") -> tuple[AuthResult, Optional[User]]:
        """用户认证
        
        Args:
            username: 用户名
            password: 密码
            ip_address: IP地址
            
        Returns:
            (认证结果, 用户对象)
        """
        self._stats['total_logins'] += 1
        
        try:
            async with self.uow:
                # 查找用户
                result = await self.uow.session.execute(select(User).filter_by(username=username))
                user = result.scalars().first()
                
                if not user:
                    await self._record_login_attempt(None, ip_address, False, "user_not_found")
                    self._stats['failed_logins'] += 1
                    return AuthResult.USER_NOT_FOUND, None
                
                # 检查账户状态
                if not user.is_active:
                    await self._record_login_attempt(user.user_id, ip_address, False, "user_disabled")
                    self._stats['failed_logins'] += 1
                    return AuthResult.USER_DISABLED, None
                
                # 检查账户是否被锁定
                if await self._is_account_locked(user.user_id):
                    await self._record_login_attempt(user.user_id, ip_address, False, "account_locked")
                    self._stats['failed_logins'] += 1
                    return AuthResult.ACCOUNT_LOCKED, None
                
                # 验证密码
                if not self._verify_password(password, user.password_hash):
                    self._logger.warning(f"用户 {username} 密码验证失败，IP: {ip_address}")
                    await self._record_failed_attempt(user.user_id)
                    await self._record_login_attempt(user.user_id, ip_address, False, "invalid_password")
                    self._stats['failed_logins'] += 1
                    return AuthResult.INVALID_CREDENTIALS, None
                
                # 认证成功
                self._logger.info(f"用户 {username} 认证成功，IP: {ip_address}")
                user.last_login = GameTime.now() if GameTime.is_initialized() else datetime.now()
                user.login_count += 1  # 更新登录次数
                await self.uow.commit()
                
                # 清除失败尝试记录
                if user.user_id in self._failed_attempts:
                    del self._failed_attempts[user.user_id]
                
                await self._record_login_attempt(user.user_id, ip_address, True)
                self._stats['successful_logins'] += 1
                
                # 发布登录事件
                await self._publish_user_event(user, "user_login", {'ip_address': ip_address})
                
                return AuthResult.SUCCESS, user
                
        except Exception as e:
            self._logger.error(f"用户 {username} 认证过程异常: {e}", exc_info=True)
            self._stats['failed_logins'] += 1
            return AuthResult.INVALID_CREDENTIALS, None
    
    async def create_session(self, user: User, ip_address: str = "unknown") -> Session:
        """创建用户会话
        
        Args:
            user: 用户对象
            ip_address: IP地址
            
        Returns:
            会话对象
        """
        session_id = secrets.token_urlsafe(32)
        
        current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            created_at=current_time,
            last_activity=current_time,
            ip_address=ip_address
        )
        
        self._sessions[session_id] = session
        
        if user.user_id not in self._user_sessions:
            self._user_sessions[user.user_id] = set()
        self._user_sessions[user.user_id].add(session_id)
        
        self._stats['active_sessions'] += 1
        
        self._logger.info(f"创建会话: {session_id} (用户: {user.username})")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象或None
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        # 检查会话是否过期
        current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
        if current_time - session.last_activity > self.session_timeout:
            await self.destroy_session(session_id)
            return None
        
        # 更新最后活动时间
        session.last_activity = current_time
        
        return session
    
    async def destroy_session(self, session_id: str) -> bool:
        """销毁会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功销毁
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return False
        
        # 从用户会话集合中移除
        if session.user_id in self._user_sessions:
            self._user_sessions[session.user_id].discard(session_id)
            if not self._user_sessions[session.user_id]:
                del self._user_sessions[session.user_id]
        
        # 删除会话
        del self._sessions[session_id]
        self._stats['active_sessions'] -= 1
        
        self._logger.info(f"销毁会话: {session_id}")
        
        return True
    
    async def has_permission(self, user: User, permission_name: str) -> bool:
        """检查用户是否有特定权限
        
        Args:
            user: 用户对象
            permission_name: 权限名称
            
        Returns:
            是否有权限
        """
        try:
            async with self.uow:
                # 通过用户角色查询权限
                stmt = select(Role).join(User.roles).where(User.user_id == user.user_id)
                result = await self.uow.session.execute(stmt)
                user_roles = result.scalars().all()
                
                for role in user_roles:
                    stmt = select(Permission).join(Role.permissions).where(Role.role_id == role.role_id)
                    result = await self.uow.session.execute(stmt)
                    role_permissions = result.scalars().all()
                    
                    for permission in role_permissions:
                        if permission.name == permission_name:
                            return True
                
                return False
                
        except Exception as e:
            self._logger.error(f"权限检查异常: {e}", exc_info=True)
            return False
    
    async def has_role(self, user: User, role_name: str) -> bool:
        """检查用户是否有特定角色
        
        Args:
            user: 用户对象
            role_name: 角色名称
            
        Returns:
            是否有角色
        """
        try:
            async with self.uow:
                # 查询用户是否有指定角色
                stmt = select(Role).join(User.roles).where(User.user_id == user.user_id, Role.name == role_name)
                result = await self.uow.session.execute(stmt)
                user_roles = result.scalars().all()
                
                return len(user_roles) > 0
                
        except Exception as e:
            self._logger.error(f"角色检查异常: {e}", exc_info=True)
            return False
    
    def authenticate_admin_password(self, password: str) -> bool:
        """简单的管理员密码验证
        
        Args:
            password: 输入的密码
            
        Returns:
            是否验证成功
        """
        # 简单的硬编码管理员密码验证
        return password == "admin"
    
    async def get_user_roles(self, user: User) -> List[Role]:
        """获取用户角色列表
        
        Args:
            user: 用户对象
            
        Returns:
            角色列表
        """
        try:
            async with self.uow:
                stmt = select(Role).join(User.roles).where(User.user_id == user.user_id)
                result = await self.uow.session.execute(stmt)
                return result.scalars().all()
                
        except Exception as e:
            self._logger.error(f"获取用户角色异常: {e}", exc_info=True)
            return []
    
    async def get_user_permissions(self, user: User) -> List[Permission]:
        """获取用户权限列表
        
        Args:
            user: 用户对象
            
        Returns:
            权限列表
        """
        try:
            permissions = set()
            user_roles = await self.get_user_roles(user)
            
            async with self.uow:
                for role in user_roles:
                    stmt = select(Permission).join(Role.permissions).where(Role.role_id == role.role_id)
                    result = await self.uow.session.execute(stmt)
                    role_permissions = result.scalars().all()
                    permissions.update(role_permissions)
            
            return list(permissions)
            
        except Exception as e:
            self._logger.error(f"获取用户权限异常: {e}", exc_info=True)
            return []
    
    def _hash_password(self, password: str) -> str:
        """哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码
        
        Args:
            password: 明文密码
            password_hash: 存储的哈希密码
            
        Returns:
            是否匹配
        """
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == stored_hash
        except Exception:
            return False
    
    def _validate_password(self, password: str) -> bool:
        """验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            是否符合要求
        """
        if len(password) < self.password_min_length:
            return False
        
        if self.require_special_chars:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False
        
        return True
    
    async def _is_account_locked(self, user_id: str) -> bool:
        """检查账户是否被锁定
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否被锁定
        """
        if user_id not in self._failed_attempts:
            return False
        
        failed_times = self._failed_attempts[user_id]
        
        # 清理过期的失败记录
        current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
        cutoff_time = current_time - self.lockout_duration
        failed_times = [t for t in failed_times if t > cutoff_time]
        self._failed_attempts[user_id] = failed_times
        
        return len(failed_times) >= self.max_failed_attempts
    
    async def _record_failed_attempt(self, user_id: str):
        """记录失败尝试
        
        Args:
            user_id: 用户ID
        """
        if user_id not in self._failed_attempts:
            self._failed_attempts[user_id] = []
        
        self._failed_attempts[user_id].append(GameTime.now() if GameTime.is_initialized() else datetime.now())
    
    async def _record_login_attempt(self, user_id: Optional[str], ip_address: str, success: bool, failure_reason: str = None):
        """记录登录尝试
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            success: 是否成功
            failure_reason: 失败原因
        """
        attempt = LoginAttempt(
            user_id=user_id or "unknown",
            ip_address=ip_address,
            timestamp=GameTime.now() if GameTime.is_initialized() else datetime.now(),
            success=success,
            failure_reason=failure_reason
        )
        
        self._login_attempts.append(attempt)
        
        # 限制记录数量
        max_attempts = 1000
        if len(self._login_attempts) > max_attempts:
            self._login_attempts = self._login_attempts[-max_attempts:]
    
    async def _assign_default_role(self, user: User):
        """分配默认角色
        
        Args:
            user: 用户对象
        """
        try:
            async with self.uow:
                # 查找默认角色
                stmt = select(Role).filter_by(name='user', is_default=True)
                result = await self.uow.session.execute(stmt)
                default_role = result.scalars().first()
            
                if default_role:
                    # 将角色添加到用户的角色列表中
                    if not user.roles:
                        user.roles = []
                    user.roles.append(default_role)
                
        except Exception as e:
            self._logger.error(f"分配默认角色失败: {e}", exc_info=True)
    
    async def _publish_user_event(self, user: User, action: str, details: Dict[str, Any] = None):
        """发布用户事件
        
        Args:
            user: 用户对象
            action: 行为
            details: 详细信息
        """
        try:
            current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
            event = UserActionEvent(
                timestamp=current_time,
                event_id=f"auth_{action}_{user.user_id}_{current_time.timestamp()}",
                source="auth_service",
                user_id=user.user_id,
                action=action,
                details=details or {}
            )
            
            await self.event_bus.publish(event)
            
        except Exception as e:
            self._logger.error(f"发布用户事件失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取认证服务统计信息
        
        Returns:
            统计信息字典
        """
        current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
        uptime = (current_time - self._stats['start_time']).total_seconds()
        
        return {
            **self._stats,
            'uptime_seconds': uptime,
            'login_success_rate': (
                self._stats['successful_logins'] / max(self._stats['total_logins'], 1)
            ) * 100,
            'locked_accounts': len([uid for uid, attempts in self._failed_attempts.items() 
                                  if len(attempts) >= self.max_failed_attempts]),
            'recent_login_attempts': len(self._login_attempts)
        }
    
    async def cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = []
        current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
        
        for session_id, session in self._sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.destroy_session(session_id)
        
        if expired_sessions:
            self._logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
    
    async def has_permission(self, user: User, permission_name: str) -> bool:
        """检查用户是否具有指定权限
        
        Args:
            user: 用户对象
            permission_name: 权限名称
            
        Returns:
            是否具有权限
        """
        try:
            async with self.uow:
                # 查询用户的所有角色
                user_roles_result = await self.uow.session.execute(
                    select(Role).join(User.roles).filter(User.user_id == user.user_id)
                )
                user_roles = user_roles_result.scalars().all()
                
                # 检查每个角色的权限
                for role in user_roles:
                    role_permissions_result = await self.uow.session.execute(
                        select(Permission).join(Role.permissions).filter(Role.role_id == role.role_id)
                    )
                    role_permissions = role_permissions_result.scalars().all()
                    
                    # 检查是否有匹配的权限
                    for permission in role_permissions:
                        if permission.name == permission_name:
                            return True
                
                return False
                
        except Exception as e:
            self._logger.error(f"检查权限失败: {e}")
            return False
    
    async def get_user_permissions(self, user: User) -> List[str]:
        """获取用户的所有权限
        
        Args:
            user: 用户对象
            
        Returns:
            权限名称列表
        """
        try:
            async with self.uow:
                # 查询用户的所有角色
                user_roles_result = await self.uow.session.execute(
                    select(Role).join(User.roles).filter(User.user_id == user.user_id)
                )
                user_roles = user_roles_result.scalars().all()
                
                permissions = set()
                
                # 收集所有角色的权限
                for role in user_roles:
                    role_permissions_result = await self.uow.session.execute(
                        select(Permission).join(Role.permissions).filter(Role.role_id == role.role_id)
                    )
                    role_permissions = role_permissions_result.scalars().all()
                    
                    for permission in role_permissions:
                        permissions.add(permission.name)
                
                return list(permissions)
                
        except Exception as e:
            self._logger.error(f"获取用户权限失败: {e}")
            return []


# 全局权限装饰器
def permission_required(permission_name: str, auth_service: 'AuthService' = None):
    """权限检查装饰器
    
    Args:
        permission_name: 所需权限名称
        auth_service: 认证服务实例（可选，如果不提供会从上下文中获取）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from commands.base import CommandContext, CommandResult
            
            # 查找CommandContext参数
            context = None
            for arg in args:
                if isinstance(arg, CommandContext):
                    context = arg
                    break
            
            # 从kwargs中查找context
            if context is None:
                context = kwargs.get('context')
            
            if context is None:
                return CommandResult(
                    success=False,
                    message="❌ 无法获取命令执行上下文"
                )
            
            if context.user is None:
                return CommandResult(
                    success=False,
                    message="❌ 用户未登录"
                )
            
            # 获取认证服务
            service = auth_service
            if service is None and hasattr(context, 'registry') and context.registry:
                # 尝试从命令注册器获取认证服务
                service = getattr(context.registry, '_auth_service', None)
            
            if service is None:
                return CommandResult(
                    success=False,
                    message="❌ 认证服务不可用"
                )
            
            # 检查权限
            has_perm = await service.has_permission(context.user, permission_name)
            if not has_perm:
                return CommandResult(
                    success=False,
                    message=f"❌ 权限不足，需要权限: {permission_name}"
                )
            
            # 执行原函数
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator