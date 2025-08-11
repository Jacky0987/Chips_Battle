# -*- coding: utf-8 -*-
"""
金融命令单元测试

测试所有金融命令的功能。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal

from commands.finance.bank import BankCommand
from tests.conftest import CommandTestMixin, AsyncTestCase


class TestBankCommand(CommandTestMixin, AsyncTestCase):
    """银行命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = BankCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="bank",
            expected_aliases=["b", "banking"]
        )
    
    @pytest.mark.asyncio
    async def test_bank_help(self, mock_context):
        """测试银行命令帮助"""
        result = await self.command.execute(["help"], mock_context)
        
        self.assert_success_result(result)
        assert "银行系统帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_bank_balance(self, mock_context, sample_user_data):
        """测试查看余额"""
        # 模拟用户对象
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "💰 账户余额: 1000.0 JCY"
            
            result = await self.command.execute(["balance"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["balance"])
    
    @pytest.mark.asyncio
    async def test_bank_deposit_valid_amount(self, mock_context, sample_user_data):
        """测试有效金额存款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 存款成功: 100 JCY"
            
            result = await self.command.execute(["deposit", "100"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["deposit", "100"])
    
    @pytest.mark.asyncio
    async def test_bank_deposit_invalid_amount(self, mock_context, sample_user_data):
        """测试无效金额存款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "❌ 存款金额必须大于0"
            
            result = await self.command.execute(["deposit", "-50"], mock_context)
            
            self.assert_error_result(result)
    
    @pytest.mark.asyncio
    async def test_bank_deposit_non_numeric_amount(self, mock_context, sample_user_data):
        """测试非数字金额存款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "❌ 金额必须是数字"
            
            result = await self.command.execute(["deposit", "abc"], mock_context)
            
            self.assert_error_result(result)
    
    @pytest.mark.asyncio
    async def test_bank_withdraw_valid_amount(self, mock_context, sample_user_data):
        """测试有效金额取款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 取款成功: 100 JCY"
            
            result = await self.command.execute(["withdraw", "100"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["withdraw", "100"])
    
    @pytest.mark.asyncio
    async def test_bank_withdraw_insufficient_funds(self, mock_context, sample_user_data):
        """测试余额不足取款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "❌ 余额不足"
            
            result = await self.command.execute(["withdraw", "1000"], mock_context)
            
            self.assert_error_result(result)
    
    @pytest.mark.asyncio
    async def test_bank_transfer_valid(self, mock_context, sample_user_data):
        """测试有效转账"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 转账成功: 100 JCY 已转账给 target_user"
            
            result = await self.command.execute(["transfer", "target_user", "100"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["transfer", "target_user", "100"])
    
    @pytest.mark.asyncio
    async def test_bank_transfer_to_nonexistent_user(self, mock_context, sample_user_data):
        """测试转账给不存在的用户"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "❌ 转入账户不存在或未启用"
            
            result = await self.command.execute(["transfer", "nonexistent", "100"], mock_context)
            
            self.assert_error_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["transfer", "nonexistent", "100"])
    
    @pytest.mark.asyncio
    async def test_bank_transfer_to_self(self, mock_context, sample_user_data):
        """测试转账给自己"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "❌ 不能转账给自己"
            
            result = await self.command.execute(["transfer", sample_user_data["user_id"], "100"], mock_context)
            
            self.assert_error_result(result)
    
    @pytest.mark.asyncio
    async def test_bank_history(self, mock_context, sample_user_data):
        """测试交易历史"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 交易历史记录:\n存款: 100 JCY\n取款: 50 JCY"
            
            result = await self.command.execute(["history"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["history"])
    
    @pytest.mark.asyncio
    async def test_bank_history_with_limit(self, mock_context, sample_user_data):
        """测试限制数量的交易历史"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 交易历史记录 (最近5条):\n存款: 100 JCY"
            
            result = await self.command.execute(["history", "5"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["history", "5"])
    
    @pytest.mark.asyncio
    async def test_bank_stats(self, mock_context, sample_user_data):
        """测试银行统计"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 银行统计信息:\n总余额: 1000 JCY\n总交易: 10笔"
            
            result = await self.command.execute(["stats"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["stats"])
    
    @pytest.mark.asyncio
    async def test_bank_loan_info(self, mock_context, sample_user_data):
        """测试贷款信息"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 贷款信息:\n当前贷款: 0 JCY\n信用评级: A"
            
            result = await self.command.execute(["loan", "info"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["loan", "info"])
    
    @pytest.mark.asyncio
    async def test_bank_loan_apply(self, mock_context, sample_user_data):
        """测试申请贷款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 贷款申请成功: 1000 JCY"
            
            result = await self.command.execute(["loan", "apply", "1000"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["loan", "apply", "1000"])
    
    @pytest.mark.asyncio
    async def test_bank_loan_repay(self, mock_context, sample_user_data):
        """测试还款"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 还款成功: 500 JCY"
            
            result = await self.command.execute(["loan", "repay", "500"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["loan", "repay", "500"])
    
    @pytest.mark.asyncio
    async def test_bank_investment_info(self, mock_context, sample_user_data):
        """测试投资信息"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 投资信息:\n当前投资: 0 JCY\n收益率: 5%"
            
            result = await self.command.execute(["investment", "info"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["investment", "info"])
    
    @pytest.mark.asyncio
    async def test_bank_investment_buy(self, mock_context, sample_user_data):
        """测试购买投资"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 投资购买成功: STOCK1 100股"
            
            result = await self.command.execute(["investment", "buy", "STOCK1", "100"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["investment", "buy", "STOCK1", "100"])
    
    @pytest.mark.asyncio
    async def test_bank_investment_sell(self, mock_context, sample_user_data):
        """测试出售投资"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 投资出售成功: STOCK1 50股"
            
            result = await self.command.execute(["investment", "sell", "STOCK1", "50"], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], ["investment", "sell", "STOCK1", "50"])
    
    @pytest.mark.asyncio
    async def test_bank_without_args(self, mock_context, sample_user_data):
        """测试无参数银行命令"""
        mock_user = Mock()
        mock_user.user_id = sample_user_data["user_id"]
        mock_context.user = mock_user
        
        with patch('commands.finance.bank.bank_commands.bank') as mock_bank:
            mock_bank.return_value = "✅ 银行帮助信息:\n可用命令: balance, deposit, withdraw, transfer"
            
            result = await self.command.execute([], mock_context)
            
            self.assert_success_result(result)
            mock_bank.assert_called_once_with(sample_user_data["user_id"], [])
    
    @pytest.mark.asyncio
    async def test_bank_unknown_action(self, mock_context):
        """测试未知银行操作"""
        result = await self.command.execute(["unknown"], mock_context)
        
        self.assert_error_result(result, "未知的银行命令")
    
    @pytest.mark.asyncio
    async def test_bank_missing_amount_for_deposit(self, mock_context):
        """测试存款缺少金额参数"""
        result = await self.command.execute(["deposit"], mock_context)
        
        self.assert_error_result(result, "用法: bank deposit")
    
    @pytest.mark.asyncio
    async def test_bank_missing_amount_for_withdraw(self, mock_context):
        """测试取款缺少金额参数"""
        result = await self.command.execute(["withdraw"], mock_context)
        
        self.assert_error_result(result, "用法: bank withdraw")
    
    @pytest.mark.asyncio
    async def test_bank_missing_args_for_transfer(self, mock_context):
        """测试转账缺少参数"""
        result = await self.command.execute(["transfer"], mock_context)
        
        self.assert_error_result(result, "用法: bank transfer")
    
    @pytest.mark.asyncio
    async def test_bank_missing_amount_for_transfer(self, mock_context):
        """测试转账缺少金额参数"""
        result = await self.command.execute(["transfer", "target"], mock_context)
        
        self.assert_error_result(result, "用法: bank transfer")
    
    def test_help_content(self):
        """测试帮助内容"""
        help_text = self.command.get_help()
        assert "银行系统帮助" in help_text
        assert "银行卡管理" in help_text
        assert "存取款" in help_text
        assert "贷款管理" in help_text


class TestFinanceCommandsIntegration(CommandTestMixin, AsyncTestCase):
    """金融命令集成测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.commands = {
            "bank": BankCommand()
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
    
    def test_all_commands_are_finance_commands(self):
        """测试所有命令都是金融命令"""
        from commands.base import FinanceCommand
        for command in self.commands.values():
            assert isinstance(command, FinanceCommand)
    
    @pytest.mark.asyncio
    async def test_all_commands_execute_without_error(self, mock_context, sample_user_data):
        """测试所有命令都能正常执行"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        for name, command in self.commands.items():
            try:
                result = await command.execute(["help"], mock_context)
                assert result is not None
                assert hasattr(result, 'success')
                assert hasattr(result, 'message')
            except Exception as e:
                pytest.fail(f"金融命令 {name} 执行失败: {e}")
    
    @pytest.mark.asyncio
    async def test_commands_handle_user_data_access(self, mock_context, sample_user_data):
        """测试命令处理用户数据访问"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        
        for name, command in self.commands.items():
            try:
                # 测试需要用户数据的操作
                result = await command.execute(["balance"], mock_context)
                assert result is not None
                # 应该能够访问用户余额信息
                if result.success:
                    assert "余额" in result.message or "balance" in result.message.lower()
            except Exception as e:
                pytest.fail(f"金融命令 {name} 访问用户数据失败: {e}")
    
    @pytest.mark.asyncio
    async def test_commands_handle_database_operations(self, mock_context, sample_user_data):
        """测试命令处理数据库操作"""
        mock_context.user_manager.get_current_user.return_value = sample_user_data
        mock_context.database.update_user.return_value = True
        
        bank_command = self.commands["bank"]
        
        # 测试存款操作
        result = await bank_command.execute(["deposit", "100"], mock_context)
        assert result is not None
        
        # 测试取款操作
        result = await bank_command.execute(["withdraw", "50"], mock_context)
        assert result is not None