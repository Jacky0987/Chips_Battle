from typing import List, Optional, Dict, Any
from dal.database import get_session
from models.apps.app import App
from models.apps.ownership import UserAppOwnership
from models.auth.user import User
from models.finance.account import Account
from core.event_bus import EventBus
from services.currency_service import CurrencyService
from decimal import Decimal
import json
import os

class AppService:
    """应用市场服务，管理应用购买和所有权"""
    
    def __init__(self, event_bus: EventBus, currency_service: CurrencyService):
        self.event_bus = event_bus
        self.currency_service = currency_service
        self._apps_cache = None
    
    def _load_app_definitions(self) -> Dict[str, Any]:
        """加载应用定义文件"""
        if self._apps_cache is None:
            apps_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'definitions', 'apps.json')
            with open(apps_file, 'r', encoding='utf-8') as f:
                self._apps_cache = json.load(f)
        return self._apps_cache
    
    def get_available_apps(self) -> List[Dict[str, Any]]:
        """获取所有可用应用"""
        app_definitions = self._load_app_definitions()
        return app_definitions.get('apps', [])
    
    def get_app_by_name(self, app_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取应用信息"""
        apps = self.get_available_apps()
        for app in apps:
            if app['name'] == app_name:
                return app
        return None
    
    def get_user_owned_apps(self, user_id: int) -> List[str]:
        """获取用户拥有的应用列表"""
        with get_session() as session:
            ownerships = session.query(UserAppOwnership).filter_by(user_id=user_id).all()
            return [ownership.app_name for ownership in ownerships]
    
    def purchase_app(self, user_id: int, app_name: str) -> Dict[str, Any]:
        """购买应用"""
        app_info = self.get_app_by_name(app_name)
        if not app_info:
            return {'success': False, 'message': f'应用 {app_name} 不存在'}
        
        # 检查用户是否已拥有该应用
        owned_apps = self.get_user_owned_apps(user_id)
        if app_name in owned_apps:
            return {'success': False, 'message': f'您已拥有应用 {app_name}'}
        
        with get_session() as session:
            # 检查用户余额
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            account = session.query(Account).filter_by(user_id=user_id, currency_code='JCC').first()
            if not account:
                return {'success': False, 'message': '用户账户不存在'}
            
            price = Decimal(str(app_info['price']))
            if account.balance < price:
                return {'success': False, 'message': f'余额不足，需要 {price} JCC'}
            
            # 扣除费用
            account.balance -= price
            
            # 创建所有权记录
            ownership = UserAppOwnership(
                user_id=user_id,
                app_name=app_name,
                purchase_price=price
            )
            session.add(ownership)
            session.commit()
            
            # 发布事件
            self.event_bus.publish('app_purchased', {
                'user_id': user_id,
                'app_name': app_name,
                'price': float(price)
            })
            
            return {
                'success': True, 
                'message': f'成功购买应用 {app_name}，花费 {price} JCC'
            }
    
    def can_use_app(self, user_id: int, app_name: str) -> bool:
        """检查用户是否可以使用指定应用"""
        app_info = self.get_app_by_name(app_name)
        if not app_info:
            return False
        
        # 免费应用可以直接使用
        if app_info.get('price', 0) == 0:
            return True
        
        # 付费应用需要检查所有权
        owned_apps = self.get_user_owned_apps(user_id)
        return app_name in owned_apps
    
    def get_app_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户应用使用统计"""
        owned_apps = self.get_user_owned_apps(user_id)
        available_apps = self.get_available_apps()
        
        total_apps = len(available_apps)
        owned_count = len(owned_apps)
        free_apps = [app for app in available_apps if app.get('price', 0) == 0]
        
        return {
            'total_apps': total_apps,
            'owned_apps': owned_count,
            'free_apps': len(free_apps),
            'owned_app_names': owned_apps
        }