# -*- coding: utf-8 -*-
"""
工作单元模式实现

封装数据库会话的生命周期，作为所有服务操作数据库的唯一入口。
实现事务管理和数据一致性保证。
"""

import logging
from typing import Optional, Type, List, Any, Dict
from contextlib import contextmanager, asynccontextmanager
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dal.database import Base


class AbstractUnitOfWork(ABC):
    """工作单元抽象基类"""
    
    @abstractmethod
    def __enter__(self):
        """进入上下文管理器"""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        pass
    
    @abstractmethod
    def commit(self):
        """提交事务"""
        pass
    
    @abstractmethod
    def rollback(self):
        """回滚事务"""
        pass
    
    @abstractmethod
    def add(self, entity: Base):
        """添加实体"""
        pass
    
    @abstractmethod
    def remove(self, entity: Base):
        """删除实体"""
        pass
    
    @abstractmethod
    def get(self, entity_type: Type[Base], entity_id: Any) -> Optional[Base]:
        """根据ID获取实体"""
        pass
    
    @abstractmethod
    def query(self, entity_type: Type[Base]):
        """查询实体"""
        pass


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy工作单元实现"""
    
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker
        self.session: Optional[Session] = None
        self._logger = logging.getLogger(__name__)
        self._is_committed = False
        self._is_rolled_back = False
    
    async def __aenter__(self):
        """异步进入上下文管理器"""
        self.session = self.sessionmaker()
        self._is_committed = False
        self._is_rolled_back = False
        self._logger.debug("开始异步数据库事务")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文管理器"""
        try:
            if exc_type is not None:
                # 发生异常，回滚事务
                self.rollback()
                self._logger.error(f"异步事务回滚，异常: {exc_val}")
            elif not self._is_committed and not self._is_rolled_back:
                # 没有显式提交或回滚，自动提交
                self.commit()
        finally:
            if self.session:
                self.session.close()
                self.session = None
                self._logger.debug("异步数据库会话已关闭")
    
    def __enter__(self):
        """进入上下文管理器"""
        self.session = self.sessionmaker()
        self._is_committed = False
        self._is_rolled_back = False
        self._logger.debug("开始数据库事务")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        try:
            if exc_type is not None:
                # 发生异常，回滚事务
                self.rollback()
                self._logger.error(f"事务回滚，异常: {exc_val}")
            elif not self._is_committed and not self._is_rolled_back:
                # 没有显式提交或回滚，自动提交
                self.commit()
        finally:
            if self.session:
                self.session.close()
                self.session = None
                self._logger.debug("数据库会话已关闭")
    
    def commit(self):
        """提交事务"""
        if self._is_committed or self._is_rolled_back:
            self._logger.warning("尝试重复提交或在回滚后提交")
            return
        
        try:
            self.session.commit()
            self._is_committed = True
            self._logger.debug("事务提交成功")
        except SQLAlchemyError as e:
            self._logger.error(f"事务提交失败: {e}")
            self.rollback()
            raise
    
    def rollback(self):
        """回滚事务"""
        if self._is_rolled_back:
            self._logger.warning("尝试重复回滚")
            return
        
        try:
            self.session.rollback()
            self._is_rolled_back = True
            self._logger.debug("事务回滚成功")
        except SQLAlchemyError as e:
            self._logger.error(f"事务回滚失败: {e}")
            raise
    
    def add(self, entity: Base):
        """添加实体到会话
        
        Args:
            entity: 要添加的实体对象
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        self.session.add(entity)
        self._logger.debug(f"添加实体: {type(entity).__name__}")
    
    def remove(self, entity: Base):
        """从会话中删除实体
        
        Args:
            entity: 要删除的实体对象
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        self.session.delete(entity)
        self._logger.debug(f"删除实体: {type(entity).__name__}")
    
    def get(self, entity_type: Type[Base], entity_id: Any) -> Optional[Base]:
        """根据ID获取实体
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            
        Returns:
            实体对象或None
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        entity = self.session.get(entity_type, entity_id)
        self._logger.debug(f"获取实体: {entity_type.__name__}({entity_id}) -> {'Found' if entity else 'Not Found'}")
        return entity
    
    def query(self, entity_type: Type[Base]):
        """创建查询对象
        
        Args:
            entity_type: 实体类型
            
        Returns:
            SQLAlchemy查询对象
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        return self.session.query(entity_type)
    
    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> Any:
        """执行原始SQL
        
        Args:
            sql: SQL语句
            params: 参数字典
            
        Returns:
            执行结果
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            if params:
                result = self.session.execute(sql, params)
            else:
                result = self.session.execute(sql)
            
            self._logger.debug(f"执行SQL: {sql[:100]}...")
            return result
        except SQLAlchemyError as e:
            self._logger.error(f"SQL执行失败: {e}")
            raise
    
    def flush(self):
        """刷新会话（将更改发送到数据库但不提交）"""
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            self.session.flush()
            self._logger.debug("会话刷新成功")
        except SQLAlchemyError as e:
            self._logger.error(f"会话刷新失败: {e}")
            raise
    
    def refresh(self, entity: Base):
        """刷新实体（从数据库重新加载）
        
        Args:
            entity: 要刷新的实体
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            self.session.refresh(entity)
            self._logger.debug(f"刷新实体: {type(entity).__name__}")
        except SQLAlchemyError as e:
            self._logger.error(f"实体刷新失败: {e}")
            raise
    
    def merge(self, entity: Base) -> Base:
        """合并实体（处理分离状态的实体）
        
        Args:
            entity: 要合并的实体
            
        Returns:
            合并后的实体
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            merged_entity = self.session.merge(entity)
            self._logger.debug(f"合并实体: {type(entity).__name__}")
            return merged_entity
        except SQLAlchemyError as e:
            self._logger.error(f"实体合并失败: {e}")
            raise
    
    def bulk_insert(self, entities: List[Base]):
        """批量插入实体
        
        Args:
            entities: 实体列表
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            self.session.add_all(entities)
            self._logger.debug(f"批量插入 {len(entities)} 个实体")
        except SQLAlchemyError as e:
            self._logger.error(f"批量插入失败: {e}")
            raise
    
    def bulk_update(self, entity_type: Type[Base], values: Dict[str, Any], 
                   where_clause=None) -> int:
        """批量更新实体
        
        Args:
            entity_type: 实体类型
            values: 更新值字典
            where_clause: WHERE条件
            
        Returns:
            受影响的行数
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            query = self.session.query(entity_type)
            if where_clause is not None:
                query = query.filter(where_clause)
            
            count = query.update(values)
            self._logger.debug(f"批量更新 {count} 个 {entity_type.__name__} 实体")
            return count
        except SQLAlchemyError as e:
            self._logger.error(f"批量更新失败: {e}")
            raise
    
    def bulk_delete(self, entity_type: Type[Base], where_clause=None) -> int:
        """批量删除实体
        
        Args:
            entity_type: 实体类型
            where_clause: WHERE条件
            
        Returns:
            受影响的行数
        """
        if not self.session:
            raise RuntimeError("会话未初始化")
        
        try:
            query = self.session.query(entity_type)
            if where_clause is not None:
                query = query.filter(where_clause)
            
            count = query.delete()
            self._logger.debug(f"批量删除 {count} 个 {entity_type.__name__} 实体")
            return count
        except SQLAlchemyError as e:
            self._logger.error(f"批量删除失败: {e}")
            raise
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息
        
        Returns:
            会话信息字典
        """
        if not self.session:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'active',
            'is_committed': self._is_committed,
            'is_rolled_back': self._is_rolled_back,
            'dirty_objects': len(self.session.dirty),
            'new_objects': len(self.session.new),
            'deleted_objects': len(self.session.deleted),
            'identity_map_size': len(self.session.identity_map)
        }


@contextmanager
def unit_of_work(sessionmaker) -> SqlAlchemyUnitOfWork:
    """工作单元上下文管理器
    
    Args:
        sessionmaker: SQLAlchemy会话工厂
        
    Yields:
        工作单元实例
    """
    uow = SqlAlchemyUnitOfWork(sessionmaker)
    with uow:
        yield uow


@asynccontextmanager
async def async_unit_of_work(sessionmaker) -> SqlAlchemyUnitOfWork:
    """异步工作单元上下文管理器
    
    Args:
        sessionmaker: SQLAlchemy会话工厂
        
    Yields:
        工作单元实例
    """
    uow = SqlAlchemyUnitOfWork(sessionmaker)
    try:
        uow.__enter__()
        yield uow
    except Exception as e:
        uow.__exit__(type(e), e, e.__traceback__)
        raise
    else:
        uow.__exit__(None, None, None)


# 为了向后兼容，提供 UnitOfWork 别名
UnitOfWork = SqlAlchemyUnitOfWork