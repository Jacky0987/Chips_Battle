import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from services.stock_service import StockService
from services.currency_service import CurrencyService

class TestStockService(unittest.TestCase):
    """StockService 单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.event_bus = MagicMock()
        self.time_service = MagicMock()
        self.time_service.get_current_time.return_value = datetime.now()
        
        # 创建服务实例
        self.stock_service = StockService(self.event_bus, self.time_service)
        
        # 模拟股票定义数据
        self.mock_stock_definitions = {
            'stocks': {
                'JCTECH': {
                    'name': 'JC科技',
                    'symbol': 'JCTECH',
                    'sector': 'technology',
                    'initial_price': 100.0,
                    'volatility': 0.02,
                    'market_cap': 1000000000
                },
                'JCBANK': {
                    'name': 'JC银行',
                    'symbol': 'JCBANK',
                    'sector': 'finance',
                    'initial_price': 50.0,
                    'volatility': 0.015,
                    'market_cap': 2000000000
                }
            },
            'sectors': {
                'technology': '科技',
                'finance': '金融'
            }
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
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        with patch.object(self.stock_service, '_load_stock_definitions') as mock_load:
            mock_load.return_value = self.mock_stock_definitions
            
            self.stock_service.initialize_stocks()
            
            # 验证数据库操作
            self.assertTrue(mock_session_instance.add.called)
            mock_session_instance.commit.assert_called_once()
    
    @patch('services.stock_service.get_session')
    def test_get_stock_info(self, mock_session):
        """测试获取股票信息"""
        mock_stock = MagicMock()
        mock_stock.symbol = 'JCTECH'
        mock_stock.name = 'JC科技'
        mock_stock.current_price = 105.0
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_stock
        
        result = self.stock_service.get_stock_info('JCTECH')
        
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
        mock_stock = MagicMock()
        mock_stock.current_price = 100.0
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_stock
        
        # 模拟用户账户
        mock_account = MagicMock()
        mock_account.balance = 1000.0
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_account
        
        result = self.stock_service.buy_stock(
            user_id=1,
            symbol='JCTECH',
            quantity=5
        )
        
        self.assertTrue(result)
        mock_session_instance.commit.assert_called_once()
    
    @patch('services.stock_service.get_session')
    def test_sell_stock(self, mock_session):
        """测试卖出股票"""
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # 模拟股票数据
        mock_stock = MagicMock()
        mock_stock.current_price = 100.0
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_stock
        
        # 模拟用户持仓
        mock_holding = MagicMock()
        mock_holding.quantity = 10
        mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_holding
        
        result = self.stock_service.sell_stock(
            user_id=1,
            symbol='JCTECH',
            quantity=5
        )
        
        self.assertTrue(result)
        mock_session_instance.commit.assert_called_once()
    
    @patch('services.stock_service.get_session')
    def test_get_user_portfolio(self, mock_session):
        """测试获取用户投资组合"""
        mock_holdings = [MagicMock(), MagicMock()]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.all.return_value = mock_holdings
        
        result = self.stock_service.get_user_portfolio(user_id=1)
        
        self.assertEqual(len(result), 2)
    
    @patch('services.stock_service.get_session')
    def test_get_market_overview(self, mock_session):
        """测试获取市场概况"""
        mock_stocks = [MagicMock(), MagicMock()]
        for i, stock in enumerate(mock_stocks):
            stock.current_price = 100.0 + i * 10
            stock.previous_price = 95.0 + i * 10
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        result = self.stock_service.get_market_overview()
        
        self.assertIn('total_stocks', result)
        self.assertIn('market_trend', result)
    
    @patch('services.stock_service.get_session')
    def test_get_stock_list(self, mock_session):
        """测试获取股票列表"""
        mock_stocks = [MagicMock(), MagicMock()]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        result = self.stock_service.get_stock_list()
        
        self.assertEqual(len(result), 2)
    
    @patch('services.stock_service.get_session')
    def test_get_price_history(self, mock_session):
        """测试获取价格历史"""
        mock_history = [MagicMock(), MagicMock()]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = mock_history
        
        result = self.stock_service.get_price_history('JCTECH', days=30)
        
        self.assertEqual(len(result), 2)
    
    def test_calculate_new_price(self):
        """测试计算新价格"""
        current_price = 100.0
        volatility = 0.02
        
        with patch('random.gauss', return_value=0.01):
            new_price = self.stock_service._calculate_new_price(current_price, volatility)
            
            self.assertIsInstance(new_price, float)
            self.assertGreater(new_price, 0)
    
    @patch('services.stock_service.get_session')
    def test_update_stock_prices_on_time_tick(self, mock_session):
        """测试基于时间滴答更新股价"""
        mock_stocks = [MagicMock(), MagicMock()]
        for i, stock in enumerate(mock_stocks):
            stock.current_price = 100.0 + i * 10
            stock.volatility = 0.02
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        with patch.object(self.stock_service, '_calculate_new_price') as mock_calc:
            mock_calc.side_effect = [105.0, 115.0]
            
            self.stock_service._update_stock_prices_on_time_tick()
            
            mock_session_instance.commit.assert_called_once()
    
    @patch('services.stock_service.get_session')
    def test_update_stock_prices_on_news(self, mock_session):
        """测试基于新闻事件更新股价"""
        mock_stocks = [MagicMock(), MagicMock()]
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.all.return_value = mock_stocks
        
        news_event = {
            'impact_type': 'market',
            'impact_strength': 0.1,
            'affected_stocks': ['JCTECH']
        }
        
        self.stock_service._update_stock_prices_on_news(news_event)
        
        mock_session_instance.commit.assert_called_once()
    
    @patch.object(StockService, '_update_stock_prices_on_time_tick')
    def test_on_time_tick(self, mock_update):
        """测试时间滴答事件处理"""
        self.stock_service.on_time_tick({'tick_count': 1})
        
        mock_update.assert_called_once()
    
    @patch.object(StockService, '_update_stock_prices_on_news')
    def test_on_news_published(self, mock_update):
        """测试新闻发布事件处理"""
        news_event = {
            'impact_type': 'market',
            'impact_strength': 0.1
        }
        
        self.stock_service.on_news_published(news_event)
        
        mock_update.assert_called_once_with(news_event)

if __name__ == '__main__':
    unittest.main()