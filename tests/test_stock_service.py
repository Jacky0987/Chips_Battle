import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal

from services.stock_service import StockService
from models.stock.stock import Stock
from models.stock.portfolio import Portfolio, PortfolioItem
from models.finance.account import Account

class TestStockService(unittest.TestCase):
    """StockService 单元测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.event_bus = MagicMock()
        self.time_service = MagicMock()
        self.currency_service = MagicMock()
        self.time_service.get_current_time.return_value = datetime.now()
        
        # 创建服务实例
        self.stock_service = StockService(self.event_bus, self.currency_service, self.time_service)
        
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

    @patch('services.stock_service.get_session')
    def test_initialize_stocks(self, mock_session):
        """测试初始化股票数据"""
        mock_session_instance = MagicMock()
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None # No existing stock
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        with patch.object(self.stock_service, '_load_stock_definitions') as mock_load:
            mock_load.return_value = self.mock_stock_definitions
            
            self.stock_service.initialize_stocks()
            
            # 验证数据库操作
            self.assertEqual(mock_session_instance.add.call_count, 2)
            added_symbols = {call.args[0].symbol for call in mock_session_instance.add.call_args_list}
            self.assertEqual(added_symbols, {'JCTECH', 'JCBANK'})
            mock_session_instance.commit.assert_called_once()

    @patch('services.stock_service.get_session')
    def test_get_stock_by_ticker(self, mock_session):
        """测试获取股票信息"""
        mock_stock = MagicMock()
        mock_stock.symbol = 'JCTECH'
        mock_stock.name = 'JC科技'
        mock_stock.current_price = Decimal('105.0')
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_stock
        
        result = self.stock_service.get_stock_by_ticker('JCTECH')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.symbol, 'JCTECH')

    @patch('services.stock_service.get_session')
    def test_get_all_stocks(self, mock_session):
        """测试获取所有股票"""
        mock_stocks = [MagicMock(), MagicMock()]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        result = self.stock_service.get_all_stocks()
        
        self.assertEqual(len(result), 2)

    @patch('services.stock_service.get_session')
    def test_buy_stock(self, mock_session):
        """测试买入股票"""
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # 模拟股票数据
        mock_stock = MagicMock(spec=Stock)
        mock_stock.id = 1
        mock_stock.current_price = Decimal('100.0')
        
        # 模拟用户账户
        mock_account = MagicMock(spec=Account)
        mock_account.balance = Decimal('1000.0')
        
        # 模拟投资组合
        def query_side_effect(model):
            if model == Stock:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_stock))))
            if model == Account:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_account))))
            if model == PortfolioItem:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))) # No existing portfolio
            return MagicMock()

        mock_session_instance.query.side_effect = query_side_effect

        result = self.stock_service.buy_stock(
            user_id=1,
            ticker='JCTECH',
            quantity=5
        )
        
        self.assertTrue(result['success'])
        mock_session_instance.commit.assert_called_once()

    @patch('services.stock_service.get_session')
    def test_sell_stock(self, mock_session):
        """测试卖出股票"""
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
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

        def query_side_effect(model):
            if model == Stock:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_stock))))
            if model == PortfolioItem:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_portfolio_item))))
            if model == Account:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_account))))
            return MagicMock()

        mock_session_instance.query.side_effect = query_side_effect
        
        result = self.stock_service.sell_stock(
            user_id=1,
            ticker='JCTECH',
            quantity=5
        )
        
        self.assertTrue(result['success'])
        mock_session_instance.commit.assert_called_once()

    @patch('services.stock_service.get_session')
    def test_get_user_portfolio(self, mock_session):
        """测试获取用户投资组合"""
        mock_stock = MagicMock(spec=Stock)
        mock_stock.symbol = 'JCTECH'
        mock_stock.name = 'JC科技'
        mock_stock.current_price = Decimal('110.0')

        mock_portfolio_item = MagicMock(spec=PortfolioItem)
        mock_portfolio_item.stock_id = 1
        mock_portfolio_item.quantity = 10
        mock_portfolio_item.average_cost = Decimal('100.0')
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        def query_side_effect(model):
            if model == PortfolioItem:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_portfolio_item]))))
            if model == Stock:
                return MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_stock))))
            return MagicMock()

        mock_session_instance.query.side_effect = query_side_effect
        
        result = self.stock_service.get_user_portfolio(user_id=1)
        
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]['profit_loss'], 100.0)

    @patch('services.stock_service.get_session')
    def test_get_market_summary(self, mock_session):
        """测试获取市场概况"""
        mock_stocks = [MagicMock(), MagicMock()]
        for i, stock in enumerate(mock_stocks):
            stock.market_cap = Decimal(1000.0 + i * 10)
            stock.sector = 'tech'
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        result = self.stock_service.get_market_summary()
        
        self.assertIn('total_stocks', result)
        self.assertIn('total_market_cap', result)

    @patch('services.stock_service.get_session')
    def test_get_stock_price_history(self, mock_session):
        """测试获取价格历史"""
        mock_history = [MagicMock(), MagicMock()]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_history
        
        with patch.object(self.stock_service, 'get_stock_by_ticker') as mock_get_stock:
            mock_get_stock.return_value = MagicMock()
            result = self.stock_service.get_stock_price_history('JCTECH', days=30)
        
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

    @patch('services.stock_service.get_session')
    def test_update_stock_prices_on_time_tick(self, mock_session):
        """测试基于时间滴答更新股价"""
        mock_stocks = [MagicMock(spec=Stock), MagicMock(spec=Stock)]
        for i, stock in enumerate(mock_stocks):
            stock.current_price = Decimal('100.0') + i * 10
            stock.volatility = Decimal('0.02')
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        with patch.object(self.stock_service, '_calculate_new_price') as mock_calc:
            mock_calc.side_effect = [Decimal('105.0'), Decimal('115.0')]
            
            self.stock_service._on_time_tick({'tick_count': 1})
            
            mock_session_instance.commit.assert_called_once()

    @patch('services.stock_service.get_session')
    def test_update_stock_prices_on_news(self, mock_session):
        """测试基于新闻事件更新股价"""
        mock_stocks = [MagicMock(spec=Stock), MagicMock(spec=Stock)]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        news_event = {
            'impact_type': 'market',
            'impact_strength': 0.1,
            'affected_stocks': ['JCTECH']
        }
        
        self.stock_service._on_news_published(news_event)
        
        mock_session_instance.commit.assert_called_once()

    def test_on_time_tick(self):
        """测试时间滴答事件处理"""
        with patch.object(self.stock_service, '_update_stock_prices') as mock_update:
            self.stock_service._on_time_tick({'tick_count': 1})
            mock_update.assert_called_once()

    def test_on_news_published(self):
        """测试新闻发布事件处理"""
        news_event = {
            'impact_type': 'market',
            'impact_strength': 0.1
        }
        with patch.object(self.stock_service, '_apply_news_impact') as mock_update:
            self.stock_service._on_news_published(news_event)
            mock_update.assert_called_once_with(news_event['impact_type'], news_event['impact_strength'])

if __name__ == '__main__':
    unittest.main()