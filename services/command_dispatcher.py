# -*- coding: utf-8 -*-
"""
命令分发器

负责解析用户输入并分发给相应的命令对象执行。
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from commands.registry import CommandRegistry
from commands.base import Command, CommandResult, CommandContext, CommandParser
from services.auth_service import AuthService
from core.event_bus import EventBus, UserActionEvent
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class CommandDispatcher:
    """命令分发器"""
    
    def __init__(self, 
                 command_registry: CommandRegistry,
                 auth_service: AuthService,
                 event_bus: EventBus,
                 console: Console = None):
        self.command_registry = command_registry
        self.auth_service = auth_service
        self.event_bus = event_bus
        self.console = console or Console()
        self._logger = logging.getLogger(__name__)
        
        # 会话状态
        self._session_data: Dict[str, Dict[str, Any]] = {}  # user_id -> session_data
        self._command_history: Dict[str, List[str]] = {}  # user_id -> command_history
        
        # 统计信息
        self._stats = {
            'commands_executed': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'unauthorized_attempts': 0,
            'start_time': datetime.now()
        }
    
    async def dispatch(self, command_input: str, user: Any) -> Optional[CommandResult]:
        """分发命令
        
        Args:
            command_input: 用户输入的命令字符串
            user: 用户对象
            
        Returns:
            命令执行结果
        """
        if not command_input.strip():
            return None
        
        # 记录命令历史
        self._add_to_history(user.user_id, command_input)
        
        # 解析命令
        command_name, args = CommandParser.parse(command_input)
        
        if not command_name:
            return CommandResult(success=False, message="请输入有效的命令")
        
        # 查找命令
        command = self.command_registry.get_command(command_name)
        if not command:
            result = await self._handle_unknown_command(command_name, args, user)
            self._display_result(result)
            return result
        
        # 创建命令上下文
        context = CommandContext(
            user=user,
            session_data=self._get_session_data(user.user_id),
            game_time=datetime.now(),  # 这里应该从时间服务获取游戏时间
            registry=self.command_registry
        )
        
        # 执行命令
        try:
            result = await self._execute_command(command, args, context)
            
            # 发布用户行为事件
            await self._publish_user_action_event(user, command_name, args, result)
            
            # 更新统计信息
            self._update_stats(result.success)
            
            # 显示结果
            self._display_result(result)
            
            return result
            
        except Exception as e:
            self._logger.error(f"命令执行异常: {e}", exc_info=True)
            error_result = CommandResult(
                success=False, 
                message=f"命令执行时发生错误: {str(e)}"
            )
            self._update_stats(False)
            self._display_result(error_result)
            return error_result
    
    async def _execute_command(self, command: Command, args: List[str], context: CommandContext) -> CommandResult:
        """执行命令
        
        Args:
            command: 命令对象
            args: 命令参数
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        # 权限检查
        if not await self._check_permissions(command, context.user):
            self._stats['unauthorized_attempts'] += 1
            return CommandResult(
                success=False,
                message=f"权限不足，无法执行命令 '{command.name}'"
            )
        
        # 参数验证
        if not command.validate_args(args):
            return CommandResult(
                success=False,
                message=f"参数无效。用法: {command.usage}"
            )
        
        # 执行命令
        self._logger.info(f"执行命令: {command.name} (用户: {context.user.username})")
        
        start_time = datetime.now()
        result = await command.execute(args, context)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 记录执行时间
        if execution_time > 1.0:  # 如果执行时间超过1秒，记录警告
            self._logger.warning(f"命令执行耗时过长: {command.name} ({execution_time:.2f}秒)")
        
        # 更新用户统计信息
        if result.success:
            await self._update_user_stats(context.user, command.name)
        
        return result
    
    async def _check_permissions(self, command: Command, user: Any) -> bool:
        """检查命令权限
        
        Args:
            command: 命令对象
            user: 用户对象
            
        Returns:
            是否有权限执行
        """
        # 检查是否为管理员专用命令
        if command.is_admin_only:
            return await self.auth_service.has_role(user, "admin")
        
        # 检查特定权限
        for permission in command.required_permissions:
            if not await self.auth_service.has_permission(user, permission):
                return False
        
        return True
    
    async def _update_user_stats(self, user: Any, command_name: str) -> None:
        """更新用户统计信息
        
        Args:
            user: 用户对象
            command_name: 执行的命令名
        """
        try:
            from dal.database import get_session
            from sqlalchemy import update
            from models.auth.user import User
            
            # 更新命令执行次数
            user.command_count = getattr(user, 'command_count', 0) + 1
            
            # 根据命令类型增加经验值
            experience_gain = self._calculate_experience_gain(command_name)
            user.experience = getattr(user, 'experience', 0) + experience_gain
            
            # 检查是否升级
            new_level = self._calculate_level(user.experience)
            if new_level > user.level:
                user.level = new_level
                self._logger.info(f"用户 {user.username} 升级到 {new_level} 级!")
            
            # 更新数据库
            async with get_session() as session:
                await session.execute(
                    update(User)
                    .where(User.user_id == user.user_id)
                    .values(
                        command_count=user.command_count,
                        experience=user.experience,
                        level=user.level
                    )
                )
                await session.commit()
                
        except Exception as e:
            self._logger.error(f"更新用户统计信息失败: {e}", exc_info=True)
    
    def _calculate_experience_gain(self, command_name: str) -> int:
        """计算命令执行获得的经验值
        
        Args:
            command_name: 命令名
            
        Returns:
            经验值增量
        """
        # 不同类型的命令给予不同的经验值
        experience_map = {
            'help': 1,
            'status': 1,
            'profile': 1,
            'bank': 5,
            'transfer': 10,
            'loan': 15,
            'stock': 20,
            'jcmarket': 20,
            'market': 10,
            'calc': 3,
            'news': 5,
            'weather': 2,
            'sudo': 25,  # 管理员命令给予更多经验
        }
        
        return experience_map.get(command_name, 2)  # 默认给予2点经验
    
    def _calculate_level(self, experience: int) -> int:
        """根据经验值计算等级
        
        Args:
            experience: 总经验值
            
        Returns:
            用户等级
        """
        # 简单的等级计算：每1000经验升1级
        return max(1, experience // 1000 + 1)
    
    async def _handle_unknown_command(self, command_name: str, args: List[str], user: Any) -> CommandResult:
        """处理未知命令
        
        Args:
            command_name: 命令名
            args: 参数
            user: 用户对象
            
        Returns:
            命令结果
        """
        # 尝试模糊匹配
        suggestions = self._find_similar_commands(command_name)
        
        message = f"未知命令: '{command_name}'"
        
        if suggestions:
            message += f"\n\n你是否想要执行以下命令之一？\n"
            for suggestion in suggestions[:3]:  # 最多显示3个建议
                message += f"  - {suggestion.name}: {suggestion.description}\n"
        
        message += "\n输入 'help' 查看所有可用命令。"
        
        return CommandResult(success=False, message=message)
    
    def _find_similar_commands(self, command_name: str) -> List[Command]:
        """查找相似的命令
        
        Args:
            command_name: 命令名
            
        Returns:
            相似命令列表
        """
        # 简单的字符串相似度匹配
        similar_commands = []
        
        for command in self.command_registry.list_commands():
            # 检查命令名相似度
            if self._calculate_similarity(command_name, command.name) > 0.6:
                similar_commands.append(command)
                continue
            
            # 检查别名相似度
            for alias in command.aliases:
                if self._calculate_similarity(command_name, alias) > 0.6:
                    similar_commands.append(command)
                    break
        
        # 按相似度排序
        similar_commands.sort(
            key=lambda c: max(
                self._calculate_similarity(command_name, c.name),
                max([self._calculate_similarity(command_name, alias) for alias in c.aliases] or [0])
            ),
            reverse=True
        )
        
        return similar_commands
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度（简单的编辑距离）
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            相似度 (0.0 - 1.0)
        """
        if not str1 or not str2:
            return 0.0
        
        # 转换为小写
        str1, str2 = str1.lower(), str2.lower()
        
        # 如果完全匹配
        if str1 == str2:
            return 1.0
        
        # 如果一个字符串包含另一个
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # 简单的编辑距离计算
        len1, len2 = len(str1), len(str2)
        if len1 > len2:
            str1, str2 = str2, str1
            len1, len2 = len2, len1
        
        distances = list(range(len1 + 1))
        
        for i2, char2 in enumerate(str2):
            new_distances = [i2 + 1]
            for i1, char1 in enumerate(str1):
                if char1 == char2:
                    new_distances.append(distances[i1])
                else:
                    new_distances.append(1 + min(distances[i1], distances[i1 + 1], new_distances[-1]))
            distances = new_distances
        
        edit_distance = distances[-1]
        max_len = max(len(str1), len(str2))
        
        return 1.0 - (edit_distance / max_len)
    
    async def _publish_user_action_event(self, user: Any, command_name: str, args: List[str], result: CommandResult):
        """发布用户行为事件
        
        Args:
            user: 用户对象
            command_name: 命令名
            args: 参数
            result: 执行结果
        """
        try:
            event = UserActionEvent(
                timestamp=datetime.now(),
                event_id=f"user_action_{user.user_id}_{datetime.now().timestamp()}",
                source="command_dispatcher",
                user_id=user.user_id,
                action=command_name,
                details={
                    'args': args,
                    'success': result.success,
                    'message': result.message,
                    'data': result.data
                }
            )
            
            await self.event_bus.publish(event)
            
        except Exception as e:
            self._logger.error(f"发布用户行为事件失败: {e}")
    
    def _display_result(self, result: CommandResult):
        """显示命令执行结果
        
        Args:
            result: 命令执行结果
        """
        if not result.message:
            return
        
        # 根据结果类型选择显示样式
        if result.success:
            if result.message.startswith('✅'):
                self.console.print(result.message, style="green")
            else:
                self.console.print(result.message)
        else:
            if result.message.startswith('❌'):
                self.console.print(result.message, style="red")
            else:
                self.console.print(f"❌ {result.message}", style="red")
    
    def _get_session_data(self, user_id: str) -> Dict[str, Any]:
        """获取用户会话数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话数据字典
        """
        if user_id not in self._session_data:
            self._session_data[user_id] = {}
        return self._session_data[user_id]
    
    def _add_to_history(self, user_id: str, command: str):
        """添加命令到历史记录
        
        Args:
            user_id: 用户ID
            command: 命令字符串
        """
        if user_id not in self._command_history:
            self._command_history[user_id] = []
        
        self._command_history[user_id].append(command)
        
        # 限制历史记录大小
        max_history = 100
        if len(self._command_history[user_id]) > max_history:
            self._command_history[user_id] = self._command_history[user_id][-max_history:]
    
    def _update_stats(self, success: bool):
        """更新统计信息
        
        Args:
            success: 命令是否执行成功
        """
        self._stats['commands_executed'] += 1
        if success:
            self._stats['successful_commands'] += 1
        else:
            self._stats['failed_commands'] += 1
    
    def get_command_history(self, user_id: str, limit: int = 10) -> List[str]:
        """获取用户命令历史
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            命令历史列表
        """
        history = self._command_history.get(user_id, [])
        return history[-limit:] if limit else history
    
    def clear_session_data(self, user_id: str):
        """清空用户会话数据
        
        Args:
            user_id: 用户ID
        """
        if user_id in self._session_data:
            del self._session_data[user_id]
        if user_id in self._command_history:
            del self._command_history[user_id]
        
        self._logger.info(f"已清空用户会话数据: {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取分发器统计信息
        
        Returns:
            统计信息字典
        """
        uptime = (datetime.now() - self._stats['start_time']).total_seconds()
        
        return {
            **self._stats,
            'uptime_seconds': uptime,
            'active_sessions': len(self._session_data),
            'total_users_with_history': len(self._command_history),
            'success_rate': (
                self._stats['successful_commands'] / max(self._stats['commands_executed'], 1)
            ) * 100
        }
    
    def display_help(self, category: str = None):
        """显示帮助信息
        
        Args:
            category: 命令分类，None表示显示所有
        """
        if category:
            commands = self.command_registry.list_commands(category)
            if not commands:
                self.console.print(f"未找到分类 '{category}' 的命令", style="yellow")
                return
            
            title = f"{category.title()} 命令"
        else:
            commands = self.command_registry.list_commands()
            title = "所有可用命令"
        
        # 按分类组织命令
        commands_by_category = {}
        for command in commands:
            cat = command.category
            if cat not in commands_by_category:
                commands_by_category[cat] = []
            commands_by_category[cat].append(command)
        
        # 创建帮助表格
        for cat, cat_commands in sorted(commands_by_category.items()):
            table = Table(title=f"{cat.title()} 命令")
            table.add_column("命令", style="cyan", no_wrap=True)
            table.add_column("描述", style="white")
            table.add_column("别名", style="dim")
            
            for command in sorted(cat_commands, key=lambda c: c.name):
                aliases = ", ".join(command.aliases) if command.aliases else "-"
                table.add_row(command.name, command.description, aliases)
            
            self.console.print(table)
            self.console.print()  # 空行
        
        # 显示使用提示
        tip_panel = Panel(
            "💡 使用 'help <命令名>' 查看特定命令的详细帮助\n"
            "💡 使用 'help <分类>' 查看特定分类的命令",
            title="提示",
            border_style="blue"
        )
        self.console.print(tip_panel)