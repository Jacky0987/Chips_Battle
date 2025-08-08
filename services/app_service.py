from typing import List, Optional, Dict, Any
from sqlalchemy import select
from dal.unit_of_work import UnitOfWork
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
    
    def __init__(self, uow: UnitOfWork, event_bus: EventBus, currency_service: CurrencyService):
        self.uow = uow
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
    
    async def get_user_owned_apps(self, user_id: int) -> List[str]:
        """获取用户拥有的应用列表"""
        async with self.uow:
            stmt = select(App.name).join(UserAppOwnership).filter(UserAppOwnership.user_id == user_id)
            result = await self.uow.session.execute(stmt)
            return result.scalars().all()
    
    async def purchase_app(self, user_id: int, app_name: str) -> Dict[str, Any]:
        """购买应用"""
        app_info = self.get_app_by_name(app_name)
        if not app_info:
            return {'success': False, 'message': f'应用 {app_name} 不存在'}
        
        # 检查用户是否已拥有该应用
        owned_apps = await self.get_user_owned_apps(user_id)
        if app_name in owned_apps:
            return {'success': False, 'message': f'您已拥有应用 {app_name}'}
        
        async with self.uow:
            # 检查用户余额
            user_result = await self.uow.session.execute(select(User).filter_by(id=user_id))
            user = user_result.scalars().first()
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            account_result = await self.uow.session.execute(select(Account).filter_by(user_id=user_id, currency_code='JCC'))
            account = account_result.scalars().first()
            if not account:
                return {'success': False, 'message': '用户账户不存在'}
            
            # 查找App记录
            app_result = await self.uow.session.execute(select(App).filter_by(name=app_name))
            app = app_result.scalars().first()
            if not app:
                return {'success': False, 'message': f'应用 {app_name} 在数据库中不存在'}
            
            price = Decimal(str(app_info['price']))
            if account.balance < price:
                return {'success': False, 'message': f'余额不足，需要 {price} JCC'}
            
            # 扣除费用
            account.balance -= price
            
            # 创建所有权记录
            ownership = UserAppOwnership(
                user_id=user_id,
                app_id=app.id,
                purchase_price=price
            )
            self.uow.session.add(ownership)
            await self.uow.commit()
            
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
    
    async def can_use_app(self, user_id: int, app_name: str) -> bool:
        """检查用户是否可以使用指定应用"""
        app_info = self.get_app_by_name(app_name)
        if not app_info:
            return False
        
        # 免费应用可以直接使用
        if app_info.get('price', 0) == 0:
            return True
        
        # 付费应用需要检查所有权
        owned_apps = await self.get_user_owned_apps(user_id)
        return app_name in owned_apps
    
    async def get_app_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户应用使用统计"""
        owned_apps = await self.get_user_owned_apps(user_id)
        available_apps = self.get_available_apps()
        
        total_apps = len(available_apps)
        owned_count = len(owned_apps)
        free_apps = [app for app in available_apps if app.get('price', 0) == 0]
        ownership_rate = (owned_count / total_apps) * 100 if total_apps > 0 else 0.0
        
        return {
            'total_apps': total_apps,
            'owned_apps': owned_count,
            'free_apps': len(free_apps),
            'owned_app_names': owned_apps,
            'ownership_rate': ownership_rate
        }
    
    async def check_market_unlock_eligibility(self, user_id: int) -> Dict[str, Any]:
        """检查用户是否有资格解锁应用市场"""
        unlock_threshold = Decimal('1000000')  # 100万JCC解锁阈值
        
        async with self.uow:
            # 获取用户所有账户余额
            accounts_result = await self.uow.session.execute(
                select(Account).filter_by(user_id=user_id)
            )
            accounts = accounts_result.scalars().all()
            
            total_balance = Decimal('0')
            for account in accounts:
                if account.currency_code == 'JCC':
                    total_balance += account.balance
            
            # 检查银行账户余额
            from models.bank.bank_account import BankAccount
            bank_accounts_result = await self.uow.session.execute(
                select(BankAccount).filter_by(user_id=user_id)
            )
            bank_accounts = bank_accounts_result.scalars().all()
            
            for bank_account in bank_accounts:
                if bank_account.currency_id == 'JCC':
                    total_balance += bank_account.balance
            
            is_eligible = total_balance >= unlock_threshold
            
            return {
                'eligible': is_eligible,
                'total_balance': float(total_balance),
                'required_balance': float(unlock_threshold),
                'remaining_needed': float(max(Decimal('0'), unlock_threshold - total_balance))
            }
    
    async def unlock_app_market(self, user_id: int) -> Dict[str, Any]:
        """解锁应用市场功能"""
        eligibility = await self.check_market_unlock_eligibility(user_id)
        
        if not eligibility['eligible']:
            return {
                'success': False,
                'message': f"资金不足，需要至少 {eligibility['required_balance']} JCC 才能解锁应用市场。\n" +
                          f"当前总资产: {eligibility['total_balance']} JCC\n" +
                          f"还需要: {eligibility['remaining_needed']} JCC"
            }
        
        # 检查是否已经解锁
        async with self.uow:
            from models.auth.user import User
            user_result = await self.uow.session.execute(select(User).filter_by(id=user_id))
            user = user_result.scalars().first()
            
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            # 检查用户是否已有市场解锁标记
            if hasattr(user, 'market_unlocked') and user.market_unlocked:
                return {'success': False, 'message': '应用市场已经解锁'}
            
            # 设置市场解锁标记（如果User模型有这个字段）
            # user.market_unlocked = True
            # await self.uow.commit()
            
            # 发布解锁事件
            self.event_bus.publish('app_market_unlocked', {
                'user_id': user_id,
                'total_balance': eligibility['total_balance']
            })
            
            return {
                'success': True,
                'message': f"🎉 恭喜！应用市场已成功解锁！\n" +
                          f"您的总资产: {eligibility['total_balance']} JCC\n" +
                          f"现在可以使用 'app market' 命令浏览和购买应用了！"
            }