# -*- coding: utf-8 -*-
"""
用户应用所有权模型

定义用户拥有的应用关系
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class UserAppOwnership(Base):
    """用户应用所有权模型
    
    表示用户拥有的应用
    """
    __tablename__ = 'user_app_ownership'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, comment='用户ID')
    app_id = Column(String(36), ForeignKey('apps.id'), nullable=False, comment='应用ID')
    purchase_price = Column(Numeric(10, 2), comment='购买价格')
    is_active = Column(Boolean, default=True, comment='是否激活')
    purchased_at = Column(DateTime, default=func.now(), comment='购买时间')
    activated_at = Column(DateTime, comment='激活时间')
    expires_at = Column(DateTime, comment='过期时间')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    user = relationship("User", back_populates="app_ownerships")
    app = relationship("App")
    
    def __repr__(self):
        return f"<UserAppOwnership(id='{self.id}', user_id='{self.user_id}', app_id='{self.app_id}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'app_id': self.app_id,
            'purchase_price': float(self.purchase_price) if self.purchase_price else 0,
            'is_active': self.is_active,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None,
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }