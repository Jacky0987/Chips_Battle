import unittest
from unittest.mock import Mock, patch, MagicMock
from commands.apps.market import MarketCommand

class TestMarketCommand(unittest.TestCase):
    """MarketCommand 单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.app_service = MagicMock()
        
        # 创建命令实例
        self.market_command = MarketCommand(self.app_service)
        
        # 模拟用户上下文
        self.user_context = {
            'user_id': 1,
            'username': 'testuser',
            'balance': 1000.0
        }
        
        # 模拟应用数据
        self.mock_apps = [
            {
                'id': 1, 
                'name': 'calculator', 
                'display_name': '计算器',
                'price': 10.0, 
                'category': '工具',
                'description': '简单易用的计算器应用',
                'icon': '🧮',
                'rating': 4.5,
                'version': '1.0.0',
                'developer': 'JC Team',
                'file_size': '2.5MB',
                'downloads': 1000,
                'features': ['基础计算', '科学计算'],
                'requirements': ['Windows 10+']
            },
            {
                'id': 2, 
                'name': 'weather', 
                'display_name': '天气',
                'price': 5.0, 
                'category': '生活',
                'description': '实时天气预报应用',
                'icon': '🌤️',
                'rating': 4.0,
                'version': '2.1.0',
                'developer': 'Weather Inc',
                'file_size': '5.2MB',
                'downloads': 2500,
                'features': ['实时天气', '7天预报'],
                'requirements': ['网络连接']
            }
        ]
    
    def test_name_property(self):
        """测试命令名称属性"""
        self.assertEqual(self.market_command.name, "market")
    
    def test_description_property(self):
        """测试命令描述属性"""
        self.assertEqual(self.market_command.description, "应用市场命令 - 浏览和购买应用")
    
    def test_show_home(self):
        """测试显示主页"""
        self.app_service.get_available_apps.return_value = self.mock_apps
        self.app_service.get_user_owned_apps.return_value = []
        
        result = self.market_command.execute([], self.user_context)
        
        self.assertIn("JC App Store", result)
        self.app_service.get_available_apps.assert_called_once()
        self.app_service.get_user_owned_apps.assert_called_once_with(1)
    
    def test_show_app_details(self):
        """测试显示应用详情"""
        mock_app = self.mock_apps[0]
        self.app_service.get_app_by_name.return_value = mock_app
        self.app_service.get_user_owned_apps.return_value = []
        
        result = self.market_command.execute(['app', 'calculator'], self.user_context)
        
        self.assertIn("计算器", result)
        self.assertIn("v1.0.0", result)
        self.app_service.get_app_by_name.assert_called_once_with('calculator')
    
    def test_show_app_details_not_found(self):
        """测试显示不存在应用的详情"""
        self.app_service.get_app_by_name.return_value = None
        
        result = self.market_command.execute(['app', 'nonexistent'], self.user_context)
        
        self.assertIn("不存在", result)
        self.app_service.get_app_by_name.assert_called_once_with('nonexistent')
    
    def test_browse_by_category(self):
        """测试按分类浏览"""
        result = self.market_command.execute(['category'], self.user_context)
        
        self.assertIn("分类", result)
    
    def test_browse_category_apps(self):
        """测试按分类浏览应用"""
        self.app_service.get_available_apps.return_value = self.mock_apps
        
        result = self.market_command.execute(['category', '工具'], self.user_context)
        
        self.assertIn("工具", result)
        self.app_service.get_available_apps.assert_called()
    
    def test_search_apps(self):
        """测试搜索应用"""
        self.app_service.get_available_apps.return_value = self.mock_apps
        
        result = self.market_command.execute(['search', 'calc'], self.user_context)
        
        self.assertIn("搜索结果", result)
        self.assertIn("calc", result)
        self.app_service.get_available_apps.assert_called()
    
    def test_search_apps_no_results(self):
        """测试搜索无结果"""
        self.app_service.get_available_apps.return_value = self.mock_apps
        
        result = self.market_command.execute(['search', 'nonexistent'], self.user_context)
        
        self.assertIn("没有找到包含", result)
        self.assertIn("nonexistent", result)
        self.app_service.get_available_apps.assert_called()
    
    def test_buy_app_success(self):
        """测试成功购买应用"""
        mock_result = {'success': True, 'message': '购买成功！应用已添加到您的账户'}
        self.app_service.purchase_app.return_value = mock_result
        
        result = self.market_command.execute(['buy', 'calculator'], self.user_context)
        
        self.assertIn("购买成功", result)
        self.app_service.purchase_app.assert_called_once_with(1, 'calculator')
    
    def test_buy_app_not_found(self):
        """测试购买不存在的应用"""
        mock_result = {'success': False, 'message': '应用不存在'}
        self.app_service.purchase_app.return_value = mock_result
        
        result = self.market_command.execute(['buy', 'nonexistent'], self.user_context)
        
        self.assertIn("不存在", result)
        self.app_service.purchase_app.assert_called_once_with(1, 'nonexistent')
    
    def test_buy_app_already_owned(self):
        """测试购买已拥有的应用"""
        mock_result = {'success': False, 'message': '您已拥有此应用'}
        self.app_service.purchase_app.return_value = mock_result
        
        result = self.market_command.execute(['buy', 'calculator'], self.user_context)
        
        self.assertIn("已拥有", result)
        self.app_service.purchase_app.assert_called_once_with(1, 'calculator')
    
    def test_buy_app_failed(self):
        """测试购买失败"""
        mock_result = {'success': False, 'message': '余额不足，无法购买此应用'}
        self.app_service.purchase_app.return_value = mock_result
        
        result = self.market_command.execute(['buy', 'calculator'], self.user_context)
        
        self.assertIn("余额不足", result)
        self.app_service.purchase_app.assert_called_once_with(1, 'calculator')
    
    def test_invalid_subcommand(self):
        """测试无效的子命令"""
        result = self.market_command.execute(['invalid'], self.user_context)
        
        self.assertIn("未知的子命令", result)
    
    def test_missing_app_name_for_app_command(self):
        """测试app命令缺少应用名称"""
        result = self.market_command.execute(['app'], self.user_context)
        
        self.assertIn("用法: market app", result)
    
    def test_missing_keyword_for_search_command(self):
        """测试search命令缺少关键词"""
        result = self.market_command.execute(['search'], self.user_context)
        
        self.assertIn("用法: market search", result)
    
    def test_missing_app_name_for_buy_command(self):
        """测试buy命令缺少应用名称"""
        result = self.market_command.execute(['buy'], self.user_context)
        
        self.assertIn("用法: market buy", result)

if __name__ == '__main__':
    unittest.main()