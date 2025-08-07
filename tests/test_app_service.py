import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from services.app_service import AppService

class TestAppService(unittest.TestCase):
    """AppService 单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.event_bus = MagicMock()
        self.currency_service = MagicMock()
        
        # 创建服务实例
        self.app_service = AppService(self.event_bus, self.currency_service)
        
        # 模拟应用数据
        self.mock_apps = {
            'apps': [
                {
                    'name': 'calculator',
                    'display_name': '计算器',
                    'price': 0,
                    'category': 'productivity'
                },
                {
                    'name': 'weather',
                    'display_name': '天气预报',
                    'price': 10,
                    'category': 'utility'
                }
            ]
        }
    
    @patch('services.app_service.get_session')
    @patch.object(AppService, '_load_app_definitions')
    def test_load_app_definitions(self, mock_load, mock_session):
        """测试加载应用定义"""
        mock_load.return_value = self.mock_apps
        
        result = self.app_service._load_app_definitions()
        
        self.assertEqual(result, self.mock_apps)
        mock_load.assert_called_once()
    
    @patch.object(AppService, '_load_app_definitions')
    def test_get_available_apps(self, mock_load):
        """测试获取可用应用"""
        mock_load.return_value = self.mock_apps
        
        result = self.app_service.get_available_apps()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'calculator')
        self.assertEqual(result[1]['name'], 'weather')
    
    @patch('services.app_service.get_session')
    def test_get_user_owned_apps(self, mock_session):
        """测试获取用户拥有的应用"""
        # 模拟数据库查询结果
        mock_ownership = MagicMock()
        mock_ownership.app_name = 'calculator'
        
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.all.return_value = [mock_ownership]
        
        result = self.app_service.get_user_owned_apps(1)
        
        self.assertEqual(result, ['calculator'])
    
    @patch.object(AppService, 'get_user_owned_apps')
    @patch.object(AppService, 'get_app_by_name')
    def test_can_use_app_free(self, mock_get_app, mock_owned_apps):
        """测试免费应用使用权限"""
        mock_get_app.return_value = {'name': 'calculator', 'price': 0}
        mock_owned_apps.return_value = []
        
        result = self.app_service.can_use_app(1, 'calculator')
        
        self.assertTrue(result)
    
    @patch.object(AppService, 'get_user_owned_apps')
    @patch.object(AppService, 'get_app_by_name')
    def test_can_use_app_owned(self, mock_get_app, mock_owned_apps):
        """测试已拥有付费应用使用权限"""
        mock_get_app.return_value = {'name': 'weather', 'price': 10}
        mock_owned_apps.return_value = ['weather']
        
        result = self.app_service.can_use_app(1, 'weather')
        
        self.assertTrue(result)
    
    @patch.object(AppService, 'get_user_owned_apps')
    @patch.object(AppService, 'get_app_by_name')
    def test_can_use_app_not_owned(self, mock_get_app, mock_owned_apps):
        """测试未拥有付费应用使用权限"""
        mock_get_app.return_value = {'name': 'weather', 'price': 10}
        mock_owned_apps.return_value = []
        
        result = self.app_service.can_use_app(1, 'weather')
        
        self.assertFalse(result)
    
    @patch.object(AppService, 'get_user_owned_apps')
    @patch.object(AppService, 'get_available_apps')
    def test_get_app_usage_stats(self, mock_available, mock_owned):
        """测试获取应用使用统计"""
        mock_available.return_value = self.mock_apps['apps']
        mock_owned.return_value = ['calculator']
        
        result = self.app_service.get_app_usage_stats(1)
        
        self.assertEqual(result['total_apps'], 2)
        self.assertEqual(result['owned_apps'], 1)
        self.assertEqual(result['free_apps'], 1)
        self.assertEqual(result['ownership_rate'], 50.0)

if __name__ == '__main__':
    unittest.main()