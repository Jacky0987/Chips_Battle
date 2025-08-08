# -*- coding: utf-8 -*-
"""
基础命令单元测试

测试所有基础命令的功能。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from commands.basic.help import HelpCommand
from commands.basic.status import StatusCommand
from commands.basic.profile import ProfileCommand
from commands.basic.quit import QuitCommand
from tests.conftest import CommandTestMixin, AsyncTestCase


class TestHelpCommand(CommandTestMixin, AsyncTestCase):
    """帮助命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = HelpCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="help",
            expected_aliases=["h", "?", "man"]
        )
    
    @pytest.mark.asyncio
    async def test_help_without_args(self, mock_context):
        """测试无参数帮助命令"""
        # 模拟注册表返回命令列表
        mock_context.registry.get_categories.return_value = ["basic", "admin"]
        mock_context.registry.list_commands.return_value = {
            "basic": ["help", "status", "profile", "quit"],
            "admin": ["sudo", "user", "role"]
        }
        mock_context.registry.get_command_names.return_value = ["help", "status", "profile", "quit"]
        
        result = await self.command.execute([], mock_context)
        
        self.assert_success_result(result)
        assert "可用命令" in result.message or "游戏帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_help_with_specific_command(self, mock_context):
        """测试特定命令帮助"""
        # 模拟获取特定命令
        mock_command = Mock()
        mock_command.name = "wallet"
        mock_command.description = "钱包管理"
        mock_command.usage = "wallet [选项]"
        mock_command.get_help.return_value = "详细帮助信息"
        
        mock_context.registry.get_command.return_value = mock_command
        
        result = await self.command.execute(["wallet"], mock_context)
        
        self.assert_success_result(result)
        assert "wallet" in result.message or "WALLET" in result.message
        assert "钱包管理" in result.message
    
    @pytest.mark.asyncio
    async def test_help_with_unknown_command(self, mock_context):
        """测试未知命令帮助"""
        mock_context.registry.get_command.return_value = None
        mock_context.registry.search_commands.return_value = ["status", "sudo"]
        
        result = await self.command.execute(["unknown"], mock_context)
        
        self.assert_error_result(result, "未找到命令")
        assert "未找到命令" in result.message
    
    @pytest.mark.asyncio
    async def test_help_with_category(self, mock_context):
        """测试分类帮助"""
        # 模拟basic分类存在且有命令
        mock_command = Mock()
        mock_command.name = "help"
        mock_command.description = "显示帮助信息"
        mock_command.aliases = ["h"]
        mock_context.registry.list_commands.return_value = [mock_command]
        
        result = await self.command.execute(["basic"], mock_context)
        
        self.assert_success_result(result)
        assert "BASIC" in result.message or "分类帮助" in result.message


class TestStatusCommand(CommandTestMixin, AsyncTestCase):
    """状态命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = StatusCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="status",
            expected_aliases=["stat", "info"]
        )
    
    @pytest.mark.asyncio
    async def test_status_basic(self, mock_context, sample_user_data):
        """测试基本状态显示"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        result = await self.command.execute([], mock_context)
        
        self.assert_success_result(result)
        assert "状态信息已显示" in result.message
    
    @pytest.mark.asyncio
    async def test_status_detailed(self, mock_context, sample_user_data):
        """测试详细状态显示"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        result = await self.command.execute(["--detailed"], mock_context)
        
        self.assert_success_result(result)
        assert "状态信息已显示" in result.message
    
    @pytest.mark.asyncio
    async def test_status_system(self, mock_context):
        """测试系统状态显示"""
        with patch('psutil.cpu_percent', return_value=25.5), \
             patch('psutil.virtual_memory') as mock_memory:
            
            mock_memory.return_value.percent = 60.0
            mock_memory.return_value.available = 4 * 1024 * 1024 * 1024  # 4GB
            
            result = await self.command.execute(["--system"], mock_context)
            
            self.assert_success_result(result)
        assert "状态信息已显示" in result.message
    
    @pytest.mark.asyncio
    async def test_status_help(self, mock_context):
        """测试状态命令帮助"""
        result = await self.command.execute(["--help"], mock_context)
        
        self.assert_success_result(result)
        assert "状态信息已显示" in result.message


class TestProfileCommand(CommandTestMixin, AsyncTestCase):
    """个人资料命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = ProfileCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="profile",
            expected_aliases=["me", "prof", "user"]
        )
    
    @pytest.mark.asyncio
    async def test_profile_view(self, mock_context, sample_user_data):
        """测试查看个人资料"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        result = await self.command.execute([], mock_context)
        
        self.assert_success_result(result)
        assert "个人资料已显示" in result.message
    
    @pytest.mark.asyncio
    async def test_profile_edit_email(self, mock_context, sample_user_data):
        """测试编辑邮箱"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        mock_context.database.update_user.return_value = True
        
        new_email = "newemail@example.com"
        result = await self.command.execute(["edit", "email", new_email], mock_context)
        
        self.assert_error_result(result)
        assert "不可编辑" in result.message
    
    @pytest.mark.asyncio
    async def test_profile_edit_invalid_email(self, mock_context, sample_user_data):
        """测试编辑无效邮箱"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        invalid_email = "invalid-email"
        result = await self.command.execute(["edit", "email", invalid_email], mock_context)
        
        self.assert_error_result(result, "不可编辑")
    
    @pytest.mark.asyncio
    async def test_profile_stats(self, mock_context, sample_user_data):
        """测试个人统计"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        result = await self.command.execute(["stats"], mock_context)
        
        self.assert_success_result(result)
        assert "个人资料已显示" in result.message
    
    @pytest.mark.asyncio
    async def test_profile_help(self, mock_context):
        """测试个人资料帮助"""
        result = await self.command.execute(["help"], mock_context)
        
        self.assert_success_result(result)
        assert "个人资料已显示" in result.message


class TestQuitCommand(CommandTestMixin, AsyncTestCase):
    """退出命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = QuitCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="quit",
            expected_aliases=["exit", "bye", "logout"]
        )
    
    @pytest.mark.asyncio
    async def test_quit_basic(self, mock_context):
        """测试基本退出"""
        result = await self.command.execute(["--force"], mock_context)
        
        self.assert_success_result(result)
        assert "再见" in result.message
        assert result.action == 'quit'
    
    @pytest.mark.asyncio
    async def test_quit_with_message(self, mock_context):
        """测试带消息退出"""
        result = await self.command.execute(["--force", "--message", "测试退出"], mock_context)
        
        self.assert_success_result(result)
        assert "再见" in result.message
        assert result.action == 'quit'
    
    @pytest.mark.asyncio
    async def test_quit_force(self, mock_context):
        """测试强制退出"""
        result = await self.command.execute(["--force"], mock_context)
        
        self.assert_success_result(result)
        assert result.action == 'quit'
    
    @pytest.mark.asyncio
    async def test_quit_help(self, mock_context):
        """测试退出命令帮助"""
        result = await self.command.execute(["help"], mock_context)
        
        self.assert_error_result(result)
        assert "退出时发生错误" in result.message or "stdin" in result.message
        assert result.action != 'quit'  # 帮助不应该退出


class TestBasicCommandsIntegration(CommandTestMixin, AsyncTestCase):
    """基础命令集成测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.commands = {
            "help": HelpCommand(),
            "status": StatusCommand(),
            "profile": ProfileCommand(),
            "quit": QuitCommand()
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
    
    def test_no_alias_conflicts(self):
        """测试别名无冲突"""
        all_aliases = set()
        for command in self.commands.values():
            for alias in command.aliases:
                assert alias not in all_aliases, f"别名冲突: {alias}"
                all_aliases.add(alias)
    
    @pytest.mark.asyncio
    async def test_all_commands_execute_without_error(self, mock_context, sample_user_data):
        """测试所有命令都能正常执行"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        mock_context.registry.get_categories.return_value = ["basic"]
        mock_context.registry.list_commands.return_value = {"basic": list(self.commands.keys())}
        
        for name, command in self.commands.items():
            try:
                result = await command.execute([], mock_context)
                assert result is not None
                assert hasattr(result, 'success')
                assert hasattr(result, 'message')
            except Exception as e:
                pytest.fail(f"命令 {name} 执行失败: {e}")
    
    @pytest.mark.asyncio
    async def test_help_command_lists_all_basic_commands(self, mock_context):
        """测试帮助命令列出所有基础命令"""
        mock_context.registry.get_categories.return_value = ["basic"]
        mock_context.registry.list_commands.return_value = {
            "basic": list(self.commands.keys())
        }
        
        help_command = self.commands["help"]
        result = await help_command.execute(["basic"], mock_context)
        
        self.assert_success_result(result)
        
        # 检查帮助信息已显示
        assert "帮助信息" in result.message or "命令列表" in result.message