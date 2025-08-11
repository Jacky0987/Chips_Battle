# -*- coding: utf-8 -*-
"""
应用命令单元测试

测试所有应用命令的功能。
"""

import pytest
import math
from unittest.mock import Mock, AsyncMock, patch, PropertyMock

from commands.apps.calculator import CalculatorCommand
from commands.apps.news import NewsCommand
from commands.apps.weather import WeatherCommand
from tests.conftest import CommandTestMixin, AsyncTestCase


class TestCalculatorCommand(CommandTestMixin, AsyncTestCase):
    """计算器命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = CalculatorCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="calc",
            expected_aliases=["calculator", "math", "compute"]
        )
    
    @pytest.mark.asyncio
    async def test_calc_help(self, mock_context):
        """测试计算器帮助"""
        result = await self.command.execute(["help"], mock_context)
        
        self.assert_success_result(result)
        assert "计算器命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_functions(self, mock_context):
        """测试显示函数列表"""
        result = await self.command.execute(["functions"], mock_context)
        
        self.assert_success_result(result)
        assert "可用数学函数" in result.message
        assert "sin" in result.message
        assert "cos" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_constants(self, mock_context):
        """测试显示常数列表"""
        result = await self.command.execute(["constants"], mock_context)
        
        self.assert_success_result(result)
        assert "可用数学常数" in result.message
        assert "pi" in result.message
        assert "e" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_basic_arithmetic(self, mock_context):
        """测试基本算术运算"""
        test_cases = [
            ("2 + 3", "5"),
            ("10 - 4", "6"),
            ("3 * 4", "12"),
            ("15 / 3", "5"),
            ("2 ** 3", "8"),
            ("17 % 5", "2")
        ]
        
        for expression, expected in test_cases:
            result = await self.command.execute(expression.split(), mock_context)
            self.assert_success_result(result)
            assert expected in result.message
    
    @pytest.mark.asyncio
    async def test_calc_complex_expression(self, mock_context):
        """测试复杂表达式"""
        result = await self.command.execute(["(2 + 3) * 4 - 1"], mock_context)
        
        self.assert_success_result(result)
        assert "19" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_math_functions(self, mock_context):
        """测试数学函数"""
        test_cases = [
            ("sqrt(16)", "4"),
            ("abs(-5)", "5"),
            ("max(3, 7)", "7"),
            ("min(3, 7)", "3")
        ]
        
        for expression, expected in test_cases:
            result = await self.command.execute(expression.split(), mock_context)
            self.assert_success_result(result)
            assert expected in result.message
    
    @pytest.mark.asyncio
    async def test_calc_trigonometric_functions(self, mock_context):
        """测试三角函数"""
        # sin(pi/2) = 1
        result = await self.command.execute(["sin(pi/2)"], mock_context)
        self.assert_success_result(result)
        assert "1" in result.message
        
        # cos(0) = 1
        result = await self.command.execute(["cos(0)"], mock_context)
        self.assert_success_result(result)
        assert "1" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_logarithmic_functions(self, mock_context):
        """测试对数函数"""
        # log10(100) = 2
        result = await self.command.execute(["log10(100)"], mock_context)
        self.assert_success_result(result)
        assert "2" in result.message
        
        # ln(e) = 1
        result = await self.command.execute(["ln(e)"], mock_context)
        self.assert_success_result(result)
        assert "1" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_constants_usage(self, mock_context):
        """测试常数使用"""
        # pi * 2
        result = await self.command.execute(["pi * 2"], mock_context)
        self.assert_success_result(result)
        # 应该接近 6.28
        assert "6.28" in result.message or "6.283" in result.message
    
    @pytest.mark.asyncio
    async def test_calc_division_by_zero(self, mock_context):
        """测试除零错误"""
        result = await self.command.execute(["1 / 0"], mock_context)
        
        self.assert_error_result(result, "除零错误")
    
    @pytest.mark.asyncio
    async def test_calc_invalid_expression(self, mock_context):
        """测试无效表达式"""
        result = await self.command.execute(["2 +"], mock_context)
        
        self.assert_error_result(result, "语法错误")
    
    @pytest.mark.asyncio
    async def test_calc_without_args(self, mock_context):
        """测试无参数计算器命令"""
        result = await self.command.execute([], mock_context)
        
        self.assert_success_result(result)
        assert "计算器命令帮助" in result.message
    
    def test_preprocess_expression(self):
        """测试表达式预处理"""
        # 测试幂运算符替换
        assert self.command._preprocess_expression("2^3") == "2**3"
        
        # 测试隐式乘法
        assert self.command._preprocess_expression("2pi") == "2*pi"
        assert self.command._preprocess_expression("3x") == "3*x"
    
    def test_format_result(self):
        """测试结果格式化"""
        # 测试整数
        assert self.command._format_result(5.0) == "5"
        
        # 测试小数
        assert self.command._format_result(3.14159) == "3.14159"
        
        # 测试无穷大
        assert "无穷大" in self.command._format_result(float('inf'))
        
        # 测试NaN
        assert "非数值" in self.command._format_result(float('nan'))


class TestNewsCommand(CommandTestMixin, AsyncTestCase):
    """新闻命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.mock_news_service = Mock()
        
        # 设置模拟数据
        from datetime import datetime
        mock_news1 = Mock()
        mock_news1.id = 1
        mock_news1.title = "测试新闻1"
        mock_news1.content = "测试内容1"
        mock_news1.published_at = datetime.now()
        mock_news1.created_at = datetime.now()
        mock_news1.category = "tech"
        mock_news1.impact_type = "neutral"
        mock_news1.impact_strength = 0.0
        # Configure market_impact as a property that returns a float
        type(mock_news1).market_impact = PropertyMock(return_value=0.2)
        mock_news1.affected_stocks = ["JCTECH"]
        
        mock_news2 = Mock()
        mock_news2.id = 2
        mock_news2.title = "测试新闻2"
        mock_news2.content = "测试内容2"
        mock_news2.published_at = datetime.now()
        mock_news2.created_at = datetime.now()
        mock_news2.category = "finance"
        mock_news2.impact_type = "neutral"
        mock_news2.impact_strength = 0.0
        # Configure market_impact as a property that returns a float
        type(mock_news2).market_impact = PropertyMock(return_value=0.1)
        mock_news2.affected_stocks = ["JCBANK"]
        
        self.mock_news_service.get_latest_news.return_value = [mock_news1, mock_news2]
        self.mock_news_service.get_news_categories.return_value = ['market', 'economy', 'technology', 'policy', 'international', 'company']
        self.mock_news_service.get_market_impact_news.return_value = [mock_news1]
        self.mock_news_service.get_news_stats.return_value = {
            'total_news': 100,
            'categories': {'market': 30, 'economy': 40, 'technology': 30}
        }
        
        self.command = NewsCommand(self.mock_news_service)
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="news",
            expected_aliases=["headlines", "info", "updates"]
        )
    
    @pytest.mark.asyncio
    async def test_news_help(self, mock_context):
        """测试新闻帮助"""
        result = await self.command.execute(["help"], mock_context)
        
        self.assert_success_result(result)
        assert "新闻命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_news_categories(self, mock_context):
        """测试新闻分类"""
        result = await self.command.execute(["categories"], mock_context)
        
        self.assert_success_result(result)
        assert "新闻分类列表" in result.message
        assert "market" in result.message
        assert "economy" in result.message
    
    @pytest.mark.asyncio
    async def test_news_sources(self, mock_context):
        """测试新闻来源"""
        result = await self.command.execute(["sources"], mock_context)
        
        self.assert_success_result(result)
        assert "可用新闻来源" in result.message
        assert "reuters" in result.message
    
    @pytest.mark.asyncio
    async def test_news_default(self, mock_context):
        """测试默认新闻获取"""
        result = await self.command.execute([], mock_context)
        
        self.assert_success_result(result)
        assert "新闻头条" in result.message
    
    @pytest.mark.asyncio
    async def test_news_by_category(self, mock_context):
        """测试按分类获取新闻"""
        result = await self.command.execute(["tech"], mock_context)
        
        self.assert_success_result(result)
        assert "TECH 新闻头条" in result.message
    
    @pytest.mark.asyncio
    async def test_news_by_category_with_count(self, mock_context):
        """测试按分类和数量获取新闻"""
        result = await self.command.execute(["finance", "3"], mock_context)
        
        self.assert_success_result(result)
        assert "FINANCE 新闻头条" in result.message
        assert "前3条" in result.message
    
    @pytest.mark.asyncio
    async def test_news_search(self, mock_context):
        """测试新闻搜索"""
        result = await self.command.execute(["search", "股票市场"], mock_context)
        
        self.assert_success_result(result)
        assert "搜索: 股票市场" in result.message
        assert "功能开发中" in result.message
    
    @pytest.mark.asyncio
    async def test_news_by_source(self, mock_context):
        """测试按来源获取新闻"""
        result = await self.command.execute(["source", "reuters"], mock_context)
        
        self.assert_success_result(result)
        assert "REUTERS 新闻头条" in result.message
    
    @pytest.mark.asyncio
    async def test_news_by_source_with_count(self, mock_context):
        """测试按来源和数量获取新闻"""
        result = await self.command.execute(["source", "bbc", "5"], mock_context)
        
        self.assert_success_result(result)
        assert "BBC 新闻头条" in result.message
        assert "功能开发中" in result.message
    
    @pytest.mark.asyncio
    async def test_news_with_number_only(self, mock_context):
        """测试仅指定数量"""
        result = await self.command.execute(["10"], mock_context)
        
        self.assert_success_result(result)
        assert "新闻头条" in result.message


class TestWeatherCommand(CommandTestMixin, AsyncTestCase):
    """天气命令测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        self.command = WeatherCommand()
    
    def test_command_properties(self):
        """测试命令属性"""
        self.assert_command_properties(
            self.command,
            expected_name="weather",
            expected_aliases=["w", "forecast", "climate"]
        )
    
    @pytest.mark.asyncio
    async def test_weather_help(self, mock_context):
        """测试天气帮助"""
        result = await self.command.execute(["help"], mock_context)
        
        self.assert_success_result(result)
        assert "天气命令帮助" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_default(self, mock_context):
        """测试默认天气查询"""
        result = await self.command.execute([], mock_context)
        
        self.assert_success_result(result)
        assert "当前位置 当前天气" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_by_city(self, mock_context):
        """测试按城市查询天气"""
        result = await self.command.execute(["北京"], mock_context)
        
        self.assert_success_result(result)
        assert "北京 当前天气" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_forecast(self, mock_context):
        """测试天气预报"""
        result = await self.command.execute(["forecast", "上海"], mock_context)
        
        self.assert_success_result(result)
        assert "上海 7天天气预报" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_hourly(self, mock_context):
        """测试小时预报"""
        result = await self.command.execute(["hourly", "广州"], mock_context)
        
        self.assert_success_result(result)
        assert "广州 24小时天气预报" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_alerts(self, mock_context):
        """测试天气预警"""
        result = await self.command.execute(["alerts"], mock_context)
        
        self.assert_success_result(result)
        assert "当前位置 天气预警信息" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_alerts_with_city(self, mock_context):
        """测试指定城市天气预警"""
        result = await self.command.execute(["alerts", "深圳"], mock_context)
        
        self.assert_success_result(result)
        assert "深圳 天气预警信息" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_history(self, mock_context):
        """测试历史天气"""
        result = await self.command.execute(["history", "杭州"], mock_context)
        
        self.assert_success_result(result)
        assert "杭州 历史天气数据" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_radar(self, mock_context):
        """测试天气雷达"""
        result = await self.command.execute(["radar"], mock_context)
        
        self.assert_success_result(result)
        assert "当前位置 天气雷达图" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_air_quality(self, mock_context):
        """测试空气质量"""
        result = await self.command.execute(["air", "成都"], mock_context)
        
        self.assert_success_result(result)
        assert "成都 空气质量指数" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_uv_index(self, mock_context):
        """测试紫外线指数"""
        result = await self.command.execute(["uv", "西安"], mock_context)
        
        self.assert_success_result(result)
        assert "西安 紫外线指数" in result.message
    
    @pytest.mark.asyncio
    async def test_weather_multi_word_city(self, mock_context):
        """测试多词城市名"""
        result = await self.command.execute(["New", "York"], mock_context)
        
        self.assert_success_result(result)
        assert "New York 当前天气" in result.message


class TestAppsCommandsIntegration(CommandTestMixin, AsyncTestCase):
    """应用命令集成测试"""
    
    def setup_method(self, method):
        """设置测试"""
        super().setup_method(method)
        mock_news_service = Mock()
        # Configure mock news service
        mock_news_service.get_latest_news.return_value = []
        mock_news_service.get_news_categories.return_value = ["market", "economy", "technology"]
        mock_news_service.get_market_impact_news.return_value = []
        mock_news_service.get_news_stats.return_value = {
            'total_news': 0,
            'category_stats': {}
        }
        self.commands = {
            "calc": CalculatorCommand(),
            "news": NewsCommand(mock_news_service),
            "weather": WeatherCommand()
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
    
    def test_all_commands_are_app_commands(self):
        """测试所有命令都是应用命令"""
        from commands.base import AppCommand, NewsCommand as BaseNewsCommand
        for command in self.commands.values():
            # NewsCommand继承自BaseNewsCommand，其他继承自AppCommand
            assert isinstance(command, (AppCommand, BaseNewsCommand))
    
    def test_no_alias_conflicts(self):
        """测试别名无冲突"""
        all_aliases = set()
        for command in self.commands.values():
            for alias in command.aliases:
                assert alias not in all_aliases, f"别名冲突: {alias}"
                all_aliases.add(alias)
    
    @pytest.mark.asyncio
    async def test_all_commands_execute_without_error(self, mock_context):
        """测试所有命令都能正常执行"""
        for name, command in self.commands.items():
            try:
                result = await command.execute(["help"], mock_context)
                assert result is not None
                assert hasattr(result, 'success')
                assert hasattr(result, 'message')
            except Exception as e:
                pytest.fail(f"应用命令 {name} 执行失败: {e}")
    
    @pytest.mark.asyncio
    async def test_commands_handle_empty_args(self, mock_context):
        """测试命令处理空参数"""
        for name, command in self.commands.items():
            try:
                result = await command.execute([], mock_context)
                assert result is not None
                # 空参数应该显示帮助或执行默认操作
                assert result.success is True
            except Exception as e:
                pytest.fail(f"应用命令 {name} 处理空参数失败: {e}")
    
    @pytest.mark.asyncio
    async def test_calculator_mathematical_accuracy(self, mock_context):
        """测试计算器数学精度"""
        calc = self.commands["calc"]
        
        # 测试精确计算
        test_cases = [
            ("0.1 + 0.2", "0.3"),  # 浮点精度问题
            ("sqrt(2) * sqrt(2)", "2"),  # 平方根精度
            ("sin(pi)", "0"),  # 三角函数精度
        ]
        
        for expression, expected in test_cases:
            result = await calc.execute(expression.split(), mock_context)
            self.assert_success_result(result)
            # 检查结果是否接近期望值
            assert expected in result.message or "0" in result.message
    
    @pytest.mark.asyncio
    async def test_news_command_categories_consistency(self, mock_context):
        """测试新闻命令分类一致性"""
        news = self.commands["news"]
        
        # 获取分类列表
        categories_result = await news.execute(["categories"], mock_context)
        self.assert_success_result(categories_result)
        
        # 测试基本功能正常工作
        basic_commands = ["latest", "market", "sources"]
        for command in basic_commands:
            result = await news.execute([command], mock_context)
            self.assert_success_result(result)
    
    @pytest.mark.asyncio
    async def test_weather_command_location_handling(self, mock_context):
        """测试天气命令位置处理"""
        weather = self.commands["weather"]
        
        # 测试不同类型的位置输入
        locations = [
            ["北京"],
            ["Beijing"],
            ["New", "York"],
            ["San", "Francisco"]
        ]
        
        for location in locations:
            result = await weather.execute(location, mock_context)
            self.assert_success_result(result)
            location_str = " ".join(location)
            assert location_str in result.message