# -*- coding: utf-8 -*-
"""
服务管理器

统一管理所有游戏服务，提供依赖注入和服务生命周期管理。
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Type, List
from dataclasses import dataclass
from enum import Enum

from config.settings import Settings
from core.event_bus import EventBus
from dal.database import DatabaseEngine
from dal.unit_of_work import SqlAlchemyUnitOfWork
from services.auth_service import AuthService
from services.time_service import TimeService
from services.currency_service import CurrencyService
from services.stock_service import StockService
from services.news_service import NewsService
from services.app_service import AppService
from services.bank_service import BankService
from services.bank_task_service import BankTaskService
from services.credit_service import CreditService
from services.command_dispatcher import CommandDispatcher
from commands.registry import CommandRegistry
from core.game_time import GameTime


class ServiceState(Enum):
    """服务状态枚举"""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    instance: Any
    state: ServiceState
    dependencies: List[str]
    error: Optional[str] = None
    
    def __str__(self):
        return f"{self.name}({self.state.value})"


class ServiceManager:
    """服务管理器
    
    负责统一管理所有游戏服务的初始化、启动和停止。
    提供依赖注入和服务生命周期管理。
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # 核心组件
        self.event_bus: Optional[EventBus] = None
        self.db_engine: Optional[DatabaseEngine] = None
        self.uow: Optional[SqlAlchemyUnitOfWork] = None
        
        # 服务注册表
        self._services: Dict[str, ServiceInfo] = {}
        self._service_order: List[str] = []  # 服务初始化顺序
        
        # 服务状态
        self._is_initialized = False
        self._is_running = False
        
        # 统计信息
        self._stats = {
            'initialization_time': 0,
            'services_count': 0,
            'failed_services': 0,
            'start_time': None
        }
    
    def register_service(self, name: str, service_class: Type, dependencies: List[str] = None):
        """注册服务
        
        Args:
            name: 服务名称
            service_class: 服务类
            dependencies: 依赖的服务名称列表
        """
        if name in self._services:
            self.logger.warning(f"服务 {name} 已存在，将被覆盖")
        
        self._services[name] = ServiceInfo(
            name=name,
            instance=None,
            state=ServiceState.NOT_INITIALIZED,
            dependencies=dependencies or []
        )
        
        self.logger.debug(f"已注册服务: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """获取服务实例
        
        Args:
            name: 服务名称
            
        Returns:
            服务实例，如果不存在或未初始化则返回None
        """
        service_info = self._services.get(name)
        if service_info and service_info.state in [ServiceState.INITIALIZED, ServiceState.RUNNING]:
            return service_info.instance
        return None
    
    def get_service_state(self, name: str) -> Optional[ServiceState]:
        """获取服务状态
        
        Args:
            name: 服务名称
            
        Returns:
            服务状态，如果服务不存在则返回None
        """
        service_info = self._services.get(name)
        return service_info.state if service_info else None
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """获取所有服务信息
        
        Returns:
            所有服务的信息字典
        """
        return self._services.copy()
    
    def _register_core_services(self):
        """注册核心服务"""
        # 注册基础服务
        self.register_service("event_bus", EventBus, [])
        self.register_service("db_engine", DatabaseEngine, [])
        self.register_service("uow", SqlAlchemyUnitOfWork, ["db_engine"])
        
        # 注册时间服务（需要先初始化，因为其他服务依赖它）
        self.register_service("time_service", TimeService, ["event_bus"])
        
        # 注册业务服务
        self.register_service("auth_service", AuthService, ["uow", "event_bus"])
        self.register_service("currency_service", CurrencyService, ["uow", "event_bus"])
        self.register_service("stock_service", StockService, ["uow", "event_bus", "currency_service", "time_service"])
        self.register_service("news_service", NewsService, ["event_bus", "time_service"])
        self.register_service("app_service", AppService, ["uow", "event_bus", "currency_service"])
        self.register_service("bank_service", BankService, ["uow", "event_bus"])
        self.register_service("bank_task_service", BankTaskService, ["uow"])
        self.register_service("credit_service", CreditService, ["uow"])
        
        # 注册命令系统
        self.register_service("command_registry", CommandRegistry, [
            "auth_service", "app_service", "news_service", "stock_service", "time_service"
        ])
        self.register_service("command_dispatcher", CommandDispatcher, [
            "command_registry", "auth_service", "event_bus"
        ])
    
    def _resolve_dependencies(self) -> List[str]:
        """解析服务依赖关系，返回初始化顺序
        
        Returns:
            按依赖关系排序的服务名称列表
        """
        # 拓扑排序算法
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(name: str):
            if name in temp_visited:
                raise ValueError(f"发现循环依赖: {name}")
            if name in visited:
                return
            
            temp_visited.add(name)
            
            service_info = self._services[name]
            for dep in service_info.dependencies:
                if dep not in self._services:
                    raise ValueError(f"服务 {name} 依赖的服务 {dep} 不存在")
                visit(dep)
            
            temp_visited.remove(name)
            visited.add(name)
            result.append(name)
        
        # 访问所有服务
        for name in self._services:
            if name not in visited:
                visit(name)
        
        return result
    
    async def initialize(self):
        """初始化所有服务"""
        if self._is_initialized:
            self.logger.warning("服务管理器已经初始化")
            return
        
        import time
        start_time = time.time()
        
        try:
            self.logger.info("开始初始化服务管理器")
            
            # 注册核心服务
            self._register_core_services()
            
            # 解析依赖关系
            self._service_order = self._resolve_dependencies()
            self.logger.info(f"服务初始化顺序: {' -> '.join(self._service_order)}")
            
            # 按顺序初始化服务
            for service_name in self._service_order:
                await self._initialize_service(service_name)
            
            # 设置全局组件
            self._setup_global_components()
            
            self._is_initialized = True
            self._stats['initialization_time'] = time.time() - start_time
            self._stats['services_count'] = len(self._services)
            self._stats['failed_services'] = sum(1 for s in self._services.values() if s.state == ServiceState.ERROR)
            
            self.logger.info(f"服务管理器初始化完成，耗时: {self._stats['initialization_time']:.2f}秒")
            self.logger.info(f"成功初始化 {self._stats['services_count'] - self._stats['failed_services']}/{self._stats['services_count']} 个服务")
            
            if self._stats['failed_services'] > 0:
                failed_services = [name for name, info in self._services.items() if info.state == ServiceState.ERROR]
                self.logger.warning(f"以下服务初始化失败: {', '.join(failed_services)}")
            
        except Exception as e:
            self.logger.error(f"服务管理器初始化失败: {e}", exc_info=True)
            raise
    
    async def _initialize_service(self, name: str):
        """初始化单个服务
        
        Args:
            name: 服务名称
        """
        service_info = self._services[name]
        
        if service_info.state != ServiceState.NOT_INITIALIZED:
            self.logger.debug(f"服务 {name} 已经初始化，状态: {service_info.state}")
            return
        
        self.logger.info(f"正在初始化服务: {name}")
        service_info.state = ServiceState.INITIALIZING
        
        try:
            # 获取依赖的服务实例
            dependencies = {}
            for dep_name in service_info.dependencies:
                dep_service = self.get_service(dep_name)
                if dep_service is None:
                    raise ValueError(f"依赖服务 {dep_name} 未初始化")
                dependencies[dep_name] = dep_service
            
            # 根据服务类型进行特殊处理
            if name == "event_bus":
                service_info.instance = EventBus()
            elif name == "db_engine":
                service_info.instance = DatabaseEngine(self.settings)
                await service_info.instance.initialize()
            elif name == "uow":
                service_info.instance = SqlAlchemyUnitOfWork(dependencies["db_engine"].sessionmaker)
            elif name == "time_service":
                service_info.instance = TimeService(dependencies["event_bus"], tick_interval=1)
            elif name == "auth_service":
                service_info.instance = AuthService(dependencies["uow"], dependencies["event_bus"])
            elif name == "currency_service":
                service_info.instance = CurrencyService(dependencies["uow"], dependencies["event_bus"])
            elif name == "stock_service":
                service_info.instance = StockService(
                    dependencies["uow"], dependencies["event_bus"], 
                    dependencies["currency_service"], dependencies["time_service"]
                )
            elif name == "news_service":
                service_info.instance = NewsService(dependencies["event_bus"], dependencies["time_service"])
            elif name == "app_service":
                service_info.instance = AppService(
                    dependencies["uow"], dependencies["event_bus"], dependencies["currency_service"]
                )
            elif name == "bank_service":
                service_info.instance = BankService(dependencies["uow"], dependencies["event_bus"])
            elif name == "bank_task_service":
                service_info.instance = BankTaskService(dependencies["uow"])
            elif name == "credit_service":
                service_info.instance = CreditService(dependencies["uow"])
            elif name == "command_registry":
                service_info.instance = CommandRegistry(
                    auth_service=dependencies["auth_service"],
                    app_service=dependencies["app_service"],
                    news_service=dependencies["news_service"],
                    stock_service=dependencies["stock_service"],
                    time_service=dependencies["time_service"]
                )
                await service_info.instance.discover_commands()
            elif name == "command_dispatcher":
                service_info.instance = CommandDispatcher(
                    dependencies["command_registry"], dependencies["auth_service"], 
                    dependencies["event_bus"]
                )
            else:
                raise ValueError(f"未知的服务类型: {name}")
            
            service_info.state = ServiceState.INITIALIZED
            self.logger.info(f"服务 {name} 初始化完成")
            
        except Exception as e:
            service_info.state = ServiceState.ERROR
            service_info.error = str(e)
            self.logger.error(f"服务 {name} 初始化失败: {e}", exc_info=True)
            raise
    
    def _setup_global_components(self):
        """设置全局组件"""
        # 设置全局数据库引擎
        from dal.database import set_global_engine
        db_engine = self.get_service("db_engine")
        if db_engine:
            set_global_engine(db_engine)
        
        # 设置GameTime的时间服务
        time_service = self.get_service("time_service")
        if time_service:
            GameTime.set_time_service(time_service)
    
    async def start_services(self):
        """启动所有需要启动的服务"""
        if not self._is_initialized:
            raise RuntimeError("服务管理器未初始化")
        
        if self._is_running:
            self.logger.warning("服务已经在运行")
            return
        
        self.logger.info("开始启动服务")
        self._stats['start_time'] = GameTime.now() if GameTime.is_initialized() else None
        
        # 启动时间服务（需要先启动）
        time_service = self.get_service("time_service")
        if time_service:
            try:
                time_service.start()
                self._services["time_service"].state = ServiceState.RUNNING
                self.logger.info("时间服务已启动")
            except Exception as e:
                self.logger.error(f"时间服务启动失败: {e}", exc_info=True)
                self._services["time_service"].state = ServiceState.ERROR
        
        # 初始化股票数据
        stock_service = self.get_service("stock_service")
        if stock_service:
            try:
                await stock_service.initialize_stocks()
                self.logger.info("股票数据初始化完成")
            except Exception as e:
                self.logger.error(f"股票数据初始化失败: {e}", exc_info=True)
        
        self._is_running = True
        self.logger.info("服务启动完成")
    
    async def stop_services(self):
        """停止所有服务"""
        if not self._is_running:
            self.logger.warning("服务未在运行")
            return
        
        self.logger.info("开始停止服务")
        
        # 按相反顺序停止服务
        for service_name in reversed(self._service_order):
            service_info = self._services[service_name]
            if service_info.state == ServiceState.RUNNING:
                await self._stop_service(service_name)
        
        self._is_running = False
        self.logger.info("服务停止完成")
    
    async def _stop_service(self, name: str):
        """停止单个服务
        
        Args:
            name: 服务名称
        """
        service_info = self._services[name]
        
        if service_info.state != ServiceState.RUNNING:
            return
        
        self.logger.info(f"正在停止服务: {name}")
        service_info.state = ServiceState.STOPPING
        
        try:
            # 根据服务类型进行特殊处理
            if name == "time_service":
                service_info.instance.stop()
            elif name == "db_engine":
                await service_info.instance.close()
            
            service_info.state = ServiceState.STOPPED
            self.logger.info(f"服务 {name} 已停止")
            
        except Exception as e:
            service_info.state = ServiceState.ERROR
            service_info.error = str(e)
            self.logger.error(f"服务 {name} 停止失败: {e}", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息字典
        """
        return self._stats.copy()
    
    def get_service_status(self) -> Dict[str, str]:
        """获取服务状态
        
        Returns:
            服务状态字典
        """
        return {name: info.state.value for name, info in self._services.items()}
    
    def is_initialized(self) -> bool:
        """检查是否已初始化
        
        Returns:
            是否已初始化
        """
        return self._is_initialized
    
    def is_running(self) -> bool:
        """检查是否在运行
        
        Returns:
            是否在运行
        """
        return self._is_running
    
    def __str__(self):
        return f"ServiceManager(services={len(self._services)}, initialized={self._is_initialized}, running={self._is_running})"