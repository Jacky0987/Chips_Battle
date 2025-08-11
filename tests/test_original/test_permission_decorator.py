#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限装饰器测试

测试permission_required装饰器的功能
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from services.auth_service import AuthService, permission_required
from commands.base import CommandContext, CommandResult
from models.auth.user import User
from models.auth.role import Role
from models.auth.permission import Permission


class TestPermissionDecorator:
    """权限装饰器测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        # 创建模拟对象
        self.mock_uow = Mock()
        self.mock_event_bus = Mock()
        self.auth_service = AuthService(self.mock_uow, self.mock_event_bus)
        
        # 创建测试用户
        self.test_user = User(
            user_id="test_user_id",
            username="testuser",
            password_hash="hashed_password",
            email="test@example.com",
            created_at=datetime.now(),
            is_active=True
        )
        
        # 创建测试上下文
        self.test_context = CommandContext(
            user=self.test_user,
            session_data={},
            game_time=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_permission_required_with_permission(self):
        """测试用户有权限时的装饰器行为"""
        # 模拟用户有权限
        self.auth_service.has_permission = AsyncMock(return_value=True)
        
        @permission_required("test_permission", self.auth_service)
        async def test_command(args, context):
            return CommandResult(success=True, message="命令执行成功")
        
        # 执行测试
        result = await test_command([], self.test_context)
        
        # 验证结果
        assert result.success is True
        assert result.message == "命令执行成功"
        
        # 验证权限检查被调用
        self.auth_service.has_permission.assert_called_once_with(
            self.test_user, "test_permission"
        )
    
    @pytest.mark.asyncio
    async def test_permission_required_without_permission(self):
        """测试用户没有权限时的装饰器行为"""
        # 模拟用户没有权限
        self.auth_service.has_permission = AsyncMock(return_value=False)
        
        @permission_required("test_permission", self.auth_service)
        async def test_command(args, context):
            return CommandResult(success=True, message="命令执行成功")
        
        # 执行测试
        result = await test_command([], self.test_context)
        
        # 验证结果
        assert result.success is False
        assert "权限不足" in result.message
        assert "test_permission" in result.message
        
        # 验证权限检查被调用
        self.auth_service.has_permission.assert_called_once_with(
            self.test_user, "test_permission"
        )
    
    @pytest.mark.asyncio
    async def test_permission_required_no_user(self):
        """测试没有用户时的装饰器行为"""
        # 创建没有用户的上下文
        no_user_context = CommandContext(
            user=None,
            session_data={},
            game_time=datetime.now()
        )
        
        @permission_required("test_permission", self.auth_service)
        async def test_command(args, context):
            return CommandResult(success=True, message="命令执行成功")
        
        # 执行测试
        result = await test_command([], no_user_context)
        
        # 验证结果
        assert result.success is False
        assert "用户未登录" in result.message
    
    @pytest.mark.asyncio
    async def test_permission_required_no_context(self):
        """测试没有上下文时的装饰器行为"""
        @permission_required("test_permission", self.auth_service)
        async def test_command(args):
            return CommandResult(success=True, message="命令执行成功")
        
        # 执行测试（不传递context）
        result = await test_command([])
        
        # 验证结果
        assert result.success is False
        assert "无法获取命令执行上下文" in result.message
    
    @pytest.mark.asyncio
    async def test_permission_required_no_auth_service(self):
        """测试没有认证服务时的装饰器行为"""
        @permission_required("test_permission")  # 不提供auth_service
        async def test_command(args, context):
            return CommandResult(success=True, message="命令执行成功")
        
        # 执行测试
        result = await test_command([], self.test_context)
        
        # 验证结果
        assert result.success is False
        assert "认证服务不可用" in result.message


class TestAuthServicePermissionMethods:
    """AuthService权限方法测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_uow = Mock()
        self.mock_event_bus = Mock()
        self.auth_service = AuthService(self.mock_uow, self.mock_event_bus)
        
        # 创建测试用户
        self.test_user = User(
            user_id="test_user_id",
            username="testuser",
            password_hash="hashed_password",
            email="test@example.com",
            created_at=datetime.now(),
            is_active=True
        )
    
    @pytest.mark.asyncio
    async def test_has_permission_success(self):
        """测试权限检查成功"""
        # 模拟数据库查询
        mock_session = Mock()
        mock_result = Mock()
        mock_permission = Mock()
        mock_permission.name = "test_permission"
        
        mock_result.scalars.return_value.all.return_value = [mock_permission]
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        self.mock_uow.session = mock_session
        self.mock_uow.__aenter__ = AsyncMock(return_value=self.mock_uow)
        self.mock_uow.__aexit__ = AsyncMock(return_value=None)
        
        # 执行测试
        result = await self.auth_service.has_permission(self.test_user, "test_permission")
        
        # 验证结果
        assert result is True
    
    @pytest.mark.asyncio
    async def test_has_permission_failure(self):
        """测试权限检查失败"""
        # 模拟数据库查询返回空结果
        mock_session = Mock()
        mock_result = Mock()
        
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        self.mock_uow.session = mock_session
        self.mock_uow.__aenter__ = AsyncMock(return_value=self.mock_uow)
        self.mock_uow.__aexit__ = AsyncMock(return_value=None)
        
        # 执行测试
        result = await self.auth_service.has_permission(self.test_user, "nonexistent_permission")
        
        # 验证结果
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self):
        """测试获取用户权限"""
        # 模拟数据库查询
        mock_session = Mock()
        mock_result = Mock()
        mock_permission1 = Mock()
        mock_permission1.name = "permission1"
        mock_permission2 = Mock()
        mock_permission2.name = "permission2"
        
        mock_result.scalars.return_value.all.return_value = [mock_permission1, mock_permission2]
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        self.mock_uow.session = mock_session
        self.mock_uow.__aenter__ = AsyncMock(return_value=self.mock_uow)
        self.mock_uow.__aexit__ = AsyncMock(return_value=None)
        
        # 执行测试
        result = await self.auth_service.get_user_permissions(self.test_user)
        
        # 验证结果
        assert isinstance(result, list)
        assert "permission1" in result
        assert "permission2" in result


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])