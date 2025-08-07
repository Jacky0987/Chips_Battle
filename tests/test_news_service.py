import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from services.news_service import NewsService

class TestNewsService(unittest.TestCase):
    """NewsService 单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.event_bus = MagicMock()
        self.time_service = MagicMock()
        self.time_service.get_current_time.return_value = datetime.now()
        
        # 创建服务实例
        self.news_service = NewsService(self.event_bus, self.time_service)
        
        # 模拟新闻模板数据
        self.mock_templates = {
            'templates': {
                'market': [
                    {
                        'title': '{company}股价{direction}{percentage}%',
                        'content': '{company}今日股价{direction}{percentage}%，{reason}。',
                        'impact_type': 'market',
                        'variables': ['company', 'direction', 'percentage', 'reason']
                    }
                ],
                'economy': [
                    {
                        'title': '经济指标{direction}',
                        'content': '最新经济数据显示{indicator}{direction}。',
                        'impact_type': 'economy',
                        'variables': ['direction', 'indicator']
                    }
                ]
            },
            'variables': {
                'company': ['JCTech', 'JCBank', 'JCEnergy'],
                'direction': ['上涨', '下跌'],
                'percentage': ['5', '10', '15'],
                'reason': ['市场看好', '业绩良好', '政策利好']
            }
        }
    
    @patch.object(NewsService, '_load_news_templates')
    def test_load_news_templates(self, mock_load):
        """测试加载新闻模板"""
        mock_load.return_value = self.mock_templates
        
        result = self.news_service._load_news_templates()
        
        self.assertEqual(result, self.mock_templates)
        mock_load.assert_called_once()

    def test_fill_news_template(self):
        """测试填充新闻模板"""
        template_str = '{company}股价{direction}{percentage}%'
        
        with patch.object(self.news_service, '_load_news_templates') as mock_load:
            mock_load.return_value = self.mock_templates
            
            def mock_random_choice(choices):
                if 'JCTech' in choices:
                    return 'JCTech'
                if '上涨' in choices:
                    return '上涨'
                if '5' in choices:
                    return '5'
                return choices[0]

            with patch('random.choice', side_effect=mock_random_choice):
                result = self.news_service._fill_template(template_str, 'market')
                self.assertEqual(result, 'JCTech股价上涨5%')

    @patch('services.news_service.NewsService._create_news')
    @patch('services.news_service.NewsService._get_random_stock')
    @patch('services.news_service.NewsService._load_news_templates')
    def test_generate_random_news(self, mock_load, mock_get_random_stock, mock_create_news):
        """测试生成随机新闻"""
        mock_load.return_value = self.mock_templates
        
        mock_stock = MagicMock()
        mock_stock.name = "TestStock"
        mock_stock.ticker = "TST"
        mock_get_random_stock.return_value = mock_stock

        # Correctly mock random.choice to return values from the provided lists
        def random_choice_side_effect(choices):
            if isinstance(choices, list) and 'market' in choices:
                return 'market' # news_type
            elif isinstance(choices, list) and self.mock_templates['templates']['market'][0] in choices:
                return self.mock_templates['templates']['market'][0] # template
            elif isinstance(choices, list) and 'JCTech' in choices:
                return 'JCTech'
            elif isinstance(choices, list) and '上涨' in choices:
                return '上涨'
            elif isinstance(choices, list) and '5' in choices:
                return '5'
            elif isinstance(choices, list) and '市场看好' in choices:
                return '市场看好'
            return choices[0]

        with patch('random.choice', side_effect=random_choice_side_effect):
            self.news_service._generate_random_news()

        mock_create_news.assert_called_once()

    @patch('services.news_service.get_session')
    def test_get_market_impact_news(self, mock_session):
        """测试获取有市场影响的新闻"""
        mock_news = MagicMock()
        mock_news.impact_type = 'market'
        mock_news.published_at = datetime.now()
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_news]
        
        result = self.news_service.get_market_impact_news()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].impact_type, 'market')

    @patch.object(NewsService, '_create_news')
    def test_on_time_tick(self, mock_create_news):
        """测试时间滴答事件处理"""
        with patch('random.random', return_value=0.1): # 20% chance
            with patch.object(self.news_service, '_generate_random_news', return_value=MagicMock()) as mock_generate:
                self.news_service._on_time_tick({'tick_count': 1})
                mock_generate.assert_called_once()

        with patch('random.random', return_value=0.3): # Not 20% chance
            with patch.object(self.news_service, '_generate_random_news', return_value=MagicMock()) as mock_generate:
                mock_generate.reset_mock()
                self.news_service._on_time_tick({'tick_count': 2})
                mock_generate.assert_not_called()

    @patch('services.news_service.get_session')
    def test_get_latest_news(self, mock_session):
        """测试获取最新新闻"""
        mock_news = MagicMock()
        mock_news.title = '测试新闻'
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_news]
        
        result = self.news_service.get_latest_news(limit=5)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, '测试新闻')
    
    @patch('services.news_service.get_session')
    def test_get_news_by_id(self, mock_session):
        """测试根据ID获取新闻"""
        mock_news = MagicMock()
        mock_news.id = 1
        mock_news.title = '测试新闻'
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = mock_news
        
        result = self.news_service.get_news_by_id(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
    
    @patch.object(NewsService, '_load_news_templates')
    def test_get_news_categories(self, mock_load):
        """测试获取新闻分类"""
        mock_load.return_value = self.mock_templates
        
        result = self.news_service.get_news_categories()
        
        self.assertIn('market', result)
        self.assertIn('economy', result)
    
    @patch('services.news_service.get_session')
    def test_get_news_stats(self, mock_session):
        """测试获取新闻统计"""
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.count.return_value = 10
        
        result = self.news_service.get_news_stats()
        
        self.assertIn('total_news', result)
        self.assertEqual(result['total_news'], 10)
    
    @patch.object(NewsService, '_generate_random_news')
    @patch.object(NewsService, '_create_news')
    def test_on_time_tick_creates_news(self, mock_create, mock_generate):
        """测试时间滴答事件处理"""
        mock_generate.return_value = {
            'title': '测试新闻',
            'content': '测试内容',
            'category': 'market',
            'impact_type': 'market',
            'impact_strength': 0.1
        }
        
        with patch('random.random', return_value=0.05):  # 触发新闻生成
            self.news_service._on_time_tick({'tick_count': 1})
            
            mock_generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()