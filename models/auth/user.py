# -*- coding: utf-8 -*-
"""
用户模型

定义用户实体和相关的数据结构。
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from models.base import BaseModel, get_game_time_now
from models.bank.bank_card import BankCard
from core.game_time import GameTime


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = 'users'
    
    # 基本信息
    user_id = Column(String(36), primary_key=True, comment='用户唯一标识')
    username = Column(String(50), unique=True, nullable=False, index=True, comment='用户名')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    email = Column(String(100), unique=True, nullable=True, index=True, comment='邮箱')
    
    # 个人信息
    display_name = Column(String(100), nullable=True, comment='显示名称')
    avatar_url = Column(String(255), nullable=True, comment='头像URL')
    bio = Column(Text, nullable=True, comment='个人简介')
    
    # 账户状态
    is_active = Column(Boolean, default=True, nullable=False, comment='是否激活')
    is_verified = Column(Boolean, default=False, nullable=False, comment='是否已验证')
    is_banned = Column(Boolean, default=False, nullable=False, comment='是否被封禁')
    
    # 时间字段
    created_at = Column(DateTime, default=get_game_time_now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=get_game_time_now, onupdate=get_game_time_now, nullable=False, comment='更新时间')
    last_login = Column(DateTime, nullable=True, comment='最后登录时间')
    last_activity = Column(DateTime, nullable=True, comment='最后活动时间')
    
    # 游戏相关
    level = Column(Integer, default=1, nullable=False, comment='用户等级')
    experience = Column(Integer, default=0, nullable=False, comment='经验值')
    reputation = Column(Integer, default=0, nullable=False, comment='声望值')
    
    # 统计信息
    login_count = Column(Integer, default=0, nullable=False, comment='登录次数')
    command_count = Column(Integer, default=0, nullable=False, comment='命令执行次数')
    
    # 设置和偏好
    timezone = Column(String(50), default='UTC', nullable=False, comment='时区')
    language = Column(String(10), default='zh-CN', nullable=False, comment='语言')
    theme = Column(String(20), default='default', nullable=False, comment='主题')
    
    # 关联关系
    roles = relationship('Role', secondary='user_roles', back_populates='users')
    accounts = relationship('Account', back_populates='user')
    app_ownerships = relationship('UserAppOwnership', back_populates='user')
    bank_accounts = relationship('BankAccount', back_populates='user')
    bank_cards = relationship('BankCard', back_populates='user')
    loans = relationship('Loan', back_populates='user')
    credit_profile = relationship('CreditProfile', back_populates='user', uselist=False)
    # wallets = relationship('Wallet', back_populates='user')
    # achievements = relationship('Achievement', secondary='user_achievements', back_populates='users')
    # news_articles = relationship('NewsArticle', back_populates='author')
    
    def __init__(self, **kwargs):
        # 如果没有提供user_id，自动生成UUID
        if 'user_id' not in kwargs or not kwargs['user_id']:
            import uuid
            kwargs['user_id'] = str(uuid.uuid4())
        
        super().__init__(**kwargs)
        if not self.display_name:
            self.display_name = self.username
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}', username='{self.username}', level={self.level})>"
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """转换为字典
        
        Args:
            include_sensitive: 是否包含敏感信息
            
        Returns:
            用户信息字典
        """
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email if include_sensitive else None,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_banned': self.is_banned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'level': self.level,
            'experience': self.experience,
            'reputation': self.reputation,
            'login_count': self.login_count,
            'command_count': self.command_count,
            'timezone': self.timezone,
            'language': self.language,
            'theme': self.theme
        }
        
        # 移除None值
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象
        
        Args:
            data: 用户数据字典
            
        Returns:
            用户对象
        """
        # 处理时间字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'last_login' in data and isinstance(data['last_login'], str):
            data['last_login'] = datetime.fromisoformat(data['last_login'])
        
        if 'last_activity' in data and isinstance(data['last_activity'], str):
            data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        
        return cls(**data)
    
    def update_activity(self):
        """更新最后活动时间"""
        if GameTime.is_initialized():
            self.last_activity = GameTime.now()
        else:
            # 如果游戏时间未初始化，使用实际时间
            self.last_activity = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def increment_login_count(self):
        """增加登录次数"""
        self.login_count += 1
        if GameTime.is_initialized():
            self.last_login = GameTime.now()
        else:
            # 如果游戏时间未初始化，使用实际时间
            self.last_login = GameTime.now() if GameTime.is_initialized() else datetime.now()
        self.update_activity()
    
    def increment_command_count(self):
        """增加命令执行次数"""
        self.command_count += 1
        self.update_activity()
    
    def add_experience(self, amount: int) -> bool:
        """增加经验值
        
        Args:
            amount: 经验值数量
            
        Returns:
            是否升级
        """
        old_level = self.level
        self.experience += amount
        
        # 计算新等级（简单的等级计算公式）
        new_level = int((self.experience / 100) ** 0.5) + 1
        
        if new_level > self.level:
            self.level = new_level
            return True  # 升级了
        
        return False  # 没有升级
    
    def get_level_progress(self) -> Dict[str, int]:
        """获取等级进度
        
        Returns:
            包含当前等级、经验值、下一级所需经验等信息的字典
        """
        current_level_exp = ((self.level - 1) ** 2) * 100
        next_level_exp = (self.level ** 2) * 100
        
        return {
            'current_level': self.level,
            'current_experience': self.experience,
            'current_level_exp': current_level_exp,
            'next_level_exp': next_level_exp,
            'progress': self.experience - current_level_exp,
            'required': next_level_exp - self.experience
        }
    
    def is_online(self, timeout_minutes: int = 5) -> bool:
        """检查用户是否在线
        
        Args:
            timeout_minutes: 超时分钟数
            
        Returns:
            是否在线
        """
        if not self.last_activity:
            return False
        
        from datetime import timedelta
        timeout = timedelta(minutes=timeout_minutes)
        current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
        return current_time - self.last_activity < timeout
    
    def get_status(self) -> str:
        """获取用户状态
        
        Returns:
            状态字符串
        """
        if self.is_banned:
            return "banned"
        elif not self.is_active:
            return "inactive"
        elif not self.is_verified:
            return "unverified"
        elif self.is_online():
            return "online"
        else:
            return "offline"
    
    def can_perform_action(self, action: str) -> bool:
        """检查用户是否可以执行特定操作
        
        Args:
            action: 操作名称
            
        Returns:
            是否可以执行
        """
        # 基本状态检查
        if self.is_banned or not self.is_active:
            return False
        
        # 根据操作类型进行不同的检查
        if action in ['post_news', 'create_app']:
            return self.is_verified and self.level >= 5
        elif action in ['trade_stocks', 'transfer_money']:
            return self.is_verified
        elif action in ['chat', 'view_market']:
            return True
        
        return True
    
    def get_display_info(self) -> Dict[str, Any]:
        """获取用于显示的用户信息
        
        Returns:
            显示信息字典
        """
        return {
            'username': self.username,
            'display_name': self.display_name,
            'level': self.level,
            'reputation': self.reputation,
            'status': self.get_status(),
            'avatar_url': self.avatar_url,
            'is_verified': self.is_verified
        }
    
    def update_profile(self, **kwargs):
        """更新用户资料
        
        Args:
            **kwargs: 要更新的字段
        """
        allowed_fields = {
            'display_name', 'bio', 'avatar_url', 'timezone', 
            'language', 'theme'
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        if GameTime.is_initialized():
            self.updated_at = GameTime.now()
        else:
            self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def ban(self, reason: str = None):
        """封禁用户
        
        Args:
            reason: 封禁原因
        """
        self.is_banned = True
        self.is_active = False
        if GameTime.is_initialized():
            self.updated_at = GameTime.now()
        else:
            self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
        # 这里可以记录封禁日志
    
    def unban(self):
        """解封用户"""
        self.is_banned = False
        self.is_active = True
        if GameTime.is_initialized():
            self.updated_at = GameTime.now()
        else:
            self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
        # 这里可以记录解封日志
    
    def verify(self):
        """验证用户"""
        self.is_verified = True
        if GameTime.is_initialized():
            self.updated_at = GameTime.now()
        else:
            self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def deactivate(self):
        """停用账户"""
        self.is_active = False
        if GameTime.is_initialized():
            self.updated_at = GameTime.now()
        else:
            self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()
    
    def activate(self):
        """激活账户"""
        self.is_active = True
        if GameTime.is_initialized():
            self.updated_at = GameTime.now()
        else:
            self.updated_at = GameTime.now() if GameTime.is_initialized() else datetime.now()