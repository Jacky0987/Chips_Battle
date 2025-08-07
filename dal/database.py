# -*- coding: utf-8 -*-
"""
数据库引擎

初始化SQLAlchemy引擎和会话工厂，管理数据库连接。
"""

import logging
from typing import Optional
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import Settings


# 创建基础模型类
Base = declarative_base()

# 元数据对象
metadata = MetaData()


class DatabaseEngine:
    """数据库引擎管理器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = None
        self.sessionmaker = None
        self._logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """初始化数据库引擎"""
        try:
            # 创建数据库引擎
            self.engine = create_engine(
                self.settings.get_database_url(),
                echo=self.settings.DATABASE_ECHO,
                # SQLite特定配置
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,  # 允许多线程访问
                    "timeout": 20  # 连接超时
                } if "sqlite" in self.settings.get_database_url() else {},
                # 连接池配置
                pool_pre_ping=True,  # 连接前检查
                pool_recycle=3600,   # 1小时回收连接
            )
            
            # 配置SQLite特定设置
            if "sqlite" in self.settings.get_database_url():
                self._configure_sqlite()
            
            # 创建会话工厂
            self.sessionmaker = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # 创建所有表
            await self._create_tables()
            
            self._logger.info(f"数据库引擎初始化成功: {self.settings.get_database_url()}")
            
        except Exception as e:
            self._logger.error(f"数据库引擎初始化失败: {e}")
            raise
    
    def _configure_sqlite(self):
        """配置SQLite特定设置"""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """设置SQLite编译指示"""
            cursor = dbapi_connection.cursor()
            
            # 启用外键约束
            cursor.execute("PRAGMA foreign_keys=ON")
            
            # 设置WAL模式以提高并发性能
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # 设置同步模式
            cursor.execute("PRAGMA synchronous=NORMAL")
            
            # 设置缓存大小 (负数表示KB)
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB
            
            # 设置临时存储
            cursor.execute("PRAGMA temp_store=MEMORY")
            
            # 设置mmap大小
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            cursor.close()
    
    async def _create_tables(self):
        """创建所有数据库表"""
        try:
            # 导入所有模型以确保它们被注册
            self._import_all_models()
            
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            
            self._logger.info("数据库表创建完成")
            
        except Exception as e:
            self._logger.error(f"创建数据库表失败: {e}")
            raise
    
    def _import_all_models(self):
        """导入所有模型类"""
        try:
            # 导入所有模型模块
            from models.auth.user import User
            from models.auth.role import Role
            from models.auth.permission import Permission
            from models.finance.currency import Currency
            from models.finance.account import Account
            from models.apps.app import App
            from models.apps.ownership import UserAppOwnership
            from models.stock.stock import Stock
            from models.stock.stock_price import StockPrice
            from models.stock.portfolio import Portfolio, PortfolioItem
            from models.news.news import News
            
            self._logger.debug("所有模型类导入完成")
            
        except ImportError as e:
            self._logger.warning(f"导入模型类时出现警告: {e}")
            # 在开发阶段，某些模型可能还未创建，这是正常的
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.sessionmaker:
            raise RuntimeError("数据库引擎未初始化")
        return self.sessionmaker()
    
    async def close(self):
        """关闭数据库引擎"""
        if self.engine:
            self.engine.dispose()
            self._logger.info("数据库引擎已关闭")
    
    def execute_raw_sql(self, sql: str, params: dict = None):
        """执行原始SQL语句
        
        Args:
            sql: SQL语句
            params: 参数字典
            
        Returns:
            执行结果
        """
        with self.get_session() as session:
            try:
                if params:
                    result = session.execute(sql, params)
                else:
                    result = session.execute(sql)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                self._logger.error(f"执行SQL失败: {e}")
                raise
    
    def get_table_info(self, table_name: str) -> dict:
        """获取表信息
        
        Args:
            table_name: 表名
            
        Returns:
            表信息字典
        """
        try:
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            
            return {
                'columns': inspector.get_columns(table_name),
                'primary_keys': inspector.get_pk_constraint(table_name),
                'foreign_keys': inspector.get_foreign_keys(table_name),
                'indexes': inspector.get_indexes(table_name)
            }
        except Exception as e:
            self._logger.error(f"获取表信息失败: {e}")
            return {}
    
    def get_database_stats(self) -> dict:
        """获取数据库统计信息"""
        try:
            stats = {
                'engine_url': str(self.engine.url),
                'pool_size': self.engine.pool.size(),
                'checked_in': self.engine.pool.checkedin(),
                'checked_out': self.engine.pool.checkedout(),
                'overflow': self.engine.pool.overflow(),
                'invalid': self.engine.pool.invalid()
            }
            
            # 如果是SQLite，获取额外信息
            if "sqlite" in str(self.engine.url):
                with self.get_session() as session:
                    # 获取数据库大小
                    result = session.execute("PRAGMA page_count")
                    page_count = result.scalar()
                    
                    result = session.execute("PRAGMA page_size")
                    page_size = result.scalar()
                    
                    stats['database_size_bytes'] = page_count * page_size
                    stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            self._logger.error(f"获取数据库统计信息失败: {e}")
            return {}


# 全局数据库引擎实例
_global_engine: Optional[DatabaseEngine] = None


def set_global_engine(engine: DatabaseEngine):
    """设置全局数据库引擎实例
    
    Args:
        engine: 数据库引擎实例
    """
    global _global_engine
    _global_engine = engine


def get_session() -> Session:
    """获取数据库会话
    
    Returns:
        数据库会话对象
        
    Raises:
        RuntimeError: 如果全局引擎未初始化
    """
    if _global_engine is None:
        raise RuntimeError("全局数据库引擎未初始化，请先调用 set_global_engine()")
    return _global_engine.get_session()