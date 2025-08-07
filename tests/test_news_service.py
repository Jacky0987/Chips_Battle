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
    
    @patch.object(NewsService, '_load_news_templates')
    def test_generate_random_news(self, mock_load):
        """测试生成随机新闻"""
        mock_load.return_value = self.mock_templates
        
        with patch('random.choice') as mock_choice:
            # 模拟随机选择
            mock_choice.side_effect = [
                'market',  # 选择分类
                self.mock_templates['templates']['market'][0],  # 选择模板
                'JCTech',  # company
                '上涨',     # direction
                '10',      # percentage
                '市场看好'  # reason
            ]
            
            result = self.news_service._generate_random_news()
            
            self.assertIsNotNone(result)
            self.assertIn('title', result)
            self.assertIn('content', result)
    
    def test_fill_news_template(self):
        """测试填充新闻模板"""
        template = {
            'title': '{company}股价{direction}{percentage}%',
            'content': '{company}今日股价{direction}{percentage}%。'
        }
        
        variables = {
            'company': 'JCTech',
            'direction': '上涨',
            'percentage': '10'
        }
        
        result = self.news_service._fill_news_template(template, variables)
        
        self.assertEqual(result['title'], 'JCTech股价上涨10%')
        self.assertEqual(result['content'], 'JCTech今日股价上涨10%。')
    
    @patch('services.news_service.get_session')
    def test_create_news(self, mock_session):
        """测试创建新闻"""
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        result = self.news_service._create_news(
            title='测试新闻',
            content='测试内容',
            category='market'
        )
        
        # 验证数据库操作
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        self.assertIsNotNone(result)
    
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
    
    @patch('services.news_service.get_session')
    def test_get_market_impact_news(self, mock_session):
        """测试获取有市场影响的新闻"""
        mock_news = MagicMock()
        mock_news.impact_type = 'market'
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_news]
        
        result = self.news_service.get_market_impact_news()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].impact_type, 'market')
    
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
    def test_on_time_tick(self, mock_create, mock_generate):
        """测试时间滴答事件处理"""
        mock_generate.return_value = {
            'title': '测试新闻',
            'content': '测试内容',
            'category': 'market',
            'impact_type': 'market',
            'impact_strength': 0.1
        }
        
        mock_news = MagicMock()
        mock_create.return_value = mock_news
        
        with patch('random.random', return_value=0.05):  # 触发新闻生成
            self.news_service.on_time_tick({'tick_count': 1})
            
            mock_generate.assert_called_once()
            mock_create.assert_called_once()
            self.event_bus.publish.assert_called_once()

if __name__ == '__main__':
    unittest.main()