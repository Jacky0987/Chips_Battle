import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal

from services.stock_service import StockService
from models.stock.stock import Stock
from models.stock.portfolio import Portfolio, PortfolioItem
from models.finance.account import Account

class TestStockService(unittest.IsolatedAsyncioTestCase):
    """StockService 单元测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.uow = AsyncMock()
        self.uow.session = MagicMock()
        self.uow.session.execute = AsyncMock()
        self.uow.__aenter__.return_value = self.uow
        self.uow.__aexit__.return_value = None
        self.event_bus = MagicMock()
        self.time_service = MagicMock()
        self.currency_service = MagicMock()
        self.time_service.get_game_time.return_value.current_time = datetime.now()
        
        # 创建服务实例
        self.stock_service = StockService(self.uow, self.event_bus, self.currency_service, self.time_service)
        
        # 模拟股票定义数据
        self.mock_stock_definitions = {
            'stocks': [
                {
                    'ticker': 'JCTECH',
                    'name': 'JC科技',
                    'sector': 'technology',
                    'ipo_price': '100.0',
                    'current_price': '100.0',
                    'market_cap': '1000000000',
                    'volatility': '0.02',
                    'description': ''
                },
                {
                    'ticker': 'JCBANK',
                    'name': 'JC银行',
                    'sector': 'finance',
                    'ipo_price': '50.0',
                    'current_price': '50.0',
                    'market_cap': '2000000000',
                    'volatility': '0.015',
                    'description': ''
                }
            ]
        }

    @patch.object(StockService, '_load_stock_definitions')
    def test_load_stock_definitions(self, mock_load):
        """测试加载股票定义"""
        mock_load.return_value = self.mock_stock_definitions
        
        result = self.stock_service._load_stock_definitions()
        
        self.assertEqual(result, self.mock_stock_definitions)
        mock_load.assert_called_once()

    async def test_initialize_stocks(self):
        """测试初始化股票数据"""
        
        # Mock the uow methods
        self.uow.session.execute.return_value.scalars.return_value.first.return_value = None # No existing stock
        
        with patch.object(self.stock_service, '_load_stock_definitions') as mock_load:
            mock_load.return_value = self.mock_stock_definitions
            
            await self.stock_service.initialize_stocks()
            
            # 验证数据库操作
            self.assertEqual(self.uow.add.call_count, 2)
            added_symbols = {call.args[0].symbol for call in self.uow.add.call_args_list}
            self.assertEqual(added_symbols, {'JCTECH', 'JCBANK'})
            self.uow.commit.assert_awaited_once()

    async def test_get_stock_by_ticker(self):
        """测试获取股票信息"""
        mock_stock = MagicMock()
        mock_stock.symbol = 'JCTECH'
        mock_stock.name = 'JC科技'
        mock_stock.current_price = Decimal('105.0')
        
        def execute_side_effect(stmt):
            result = MagicMock()
            result.scalars.return_value.first.return_value = mock_stock
            return result
        self.uow.session.execute.side_effect = execute_side_effect
        
        result = await self.stock_service.get_stock_by_ticker('JCTECH')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.symbol, 'JCTECH')

    async def test_get_all_stocks(self):
        """测试获取所有股票"""
        mock_stocks = [MagicMock(), MagicMock()]
        
        def execute_side_effect(stmt):
            result = MagicMock()
            result.scalars.return_value.all.return_value = mock_stocks
            return result
        self.uow.session.execute.side_effect = execute_side_effect
        
        result = await self.stock_service.get_all_stocks()
        
        self.assertEqual(len(result), 2)

    async def test_buy_stock(self):
        """测试买入股票"""
        
        # 模拟股票数据
        mock_stock = MagicMock(spec=Stock)
        mock_stock.id = 1
        mock_stock.current_price = Decimal('100.0')
        
        # 模拟用户账户
        mock_account = MagicMock(spec=Account)
        mock_account.balance = Decimal('1000.0')

        # 模拟投资组合
        def execute_side_effect(stmt):
            # A simple way to mock different query results based on the statement
            # In a real scenario, you might want to parse the statement for more robust mocking
            if "PortfolioItem" in str(stmt.compile(compile_kwargs={"literal_binds": True})) and "stock_id" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = None
                return result
            if "Stock" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = mock_stock
                return result
            if "Account" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = mock_account
                return result
            if "Portfolio" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = MagicMock(id=1)
                return result
            return MagicMock()

        self.uow.session.execute.side_effect = execute_side_effect

        result = await self.stock_service.buy_stock(
            user_id=1,
            ticker='JCTECH',
            quantity=5
        )
        
        self.assertTrue(result['success'])
        self.uow.commit.assert_awaited_once()

    async def test_sell_stock(self):
        """测试卖出股票"""
        
        # 模拟股票数据
        mock_stock = MagicMock(spec=Stock)
        mock_stock.id = 1
        mock_stock.current_price = Decimal('100.0')
        
        # 模拟用户持仓
        mock_portfolio_item = MagicMock(spec=PortfolioItem)
        mock_portfolio_item.quantity = 10
        
        # 模拟用户账户
        mock_account = MagicMock(spec=Account)
        mock_account.balance = Decimal('1000.0')

        def execute_side_effect(stmt):
            if "PortfolioItem" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = mock_portfolio_item
                return result
            if "Stock" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = mock_stock
                return result
            if "Account" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = mock_account
                return result
            if "Portfolio" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = MagicMock(id=1)
                return result
            return MagicMock()

        self.uow.session.execute.side_effect = execute_side_effect
        
        result = await self.stock_service.sell_stock(
            user_id=1,
            ticker='JCTECH',
            quantity=5
        )
        
        self.assertTrue(result['success'])
        self.uow.commit.assert_awaited_once()

    async def test_get_user_portfolio(self):
        """测试获取用户投资组合"""
        mock_stock = MagicMock(spec=Stock)
        mock_stock.symbol = 'JCTECH'
        mock_stock.name = 'JC科技'
        mock_stock.current_price = Decimal('110.0')

        mock_portfolio_item = MagicMock(spec=PortfolioItem)
        mock_portfolio_item.stock_id = 1
        mock_portfolio_item.quantity = 10
        mock_portfolio_item.average_cost = Decimal('100.0')
        
        def execute_side_effect(stmt):
            if "PortfolioItem" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.all.return_value = [mock_portfolio_item]
                return result
            if "Stock" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = mock_stock
                return result
            if "Portfolio" in str(stmt.compile(compile_kwargs={"literal_binds": True})):
                result = MagicMock()
                result.scalars.return_value.first.return_value = MagicMock(id=1)
                return result
            return MagicMock()

        self.uow.session.execute.side_effect = execute_side_effect
        
        result = await self.stock_service.get_user_portfolio(user_id=1)
        
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]['profit_loss'], 100.0)

    async def test_get_market_summary(self):
        """测试获取市场概况"""
        mock_stocks = [MagicMock(), MagicMock()]
        for i, stock in enumerate(mock_stocks):
            stock.market_cap = Decimal(1000.0 + i * 10)
            stock.sector = 'tech'
        
        def execute_side_effect(stmt):
            result = MagicMock()
            result.scalars.return_value.all.return_value = mock_stocks
            return result
        self.uow.session.execute.side_effect = execute_side_effect
        
        result = await self.stock_service.get_market_summary()
        
        self.assertIn('total_stocks', result)
        self.assertIn('total_market_cap', result)

    async def test_get_stock_price_history(self):
        """测试获取价格历史"""
        mock_history = [MagicMock(), MagicMock()]
        
        def execute_side_effect(stmt):
            result = MagicMock()
            result.scalars.return_value.all.return_value = mock_history
            return result
        self.uow.session.execute.side_effect = execute_side_effect
        
        with patch.object(self.stock_service, 'get_stock_by_ticker', new_callable=AsyncMock) as mock_get_stock:
            mock_get_stock.return_value = MagicMock(id=1)
            result = await self.stock_service.get_stock_price_history('JCTECH', days=30)
        
        self.assertEqual(len(result), 2)

    def test_calculate_new_price(self):
        """测试计算新价格"""
        mock_stock = MagicMock(spec=Stock)
        mock_stock.current_price = Decimal('100.0')
        mock_stock.volatility = Decimal('0.02')
        mock_stock.ipo_price = Decimal('100.0')
        mock_stock.sector = 'tech'

        with patch('random.gauss', return_value=0.01):
            new_price = self.stock_service._calculate_new_price(mock_stock)
            
            self.assertIsInstance(new_price, Decimal)
            self.assertGreater(new_price, 0)

    async def test_update_stock_prices_on_time_tick(self):
        """测试基于时间滴答更新股价"""
        mock_stocks = [MagicMock(spec=Stock), MagicMock(spec=Stock)]
        for i, stock in enumerate(mock_stocks):
            stock.current_price = Decimal('100.0') + i * 10
            stock.volatility = Decimal('0.02')
        
        def execute_side_effect(stmt):
            result = MagicMock()
            result.scalars.return_value.all.return_value = mock_stocks
            return result
        self.uow.session.execute.side_effect = execute_side_effect
        
        with patch.object(self.stock_service, '_calculate_new_price') as mock_calc:
            mock_calc.side_effect = [Decimal('105.0'), Decimal('115.0')]
            
            await self.stock_service._on_time_tick(MagicMock())
            
            self.uow.commit.assert_awaited_once()

    async def test_update_stock_prices_on_news(self):
        """测试基于新闻事件更新股价"""
        mock_stocks = [MagicMock(spec=Stock), MagicMock(spec=Stock)]
        
        def execute_side_effect(stmt):
            result = MagicMock()
            result.scalars.return_value.all.return_value = mock_stocks
            return result
        self.uow.session.execute.side_effect = execute_side_effect
        
        news_event = {
            'impact_type': 'market',
            'impact_strength': 0.1,
            'affected_stocks': ['JCTECH']
        }
        
        await self.stock_service._on_news_published(news_event)
        
        self.uow.commit.assert_awaited_once()

    async def test_on_time_tick(self):
        """测试时间滴答事件处理"""
        with patch.object(self.stock_service, '_update_stock_prices', new_callable=AsyncMock) as mock_update:
            await self.stock_service._on_time_tick(MagicMock())
            mock_update.assert_called_once()

    async def test_on_news_published(self):
        """测试新闻发布事件处理"""
        news_event = {
            'impact_type': 'market',
            'impact_strength': 0.1,
            'affected_stocks': []
        }
        with patch.object(self.stock_service, '_apply_news_impact', new_callable=AsyncMock) as mock_update:
            await self.stock_service._on_news_published(news_event)
            mock_update.assert_called_once_with(news_event['impact_type'], news_event['impact_strength'], news_event['affected_stocks'])

if __name__ == '__main__':
    unittest.main()