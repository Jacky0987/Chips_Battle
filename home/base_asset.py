"""
资产基类 - 所有投资品的基础类
"""

from abc import ABC, abstractmethod
from datetime import datetime
import random


class BaseAsset(ABC):
    """资产基类"""
    
    def __init__(self, asset_id, name, description, current_price, category, rarity="common", emoji="💎"):
        self.asset_id = asset_id
        self.name = name
        self.description = description
        self.current_price = current_price
        self.category = category
        self.rarity = rarity  # common, rare, epic, legendary
        self.emoji = emoji
        self.purchase_date = None
        self.purchase_price = 0
        self.quantity = 0
        self.last_update = datetime.now().isoformat()
        
        # 价格历史
        self.price_history = [current_price]
        self.volatility = self._get_base_volatility()
    
    @abstractmethod
    def update_price(self):
        """更新价格 - 子类必须实现"""
        pass
    
    def _get_base_volatility(self):
        """根据稀有度获取基础波动率"""
        volatility_map = {
            'common': 0.02,
            'rare': 0.05,
            'epic': 0.08,
            'legendary': 0.12
        }
        return volatility_map.get(self.rarity, 0.02)
    
    def get_value(self):
        """获取当前总价值"""
        return self.current_price * self.quantity
    
    def get_profit_loss(self):
        """获取盈亏"""
        if self.quantity == 0:
            return 0
        return (self.current_price - self.purchase_price) * self.quantity
    
    def get_profit_percentage(self):
        """获取盈亏百分比"""
        if self.purchase_price == 0:
            return 0
        return ((self.current_price - self.purchase_price) / self.purchase_price) * 100
    
    def get_rarity_info(self):
        """获取稀有度信息"""
        rarity_map = {
            'common': {'name': '普通', 'color': '⚪', 'multiplier': 1.0},
            'rare': {'name': '稀有', 'color': '🔵', 'multiplier': 1.5},
            'epic': {'name': '史诗', 'color': '🟣', 'multiplier': 2.0},
            'legendary': {'name': '传奇', 'color': '🟡', 'multiplier': 3.0}
        }
        return rarity_map.get(self.rarity, rarity_map['common'])
    
    def get_price_trend(self):
        """获取价格趋势"""
        if len(self.price_history) < 2:
            return "持平"
        
        recent_change = (self.price_history[-1] - self.price_history[-2]) / self.price_history[-2]
        if recent_change > 0.02:
            return "📈 上涨"
        elif recent_change < -0.02:
            return "📉 下跌"
        else:
            return "➡️ 持平"
    
    def get_info_display(self):
        """获取信息展示"""
        rarity_info = self.get_rarity_info()
        trend = self.get_price_trend()
        
        return f"""
{self.emoji} {self.name} {rarity_info['color']}
  类别: {self.category}
  稀有度: {rarity_info['name']}
  当前价格: ${self.current_price:,.2f}
  趋势: {trend}
  持有数量: {self.quantity}
  总价值: ${self.get_value():,.2f}
  盈亏: ${self.get_profit_loss():+,.2f} ({self.get_profit_percentage():+.1f}%)
""" 