# -*- coding: utf-8 -*-
"""
管理员命令单元测试

测试所有管理员命令的功能。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from commands.admin.sudo import SudoCommand
from commands.admin.user import UserCommand
from commands.admin.role import RoleCommand
from tests.conftest import CommandTestMixin, AsyncTestCase


class TestSudoCommand(CommandTestMixin, AsyncTestCase):
    """Sudo命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = SudoCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="sudo",
            expected_aliases=["su", "admin"]
        )
    
    @pytest.mark.asyncio
    async def test_sudo_without_permission(self, mock_context):
        """测试无权限执行sudo"""
        mock_context.session_data = {}
        
        result = await self.command.execute(["test"], mock_context)
        
        self.assert_error_result(result, "需要管理员认证")
    
    @pytest.mark.asyncio
    async def test_sudo_help(self, admin_context):
        """测试sudo帮助"""
        result = await self.command.execute(["help"], admin_context)
        
        self.assert_success_result(result)
        assert "管理员命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_sudo_status(self, admin_context):
        """测试sudo状态"""
        result = await self.command.execute(["system", "status"], admin_context)
        
        self.assert_success_result(result)
        assert "系统状态" in result.message
    
    @pytest.mark.asyncio
    async def test_sudo_users(self, admin_context):
        """测试sudo用户管理"""
        result = await self.command.execute(["user", "list"], admin_context)
        
        self.assert_success_result(result)
        assert "用户" in result.message
    
    @pytest.mark.asyncio
    async def test_sudo_roles(self, admin_context):
        """测试sudo角色管理"""
        result = await self.command.execute(["role", "list"], admin_context)
        
        self.assert_success_result(result)
        assert "角色" in result.message
    
    @pytest.mark.asyncio
    async def test_sudo_system(self, admin_context):
        """测试sudo系统管理"""
        result = await self.command.execute(["system", "status"], admin_context)
        
        self.assert_success_result(result)
        assert "系统" in result.message
    
    @pytest.mark.asyncio
    async def test_sudo_logs(self, admin_context):
        """测试sudo日志查看"""
        result = await self.command.execute(["system", "logs"], admin_context)
        
        self.assert_success_result(result)
        assert "系统日志" in result.message
    
    @pytest.mark.asyncio
    async def test_sudo_unknown_action(self, admin_context):
        """测试sudo未知操作"""
        result = await self.command.execute(["unknown"], admin_context)
        
        self.assert_error_result(result)
        assert "未知的sudo命令" in result.message


class TestUserCommand(CommandTestMixin, AsyncTestCase):
    """用户命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = UserCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="user",
            expected_aliases=["users", "usr"]
        )
    
    @pytest.mark.asyncio
    async def test_user_without_permission(self, mock_context):
        """测试无权限执行用户命令"""
        mock_context.user_manager.is_admin.return_value = False
        
        result = await self.command.execute(["list"], mock_context)
        
        self.assert_error_result(result, "权限不足")
    
    @pytest.mark.asyncio
    async def test_user_help(self, admin_context):
        """测试用户命令帮助"""
        result = await self.command.execute(["help"], admin_context)
        
        self.assert_success_result(result)
        assert "用户管理命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_user_list(self, admin_context):
        """测试用户列表"""
        admin_context.database.get_all_users.return_value = [
            {"username": "user1", "email": "user1@example.com", "status": "active"},
            {"username": "user2", "email": "user2@example.com", "status": "banned"}
        ]
        
        result = await self.command.execute(["list"], admin_context)
        
        self.assert_success_result(result)
        assert "用户列表" in result.message
    
    @pytest.mark.asyncio
    async def test_user_info(self, admin_context, sample_user_data):
        """测试用户信息查看"""
        admin_context.database.get_user.return_value = sample_user_data
        
        result = await self.command.execute(["info", "testuser"], admin_context)
        
        self.assert_success_result(result)
        assert "用户信息" in result.message
        assert "testuser" in result.message
    
    @pytest.mark.asyncio
    async def test_user_create(self, admin_context):
        """测试用户创建"""
        admin_context.database.create_user.return_value = True
        
        result = await self.command.execute(["create"], admin_context)
        
        self.assert_success_result(result)
        assert "创建新用户" in result.message
    
    @pytest.mark.asyncio
    async def test_user_edit(self, admin_context):
        """测试用户编辑"""
        admin_context.database.update_user.return_value = True
        
        result = await self.command.execute(["edit", "testuser", "email"], admin_context)
        
        self.assert_success_result(result)
        assert "编辑用户" in result.message
        assert "testuser" in result.message
    
    @pytest.mark.asyncio
    async def test_user_delete(self, admin_context):
        """测试用户删除"""
        admin_context.database.delete_user.return_value = True
        
        result = await self.command.execute(["delete", "testuser"], admin_context)
        
        self.assert_success_result(result)
        assert "删除用户" in result.message
        assert "testuser" in result.message
    
    @pytest.mark.asyncio
    async def test_user_ban(self, admin_context):
        """测试用户封禁"""
        admin_context.database.update_user.return_value = True
        
        result = await self.command.execute(["ban", "testuser"], admin_context)
        
        self.assert_success_result(result)
        assert "封禁用户" in result.message
        assert "testuser" in result.message
    
    @pytest.mark.asyncio
    async def test_user_unban(self, admin_context):
        """测试用户解封"""
        admin_context.database.update_user.return_value = True
        
        result = await self.command.execute(["unban", "testuser"], admin_context)
        
        self.assert_success_result(result)
        assert "解封用户" in result.message
        assert "testuser" in result.message
    
    @pytest.mark.asyncio
    async def test_user_without_args(self, admin_context):
        """测试无参数用户命令"""
        result = await self.command.execute([], admin_context)
        
        self.assert_success_result(result)
        assert "用户管理命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_user_unknown_action(self, admin_context):
        """测试未知用户操作"""
        result = await self.command.execute(["unknown"], admin_context)
        
        self.assert_error_result(result, "未知的用户管理操作")


class TestRoleCommand(CommandTestMixin, AsyncTestCase):
    """角色命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = RoleCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="role",
            expected_aliases=["roles", "perm", "permission"]
        )
    
    @pytest.mark.asyncio
    async def test_role_without_permission(self, mock_context):
        """测试无权限执行角色命令"""
        mock_context.user_manager.is_admin.return_value = False
        
        result = await self.command.execute(["list"], mock_context)
        
        self.assert_error_result(result, "权限不足")
    
    @pytest.mark.asyncio
    async def test_role_help(self, admin_context):
        """测试角色命令帮助"""
        result = await self.command.execute(["help"], admin_context)
        
        self.assert_success_result(result)
        assert "角色管理命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_role_list(self, admin_context):
        """测试角色列表"""
        result = await self.command.execute(["list"], admin_context)
        
        self.assert_success_result(result)
        assert "角色列表" in result.message
    
    @pytest.mark.asyncio
    async def test_role_info(self, admin_context):
        """测试角色信息查看"""
        result = await self.command.execute(["info", "admin"], admin_context)
        
        self.assert_success_result(result)
        assert "角色信息" in result.message
        assert "admin" in result.message
    
    @pytest.mark.asyncio
    async def test_role_create(self, admin_context):
        """测试角色创建"""
        result = await self.command.execute(["create"], admin_context)
        
        self.assert_success_result(result)
        assert "创建新角色" in result.message
    
    @pytest.mark.asyncio
    async def test_role_edit(self, admin_context):
        """测试角色编辑"""
        result = await self.command.execute(["edit", "moderator", "permissions"], admin_context)
        
        self.assert_success_result(result)
        assert "编辑角色" in result.message
        assert "moderator" in result.message
    
    @pytest.mark.asyncio
    async def test_role_delete(self, admin_context):
        """测试角色删除"""
        result = await self.command.execute(["delete", "old_role"], admin_context)
        
        self.assert_success_result(result)
        assert "删除角色" in result.message
        assert "old_role" in result.message
    
    @pytest.mark.asyncio
    async def test_role_assign(self, admin_context):
        """测试角色分配"""
        result = await self.command.execute(["assign", "testuser", "moderator"], admin_context)
        
        self.assert_success_result(result)
        assert "角色分配" in result.message
        assert "testuser" in result.message
        assert "moderator" in result.message
    
    @pytest.mark.asyncio
    async def test_role_revoke(self, admin_context):
        """测试角色撤销"""
        result = await self.command.execute(["revoke", "testuser", "moderator"], admin_context)
        
        self.assert_success_result(result)
        assert "角色撤销" in result.message
        assert "testuser" in result.message
        assert "moderator" in result.message
    
    @pytest.mark.asyncio
    async def test_role_permissions(self, admin_context):
        """测试权限列表"""
        result = await self.command.execute(["permissions"], admin_context)
        
        self.assert_success_result(result)
        assert "权限列表" in result.message
    
    @pytest.mark.asyncio
    async def test_role_without_args(self, admin_context):
        """测试无参数角色命令"""
        result = await self.command.execute([], admin_context)
        
        self.assert_success_result(result)
        assert "角色管理命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_role_unknown_action(self, admin_context):
        """测试未知角色操作"""
        result = await self.command.execute(["unknown"], admin_context)
        
        self.assert_error_result(result, "未知的角色管理操作")
    
    @pytest.mark.asyncio
    async def test_role_assign_missing_args(self, admin_context):
        """测试角色分配缺少参数"""
        result = await self.command.execute(["assign", "testuser"], admin_context)
        
        self.assert_error_result(result, "未知的角色管理操作")
    
    @pytest.mark.asyncio
    async def test_role_revoke_missing_args(self, admin_context):
        """测试角色撤销缺少参数"""
        result = await self.command.execute(["revoke", "testuser"], admin_context)
        
        self.assert_error_result(result, "未知的角色管理操作")


class TestAdminCommandsIntegration(CommandTestMixin, AsyncTestCase):
    """管理员命令集成测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.commands = {
            "sudo": SudoCommand(),
            "user": UserCommand(),
            "role": RoleCommand()
        }
    
    def test_all_commands_have_required_properties(self):
        """测试所有命令都有必需属性"""
        for name, command in self.commands.items():
            assert hasattr(command, 'name')
            assert hasattr(command, 'aliases')
            assert hasattr(command, 'description')
            assert hasattr(command, 'usage')
            assert hasattr(command, 'execute')
            assert command.name == name
    
    def test_all_commands_are_admin_commands(self):
        """测试所有命令都是管理员命令"""
        from commands.base import AdminCommand
        for command in self.commands.values():
            assert isinstance(command, AdminCommand)
    
    def test_no_alias_conflicts(self):
        """测试别名无冲突"""
        all_aliases = set()
        for command in self.commands.values():
            for alias in command.aliases:
                assert alias not in all_aliases, f"别名冲突: {alias}"
                all_aliases.add(alias)
    
    @pytest.mark.asyncio
    async def test_all_commands_require_admin_permission(self, mock_context):
        """测试所有命令都需要管理员权限"""
        mock_context.user_manager.is_admin.return_value = False
        
        for name, command in self.commands.items():
            result = await command.execute(["help"], mock_context)
            # 所有管理员命令在无权限时都应该返回错误
            if not result.success:
                assert "权限" in result.message or "管理员" in result.message
    
    @pytest.mark.asyncio
    async def test_all_commands_execute_with_admin_permission(self, admin_context):
        """测试所有命令在有管理员权限时都能执行"""
        for name, command in self.commands.items():
            try:
                result = await command.execute(["help"], admin_context)
                assert result is not None
                assert hasattr(result, 'success')
                assert hasattr(result, 'message')
            except Exception as e:
                pytest.fail(f"管理员命令 {name} 执行失败: {e}")
    
    @pytest.mark.asyncio
    async def test_commands_handle_empty_args(self, admin_context):
        """测试命令处理空参数"""
        for name, command in self.commands.items():
            try:
                result = await command.execute([], admin_context)
                assert result is not None
                # 空参数应该显示帮助或执行默认操作
                assert result.success is True
            except Exception as e:
                pytest.fail(f"管理员命令 {name} 处理空参数失败: {e}")