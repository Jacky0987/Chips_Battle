# -*- coding: utf-8 -*-
"""
应用模型

定义应用的数据结构和业务逻辑
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Numeric
from sqlalchemy.sql import func
from models.base import Base


class App(Base):
    """应用模型
    
    表示系统中的应用程序
    """
    __tablename__ = 'apps'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, comment='应用名称')
    description = Column(Text, comment='应用描述')
    version = Column(String(20), comment='应用版本')
    category = Column(String(50), comment='应用分类')
    price = Column(Numeric(10, 2), default=0, comment='应用价格')
    is_active = Column(Boolean, default=True, comment='是否激活')
    is_free = Column(Boolean, default=False, comment='是否免费')
    download_count = Column(Integer, default=0, comment='下载次数')
    rating = Column(Numeric(3, 2), default=0, comment='评分')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def __repr__(self):
        return f"<App(id='{self.id}', name='{self.name}', version='{self.version}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'category': self.category,
            'price': float(self.price) if self.price else 0,
            'is_active': self.is_active,
            'is_free': self.is_free,
            'download_count': self.download_count,
            'rating': float(self.rating) if self.rating else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }