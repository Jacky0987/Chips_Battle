# -*- coding: utf-8 -*-
"""
基础模型

定义所有数据模型的基类和通用功能。
"""

from dal.database import Base
from sqlalchemy import Column, DateTime, String, Text, Boolean, Integer
from datetime import datetime
from typing import Dict, Any, Optional
import json





class BaseModel(Base):
    """所有模型的基类"""
    
    __abstract__ = True
    
    # 通用字段
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def __init__(self, **kwargs):
        """初始化模型
        
        Args:
            **kwargs: 字段值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self, exclude: Optional[list] = None, include_relationships: bool = False) -> Dict[str, Any]:
        """转换为字典
        
        Args:
            exclude: 要排除的字段列表
            include_relationships: 是否包含关联关系
            
        Returns:
            字典表示
        """
        exclude = exclude or []
        result = {}
        
        # 获取所有列
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                
                # 处理特殊类型
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif value is not None:
                    result[column.name] = value
        
        # 包含关联关系（如果需要）
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                if relationship.key not in exclude:
                    related_obj = getattr(self, relationship.key)
                    if related_obj is not None:
                        if hasattr(related_obj, '__iter__') and not isinstance(related_obj, str):
                            # 一对多或多对多关系
                            result[relationship.key] = [
                                obj.to_dict(exclude=exclude) if hasattr(obj, 'to_dict') else str(obj)
                                for obj in related_obj
                            ]
                        else:
                            # 一对一关系
                            result[relationship.key] = (
                                related_obj.to_dict(exclude=exclude) 
                                if hasattr(related_obj, 'to_dict') 
                                else str(related_obj)
                            )
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """从字典创建模型实例
        
        Args:
            data: 数据字典
            
        Returns:
            模型实例
        """
        # 过滤掉不存在的字段
        filtered_data = {}
        for key, value in data.items():
            if hasattr(cls, key):
                # 处理时间字段
                if key in ['created_at', 'updated_at'] and isinstance(value, str):
                    try:
                        filtered_data[key] = datetime.fromisoformat(value)
                    except ValueError:
                        continue
                else:
                    filtered_data[key] = value
        
        return cls(**filtered_data)
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[list] = None):
        """从字典更新模型
        
        Args:
            data: 数据字典
            exclude: 要排除的字段列表
        """
        exclude = exclude or ['created_at', 'updated_at']
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                # 处理时间字段
                if key.endswith('_at') and isinstance(value, str):
                    try:
                        value = datetime.fromisoformat(value)
                    except ValueError:
                        continue
                
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
    
    def to_json(self, **kwargs) -> str:
        """转换为JSON字符串
        
        Args:
            **kwargs: to_dict的参数
            
        Returns:
            JSON字符串
        """
        return json.dumps(self.to_dict(**kwargs), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """从JSON字符串创建模型实例
        
        Args:
            json_str: JSON字符串
            
        Returns:
            模型实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self):
        """字符串表示"""
        class_name = self.__class__.__name__
        
        # 尝试获取主键值
        primary_keys = []
        for column in self.__table__.primary_key.columns:
            value = getattr(self, column.name, None)
            if value is not None:
                primary_keys.append(f"{column.name}='{value}'")
        
        pk_str = ', '.join(primary_keys) if primary_keys else 'no_pk'
        return f"<{class_name}({pk_str})>"
    
    def __str__(self):
        """用户友好的字符串表示"""
        return self.__repr__()
    
    def __eq__(self, other):
        """相等性比较"""
        if not isinstance(other, self.__class__):
            return False
        
        # 比较主键
        for column in self.__table__.primary_key.columns:
            if getattr(self, column.name) != getattr(other, column.name):
                return False
        
        return True
    
    def __hash__(self):
        """哈希值"""
        # 基于主键计算哈希
        pk_values = []
        for column in self.__table__.primary_key.columns:
            value = getattr(self, column.name)
            if value is not None:
                pk_values.append(str(value))
        
        return hash(tuple(pk_values)) if pk_values else hash(id(self))
    
    def clone(self, **overrides) -> 'BaseModel':
        """克隆模型实例
        
        Args:
            **overrides: 要覆盖的字段值
            
        Returns:
            新的模型实例
        """
        data = self.to_dict(exclude=['created_at', 'updated_at'])
        data.update(overrides)
        return self.__class__.from_dict(data)
    
    def get_changes(self, other: 'BaseModel') -> Dict[str, tuple]:
        """获取与另一个实例的差异
        
        Args:
            other: 另一个模型实例
            
        Returns:
            差异字典，格式为 {field: (old_value, new_value)}
        """
        if not isinstance(other, self.__class__):
            raise ValueError("Cannot compare with different model type")
        
        changes = {}
        
        for column in self.__table__.columns:
            field_name = column.name
            old_value = getattr(self, field_name)
            new_value = getattr(other, field_name)
            
            if old_value != new_value:
                changes[field_name] = (old_value, new_value)
        
        return changes
    
    def is_valid(self) -> tuple[bool, list]:
        """验证模型数据
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 检查必填字段
        for column in self.__table__.columns:
            if not column.nullable and column.default is None:
                value = getattr(self, column.name)
                if value is None:
                    errors.append(f"Field '{column.name}' is required")
        
        # 检查字符串长度
        for column in self.__table__.columns:
            if hasattr(column.type, 'length') and column.type.length:
                value = getattr(self, column.name)
                if isinstance(value, str) and len(value) > column.type.length:
                    errors.append(
                        f"Field '{column.name}' exceeds maximum length of {column.type.length}"
                    )
        
        return len(errors) == 0, errors
    
    def refresh_timestamps(self):
        """刷新时间戳"""
        self.updated_at = datetime.now()
    
    @classmethod
    def get_table_name(cls) -> str:
        """获取表名
        
        Returns:
            表名
        """
        return cls.__tablename__
    
    @classmethod
    def get_column_names(cls) -> list:
        """获取所有列名
        
        Returns:
            列名列表
        """
        return [column.name for column in cls.__table__.columns]
    
    @classmethod
    def get_primary_key_names(cls) -> list:
        """获取主键列名
        
        Returns:
            主键列名列表
        """
        return [column.name for column in cls.__table__.primary_key.columns]
    
    def get_primary_key_values(self) -> Dict[str, Any]:
        """获取主键值
        
        Returns:
            主键值字典
        """
        result = {}
        for column in self.__table__.primary_key.columns:
            result[column.name] = getattr(self, column.name)
        return result


class TimestampMixin:
    """时间戳混入类"""
    
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')


class SoftDeleteMixin:
    """软删除混入类"""
    
    deleted_at = Column(DateTime, nullable=True, comment='删除时间')
    is_deleted = Column(Boolean, default=False, nullable=False, comment='是否已删除')
    
    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.updated_at = datetime.now()
    
    def restore(self):
        """恢复"""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.now()


class AuditMixin:
    """审计混入类"""
    
    created_by = Column(String(36), nullable=True, comment='创建者ID')
    updated_by = Column(String(36), nullable=True, comment='更新者ID')
    version = Column(Integer, default=1, nullable=False, comment='版本号')
    
    def increment_version(self):
        """增加版本号"""
        self.version += 1
        self.updated_at = datetime.now()


class MetadataMixin:
    """元数据混入类"""
    
    metadata_json = Column(Text, nullable=True, comment='元数据JSON')
    
    def set_metadata(self, key: str, value: Any):
        """设置元数据
        
        Args:
            key: 键
            value: 值
        """
        metadata = self.get_metadata()
        metadata[key] = value
        self.metadata_json = json.dumps(metadata, ensure_ascii=False)
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据
        
        Returns:
            元数据字典
        """
        if not self.metadata_json:
            return {}
        
        try:
            return json.loads(self.metadata_json)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """获取元数据值
        
        Args:
            key: 键
            default: 默认值
            
        Returns:
            元数据值
        """
        metadata = self.get_metadata()
        return metadata.get(key, default)
    
    def remove_metadata(self, key: str):
        """移除元数据
        
        Args:
            key: 键
        """
        metadata = self.get_metadata()
        if key in metadata:
            del metadata[key]
            self.metadata_json = json.dumps(metadata, ensure_ascii=False)