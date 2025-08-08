# -*- coding: utf-8 -*-
"""
命令注册器

自动发现并注册所有命令类。
"""

import os
import importlib
import inspect
import logging
from typing import Dict, List, Type, Optional
from pathlib import Path
from commands.base import Command
from services.app_service import AppService
from services.news_service import NewsService


class CommandRegistry:
    """命令注册器"""
    
    def __init__(self, auth_service=None, app_service=None, news_service=None, stock_service=None):
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}  # alias -> command_name
        self._categories: Dict[str, List[str]] = {}  # category -> [command_names]
        self._logger = logging.getLogger(__name__)
        self._auth_service = auth_service
        self._app_service = app_service
        self._news_service = news_service
        self._stock_service = stock_service
    
    async def discover_commands(self, commands_dir: str = None):
        """自动发现并注册命令
        
        Args:
            commands_dir: 命令目录路径，默认为当前模块的commands目录
        """
        if commands_dir is None:
            # 获取项目根目录下的commands目录
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            commands_dir = project_root / "commands"
        else:
            commands_dir = Path(commands_dir)
        
        if not commands_dir.exists():
            self._logger.error(f"命令目录不存在: {commands_dir}")
            return
        
        self._logger.info(f"开始发现命令: {commands_dir}")
        
        # 递归扫描命令目录
        await self._scan_directory(commands_dir)
        
        self._logger.info(f"命令发现完成，共注册 {len(self._commands)} 个命令")
    
    async def _scan_directory(self, directory: Path, package_prefix: str = "commands"):
        """递归扫描目录中的命令
        
        Args:
            directory: 要扫描的目录
            package_prefix: 包前缀
        """
        for item in directory.iterdir():
            if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                # 扫描Python文件
                await self._scan_module(item, package_prefix)
            elif item.is_dir() and not item.name.startswith('_'):
                # 递归扫描子目录
                sub_package = f"{package_prefix}.{item.name}"
                await self._scan_directory(item, sub_package)
    
    async def _scan_module(self, module_path: Path, package_prefix: str):
        """扫描模块中的命令类
        
        Args:
            module_path: 模块文件路径
            package_prefix: 包前缀
        """
        try:
            # 构建模块名
            module_name = f"{package_prefix}.{module_path.stem}"
            self._logger.debug(f"正在扫描模块: {module_name}")
            
            # 动态导入模块
            module = importlib.import_module(module_name)
            
            # 查找命令类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                try:
                    if (issubclass(obj, Command) and 
                        obj != Command and 
                        not inspect.isabstract(obj)):
                        # 实例化并注册命令
                        try:
                            # 特殊处理需要依赖注入的命令
                            if name == 'SudoCommand' and self._auth_service:
                                command_instance = obj(auth_service=self._auth_service)
                            elif name == 'MarketCommand' and self._app_service:
                                command_instance = obj(app_service=self._app_service)
                            elif name == 'NewsCommand' and self._news_service:
                                command_instance = obj(news_service=self._news_service)
                            elif name == 'JCMarketCommand' and self._stock_service:
                                command_instance = obj(stock_service=self._stock_service)
                            else:
                                command_instance = obj()
                            self.register_command(command_instance)
                            self._logger.debug(f"注册命令: {command_instance.name} (来自 {module_name})")
                        except Exception as e:
                            self._logger.error(f"实例化命令失败 {name}: {e}")
                except TypeError:
                     # 跳过不是类的对象或无法进行issubclass检查的对象
                     continue
        
        except ImportError as e:
            self._logger.warning(f"导入模块失败 {module_path}: {e}")
        except Exception as e:
            self._logger.error(f"扫描模块时发生错误 {module_path}: {e}")
    
    def register_command(self, command: Command):
        """注册单个命令
        
        Args:
            command: 命令实例
        """
        command_name = command.name.lower()
        
        # 检查命令名是否已存在
        if command_name in self._commands:
            self._logger.warning(f"命令名冲突: {command_name}，将覆盖现有命令")
        
        # 注册命令
        self._commands[command_name] = command
        self._logger.debug(f"注册命令: {command_name} (类型: {command.__class__.__name__})")
        
        # 注册别名
        for alias in command.aliases:
            alias_lower = alias.lower()
            if alias_lower in self._aliases:
                self._logger.warning(f"别名冲突: {alias_lower}，将覆盖现有别名")
            self._aliases[alias_lower] = command_name
            self._logger.debug(f"注册别名: {alias_lower} -> {command_name}")
        
        # 注册到分类
        category = command.category
        if category not in self._categories:
            self._categories[category] = []
            self._logger.debug(f"创建新分类: {category}")
        if command_name not in self._categories[category]:
            self._categories[category].append(command_name)
            self._logger.debug(f"添加命令到分类 {category}: {command_name}")
        
        self._logger.debug(f"命令注册成功: {command_name} (分类: {category}, 别名: {command.aliases})")
    
    def unregister_command(self, command_name: str) -> bool:
        """注销命令
        
        Args:
            command_name: 命令名
            
        Returns:
            是否成功注销
        """
        command_name = command_name.lower()
        
        if command_name not in self._commands:
            return False
        
        command = self._commands[command_name]
        
        # 移除命令
        del self._commands[command_name]
        
        # 移除别名
        aliases_to_remove = []
        for alias, target in self._aliases.items():
            if target == command_name:
                aliases_to_remove.append(alias)
        
        for alias in aliases_to_remove:
            del self._aliases[alias]
        
        # 从分类中移除
        category = command.category
        if category in self._categories and command_name in self._categories[category]:
            self._categories[category].remove(command_name)
            if not self._categories[category]:  # 如果分类为空，删除分类
                del self._categories[category]
        
        self._logger.info(f"命令注销成功: {command_name}")
        return True
    
    def get_command(self, command_name: str) -> Optional[Command]:
        """获取命令实例
        
        Args:
            command_name: 命令名或别名
            
        Returns:
            命令实例或None
        """
        command_name = command_name.lower()
        
        # 直接查找命令名
        if command_name in self._commands:
            return self._commands[command_name]
        
        # 查找别名
        if command_name in self._aliases:
            actual_command_name = self._aliases[command_name]
            return self._commands.get(actual_command_name)
        
        return None
    
    def list_commands(self, category: str = None) -> List[Command]:
        """列出命令
        
        Args:
            category: 命令分类，None表示所有命令
            
        Returns:
            命令列表
        """
        if category is None:
            return list(self._commands.values())
        
        if category not in self._categories:
            return []
        
        return [self._commands[name] for name in self._categories[category]]
    
    def get_command_names(self, category: str = None) -> List[str]:
        """获取命令名列表
        
        Args:
            category: 命令分类，None表示所有命令
            
        Returns:
            命令名列表
        """
        if category is None:
            return list(self._commands.keys())
        
        return self._categories.get(category, [])
    
    def get_categories(self) -> List[str]:
        """获取所有命令分类
        
        Returns:
            分类列表
        """
        return list(self._categories.keys())
    
    def search_commands(self, keyword: str) -> List[Command]:
        """搜索命令
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的命令列表
        """
        keyword = keyword.lower()
        results = []
        
        for command in self._commands.values():
            # 搜索命令名
            if keyword in command.name.lower():
                results.append(command)
                continue
            
            # 搜索别名
            if any(keyword in alias.lower() for alias in command.aliases):
                results.append(command)
                continue
            
            # 搜索描述
            if keyword in command.description.lower():
                results.append(command)
                continue
        
        return results
    
    def get_command_help(self, command_name: str = None) -> str:
        """获取命令帮助信息
        
        Args:
            command_name: 命令名，None表示获取所有命令的帮助
            
        Returns:
            帮助信息字符串
        """
        if command_name:
            command = self.get_command(command_name)
            if command:
                return command.get_help()
            else:
                return f"未找到命令: {command_name}"
        
        # 生成所有命令的帮助信息
        help_text = "# 可用命令\n\n"
        
        for category in sorted(self._categories.keys()):
            help_text += f"## {category.title()}\n\n"
            
            commands_in_category = [self._commands[name] for name in self._categories[category]]
            commands_in_category.sort(key=lambda c: c.name)
            
            for command in commands_in_category:
                help_text += f"- **{command.name}**: {command.description}\n"
                if command.aliases:
                    help_text += f"  别名: {', '.join(command.aliases)}\n"
            
            help_text += "\n"
        
        return help_text
    
    def get_stats(self) -> Dict[str, any]:
        """获取注册器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_commands': len(self._commands),
            'total_aliases': len(self._aliases),
            'categories': len(self._categories),
            'commands_by_category': {cat: len(commands) for cat, commands in self._categories.items()}
        }
    
    def validate_registry(self) -> List[str]:
        """验证注册器状态
        
        Returns:
            问题列表，空列表表示无问题
        """
        issues = []
        
        # 检查命令名冲突
        command_names = set()
        for command in self._commands.values():
            if command.name.lower() in command_names:
                issues.append(f"命令名重复: {command.name}")
            command_names.add(command.name.lower())
        
        # 检查别名冲突
        all_names = set(self._commands.keys())
        for alias, target in self._aliases.items():
            if alias in all_names:
                issues.append(f"别名与命令名冲突: {alias}")
            if target not in self._commands:
                issues.append(f"别名指向不存在的命令: {alias} -> {target}")
        
        # 检查分类一致性
        for category, command_names in self._categories.items():
            for command_name in command_names:
                if command_name not in self._commands:
                    issues.append(f"分类中包含不存在的命令: {category} -> {command_name}")
                elif self._commands[command_name].category != category:
                    issues.append(f"命令分类不一致: {command_name}")
        
        return issues