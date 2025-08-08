# -*- coding: utf-8 -*-
"""
新闻模型

定义新闻的数据结构和业务逻辑
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Numeric
from sqlalchemy.sql import func
from models.base import Base
import uuid


class News(Base):
    """新闻模型
    
    表示系统中的新闻信息
    """
    __tablename__ = 'news'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment='新闻标题')
    content = Column(Text, nullable=False, comment='新闻内容')
    summary = Column(String(500), comment='新闻摘要')
    author = Column(String(100), comment='作者')
    source = Column(String(100), comment='新闻来源')
    category = Column(String(50), comment='新闻分类')
    tags = Column(String(200), comment='标签')
    view_count = Column(Integer, default=0, comment='浏览次数')
    is_published = Column(Boolean, default=False, comment='是否发布')
    is_featured = Column(Boolean, default=False, comment='是否推荐')
    impact_type = Column(String(50), default='neutral', comment='市场影响类型')
    impact_strength = Column(Numeric(5, 2), default=0.0, comment='市场影响强度')
    published_at = Column(DateTime, comment='发布时间')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def __repr__(self):
        return f"<News(id='{self.id}', title='{self.title}', author='{self.author}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'author': self.author,
            'source': self.source,
            'category': self.category,
            'tags': self.tags,
            'view_count': self.view_count,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'impact_type': self.impact_type,
            'impact_strength': float(self.impact_strength) if self.impact_strength is not None else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }