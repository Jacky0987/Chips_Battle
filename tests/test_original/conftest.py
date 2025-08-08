# -*- coding: utf-8 -*-
"""
Pytest配置文件

提供测试的通用配置和fixture。
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any
from datetime import datetime

from commands.base import CommandContext
from commands.registry import CommandRegistry
from dal.database import DatabaseEngine
# UserManager is not implemented yet, we'll mock it


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_database():
    """模拟数据库引擎"""
    db = Mock(spec=DatabaseEngine)
    db.get_session = Mock()
    db.execute_raw_sql = AsyncMock()
    db.update_user = AsyncMock(return_value=True)
    db.get_user = AsyncMock()  # 添加缺失的get_user方法
    db.get_all_users = AsyncMock(return_value=[])  # 添加缺失的get_all_users方法
    db.create_user = AsyncMock(return_value=True)  # 添加缺失的create_user方法
    db.delete_user = AsyncMock(return_value=True)  # 添加缺失的delete_user方法
    return db


@pytest.fixture
def mock_user_manager():
    """模拟用户管理器"""
    user_manager = Mock()
    user_manager.get_current_user = AsyncMock()
    user_manager.authenticate = AsyncMock()
    user_manager.has_permission = AsyncMock(return_value=True)
    user_manager.is_admin = AsyncMock(return_value=False)
    return user_manager


@pytest.fixture
def mock_registry():
    """模拟命令注册表"""
    registry = Mock(spec=CommandRegistry)
    registry.get_command = Mock()
    registry.list_commands = Mock(return_value={})
    registry.get_categories = Mock(return_value=["basic", "admin", "finance", "apps"])
    registry.search_commands = Mock(return_value=[])
    return registry


@pytest.fixture
def mock_context(mock_database, mock_user_manager, mock_registry):
    """创建模拟命令上下文"""
    context = Mock(spec=CommandContext)
    context.database = mock_database
    context.user_manager = mock_user_manager
    context.registry = mock_registry
    context.registry.get_categories.return_value = ["basic", "finance", "admin", "apps"]
    context.registry.get_command_names.return_value = ["help", "status", "profile", "quit"]
    
    # 创建一个mock命令对象
    mock_command = Mock()
    mock_command.name = "help"
    mock_command.description = "显示帮助信息"
    mock_command.aliases = ["h", "?"]
    mock_command.category = "basic"
    mock_command.usage = "help [命令名称|分类]"
    
    # 默认返回None，但可以在测试中覆盖
    def mock_get_command(command_name):
        if command_name == "wallet":
            mock_cmd = Mock()
            mock_cmd.name = "wallet"
            mock_cmd.description = "钱包管理"
            mock_cmd.usage = "wallet [选项]"
            mock_cmd.aliases = ["w"]
            mock_cmd.category = "finance"
            mock_cmd.get_help.return_value = "详细帮助信息"
            return mock_cmd
        return None
    
    context.registry.get_command.side_effect = mock_get_command
    # 为list_commands设置side_effect来处理不同的分类
    def mock_list_commands(category=None):
        if category == "basic":
            return [mock_command]
        return []
    
    context.registry.list_commands.side_effect = mock_list_commands
    context.user = MockUser()
    context.session_data = {}
    context.user_id = "test_user"
    context.session_id = "test_session"
    context.permissions = ["basic.read", "basic.write"]
    context.logger = Mock()
    return context


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "user_id": "test_user",
        "username": "testuser",
        "email": "test@example.com",
        "display_name": "Test User",
        "bio": "Test user bio",
        "timezone": "UTC",
        "language": "zh-CN",
        "balance": 1000.0,
        "created_at": datetime(2024, 1, 1, 0, 0, 0),
        "last_login": "2024-01-01T12:00:00Z",
        "status": "active",
        "roles": ["user"]
    }


@pytest.fixture
def admin_context(mock_context):
    """管理员上下文"""
    mock_context.permissions.extend([
        "admin.read", "admin.write", "admin.delete",
        "user.create", "user.edit", "user.delete"
    ])
    mock_context.user_manager.is_admin.return_value = True
    mock_context.session_data['is_admin'] = True  # 设置管理员模式
    return mock_context


class AsyncTestCase:
    """异步测试基类"""
    
    def setup_method(self, method):
        """测试方法设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def teardown_method(self, method):
        """测试方法清理"""
        self.loop.close()
    
    async def run_async_test(self, coro):
        """运行异步测试"""
        return await coro


class CommandTestMixin:
    """命令测试混入类"""
    
    def assert_success_result(self, result, expected_message=None):
        """断言成功结果"""
        assert result.success is True
        if expected_message:
            assert expected_message in result.message
    
    def assert_error_result(self, result, expected_error=None):
        """断言错误结果"""
        assert result.success is False
        if expected_error:
            assert expected_error in result.message
    
    def assert_command_properties(self, command, expected_name, expected_aliases=None):
        """断言命令属性"""
        assert command.name == expected_name
        if expected_aliases:
            assert set(command.aliases) == set(expected_aliases)
        assert command.description is not None
        assert command.usage is not None


# 测试数据常量
TEST_USER_DATA = {
    "id": 1,
    "user_id": "test_user_id",
    "username": "test_user",
    "email": "test@example.com",
    "display_name": "Test User",
    "bio": "Test user bio",
    "timezone": "UTC",
    "language": "zh-CN",
    "role": "user",
    "balance": 1000.0,
    "level": 5,
    "experience": 2500,
    "reputation": 100,
    "login_count": 10,
    "command_count": 50,
    "theme": "default",
    "is_active": True,
    "is_verified": True,
    "is_banned": False,
    "created_at": datetime(2024, 1, 1, 0, 0, 0)
}

class MockUser:
    """模拟用户对象"""
    def __init__(self, user_data=None):
        data = user_data or TEST_USER_DATA
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.username = data["username"]
        self.email = data["email"]
        self.display_name = data["display_name"]
        self.bio = data["bio"]
        self.timezone = data["timezone"]
        self.language = data["language"]
        self.role = data["role"]
        self.balance = data["balance"]
        self.level = data["level"]
        self.experience = data["experience"]
        self.reputation = data["reputation"]
        self.login_count = data["login_count"]
        self.command_count = data["command_count"]
        self.theme = data["theme"]
        self.is_active = data["is_active"]
        self.is_verified = data["is_verified"]
        self.is_banned = data["is_banned"]
        self.created_at = data["created_at"]

TEST_COMMANDS = {
    "basic": ["help", "status", "profile", "quit"],
    "admin": ["sudo", "user", "role"],
    "finance": ["bank"],
    "apps": ["calc", "news", "weather"]
}

TEST_USER_PERMISSIONS = {
    "user": ["basic.read", "basic.write"],
    "admin": ["basic.read", "basic.write", "admin.read", "admin.write", "admin.delete"],
    "finance": ["basic.read", "basic.write", "finance.read", "finance.write"],
    "moderator": ["basic.read", "basic.write", "user.moderate"]
}