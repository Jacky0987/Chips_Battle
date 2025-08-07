import json
import random
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from pathlib import Path

from dal.unit_of_work import AbstractUnitOfWork
from models.finance.currency import Currency
from core.event_bus import EventBus, TimeTickEvent


class CurrencyService:
    """货币服务 - 处理货币兑换和汇率管理"""
    
    def __init__(self, uow: AbstractUnitOfWork, event_bus: EventBus):
        self.uow = uow
        self.event_bus = event_bus
        self._logger = logging.getLogger(__name__)
        
        # 汇率波动配置
        self.volatility_config = {
            'USD': {'min_change': -0.05, 'max_change': 0.05, 'volatility': 0.02},
            'EUR': {'min_change': -0.06, 'max_change': 0.06, 'volatility': 0.025},
            'GBP': {'min_change': -0.07, 'max_change': 0.07, 'volatility': 0.03},
            'JPY': {'min_change': -0.03, 'max_change': 0.03, 'volatility': 0.015},
            'CNY': {'min_change': -0.02, 'max_change': 0.02, 'volatility': 0.01},
            'KRW': {'min_change': -0.04, 'max_change': 0.04, 'volatility': 0.02},
            'AUD': {'min_change': -0.06, 'max_change': 0.06, 'volatility': 0.025},
            'CAD': {'min_change': -0.05, 'max_change': 0.05, 'volatility': 0.02},
            'CHF': {'min_change': -0.04, 'max_change': 0.04, 'volatility': 0.018}
        }
        
        # 注册事件监听
        self.event_bus.subscribe(TimeTickEvent, self._handle_time_tick)
        
        self._logger.info("货币服务已初始化")
    
    async def initialize_currencies(self) -> bool:
        """从JSON文件初始化货币数据"""
        try:
            currencies_file = Path("data/definitions/currencies.json")
            if not currencies_file.exists():
                self._logger.error(f"货币定义文件不存在: {currencies_file}")
                return False
            
            with open(currencies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            async with self.uow:
                for currency_data in data['currencies']:
                    # 检查货币是否已存在
                    existing = self.uow.query(Currency).filter_by(
                        code=currency_data['code']
                    ).first()
                    
                    if not existing:
                        currency = Currency(
                            code=currency_data['code'],
                            name=currency_data['name'],
                            symbol=currency_data['symbol'],
                            decimal_places=currency_data['decimal_places'],
                            exchange_rate=Decimal(str(currency_data['exchange_rate'])),
                            is_active=currency_data['is_active'],
                            is_base_currency=currency_data['is_base_currency'],
                            description=currency_data['description']
                        )
                        self.uow.add(currency)
                        self._logger.info(f"添加货币: {currency.code} - {currency.name}")
                
                self.uow.commit()
                self._logger.info("货币数据初始化完成")
                return True
                
        except Exception as e:
            self._logger.error(f"初始化货币数据失败: {e}")
            return False
    
    def get_currency(self, code: str) -> Optional[Currency]:
        """根据代码获取货币"""
        try:
            with self.uow:
                return self.uow.query(Currency).filter_by(
                    code=code.upper(), is_active=True
                ).first()
        except Exception as e:
            self._logger.error(f"获取货币失败 {code}: {e}")
            return None
    
    def get_all_currencies(self) -> List[Currency]:
        """获取所有活跃货币"""
        try:
            with self.uow:
                return self.uow.query(Currency).filter_by(is_active=True).all()
        except Exception as e:
            self._logger.error(f"获取货币列表失败: {e}")
            return []
    
    def get_base_currency(self) -> Optional[Currency]:
        """获取基础货币 (JCY)"""
        try:
            with self.uow:
                return self.uow.query(Currency).filter_by(
                    is_base_currency=True, is_active=True
                ).first()
        except Exception as e:
            self._logger.error(f"获取基础货币失败: {e}")
            return None
    
    def convert_currency(self, amount: Decimal, from_code: str, to_code: str) -> Optional[Decimal]:
        """货币兑换
        
        Args:
            amount: 金额
            from_code: 源货币代码
            to_code: 目标货币代码
            
        Returns:
            兑换后的金额
        """
        try:
            if from_code.upper() == to_code.upper():
                return amount
            
            from_currency = self.get_currency(from_code)
            to_currency = self.get_currency(to_code)
            
            if not from_currency or not to_currency:
                self._logger.error(f"货币不存在: {from_code} -> {to_code}")
                return None
            
            # 先转换为基础货币 (JCY)
            jcy_amount = amount * from_currency.exchange_rate
            
            # 再转换为目标货币
            result = jcy_amount / to_currency.exchange_rate
            
            # 根据目标货币的小数位数进行四舍五入
            decimal_places = to_currency.decimal_places
            quantize_exp = Decimal('0.1') ** decimal_places
            
            return result.quantize(quantize_exp, rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self._logger.error(f"货币兑换失败 {from_code}->{to_code}: {e}")
            return None
    
    def format_amount(self, amount: Decimal, currency_code: str) -> str:
        """格式化金额显示
        
        Args:
            amount: 金额
            currency_code: 货币代码
            
        Returns:
            格式化后的金额字符串
        """
        currency = self.get_currency(currency_code)
        if not currency:
            return f"{amount} {currency_code}"
        
        # 根据小数位数格式化
        if currency.decimal_places == 0:
            formatted_amount = f"{int(amount):,}"
        else:
            format_str = f"{{:,.{currency.decimal_places}f}}"
            formatted_amount = format_str.format(float(amount))
        
        return f"{currency.symbol}{formatted_amount}"
    
    def get_exchange_rate(self, from_code: str, to_code: str) -> Optional[Decimal]:
        """获取汇率
        
        Args:
            from_code: 源货币代码
            to_code: 目标货币代码
            
        Returns:
            汇率
        """
        if from_code.upper() == to_code.upper():
            return Decimal('1.0')
        
        from_currency = self.get_currency(from_code)
        to_currency = self.get_currency(to_code)
        
        if not from_currency or not to_currency:
            return None
        
        # 计算汇率: from_currency -> JCY -> to_currency
        return from_currency.exchange_rate / to_currency.exchange_rate
    
    async def _handle_time_tick(self, event: TimeTickEvent):
        """处理时间事件，更新汇率"""
        try:
            # 每小时更新一次汇率
            if event.current_time.minute == 0:
                await self._update_exchange_rates()
        except Exception as e:
            self._logger.error(f"处理时间事件失败: {e}")
    
    async def _update_exchange_rates(self):
        """更新汇率 - 模拟市场波动"""
        try:
            async with self.uow:
                currencies = self.uow.query(Currency).filter(
                    Currency.is_active == True,
                    Currency.is_base_currency == False
                ).all()
                
                for currency in currencies:
                    config = self.volatility_config.get(currency.code, {
                        'min_change': -0.03, 'max_change': 0.03, 'volatility': 0.02
                    })
                    
                    # 生成随机波动
                    change_percent = random.uniform(
                        config['min_change'], 
                        config['max_change']
                    ) * config['volatility']
                    
                    # 应用波动
                    new_rate = currency.exchange_rate * (1 + Decimal(str(change_percent)))
                    
                    # 确保汇率在合理范围内
                    min_rate = currency.exchange_rate * Decimal('0.8')
                    max_rate = currency.exchange_rate * Decimal('1.2')
                    new_rate = max(min_rate, min(max_rate, new_rate))
                    
                    currency.exchange_rate = new_rate
                    currency.updated_at = datetime.utcnow()
                    
                    self._logger.debug(
                        f"汇率更新: {currency.code} {currency.exchange_rate:.6f} "
                        f"(变化: {change_percent:.4f}%)"
                    )
                
                self.uow.commit()
                self._logger.info("汇率更新完成")
                
        except Exception as e:
            self._logger.error(f"更新汇率失败: {e}")
    
    def get_currency_stats(self) -> Dict:
        """获取货币统计信息"""
        try:
            with self.uow:
                currencies = self.get_all_currencies()
                base_currency = self.get_base_currency()
                
                return {
                    'total_currencies': len(currencies),
                    'base_currency': base_currency.code if base_currency else None,
                    'active_currencies': [c.code for c in currencies],
                    'last_updated': datetime.utcnow().isoformat()
                }
        except Exception as e:
            self._logger.error(f"获取货币统计失败: {e}")
            return {}