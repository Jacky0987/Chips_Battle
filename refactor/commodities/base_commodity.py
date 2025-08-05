"""
大宗商品基础类
所有商品类型的抽象基类
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random
import json


class BaseCommodity(ABC):
    """大宗商品基础抽象类"""
    
    def __init__(self, symbol, name, current_price, currency="USD", 
                 volatility=0.02, tick_size=0.01, contract_size=1):
        self.symbol = symbol
        self.name = name
        self.current_price = current_price
        self.currency = currency
        self.volatility = volatility
        self.tick_size = tick_size  # 最小价格变动单位
        self.contract_size = contract_size  # 合约规模
        self.price_history = [current_price] * 20
        self.last_updated = datetime.now()
        
        # 交易相关属性
        self.bid_price = current_price - tick_size
        self.ask_price = current_price + tick_size
        self.spread = self.ask_price - self.bid_price
        
        # 市场数据
        self.volume_24h = 0
        self.high_24h = current_price
        self.low_24h = current_price
        self.change_24h = 0.0
        self.change_24h_pct = 0.0
        
    @abstractmethod
    def update_price(self):
        """更新价格 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_trading_hours(self):
        """获取交易时间 - 子类必须实现"""
        pass
    
    @abstractmethod
    def calculate_margin_required(self, quantity, leverage=1):
        """计算所需保证金 - 子类必须实现"""
        pass
    
    def _simulate_price_movement(self):
        """模拟价格波动"""
        # 使用几何布朗运动模拟价格
        dt = 1/24/60  # 1分钟间隔
        drift = 0.0001  # 微小趋势
        
        # 随机价格变动
        random_change = random.gauss(0, self.volatility * (dt ** 0.5))
        price_change = self.current_price * (drift * dt + random_change)
        
        # 更新价格
        new_price = max(self.current_price + price_change, self.tick_size)
        self._update_price_data(new_price)
        
        return new_price
    
    def _update_price_data(self, new_price):
        """更新价格相关数据"""
        old_price = self.current_price
        self.current_price = round(new_price, len(str(self.tick_size).split('.')[-1]))
        
        # 更新买卖价差
        spread_half = self.tick_size * random.uniform(0.5, 2.0)
        self.bid_price = self.current_price - spread_half
        self.ask_price = self.current_price + spread_half
        self.spread = self.ask_price - self.bid_price
        
        # 更新历史价格
        self.price_history.append(self.current_price)
        if len(self.price_history) > 100:
            self.price_history.pop(0)
        
        # 更新24小时数据
        if len(self.price_history) >= 2:
            self.change_24h = self.current_price - self.price_history[0]
            self.change_24h_pct = (self.change_24h / self.price_history[0]) * 100
            self.high_24h = max(self.price_history[-24:])
            self.low_24h = min(self.price_history[-24:])
        
        # 模拟成交量
        volume_factor = abs(self.change_24h_pct) / 100 + 0.1
        self.volume_24h = int(random.uniform(1000000, 10000000) * volume_factor)
        
        self.last_updated = datetime.now()
    
    def get_price_info(self):
        """获取价格信息"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price,
            'bid': self.bid_price,
            'ask': self.ask_price,
            'spread': self.spread,
            'currency': self.currency,
            'change_24h': self.change_24h,
            'change_24h_pct': self.change_24h_pct,
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'volume_24h': self.volume_24h,
            'last_updated': self.last_updated.isoformat()
        }
    
    def get_technical_indicators(self, period=20):
        """计算技术指标"""
        if len(self.price_history) < period:
            return {}
        
        prices = self.price_history[-period:]
        
        # 移动平均线
        sma = sum(prices) / len(prices)
        
        # 布林带
        std_dev = (sum([(p - sma) ** 2 for p in prices]) / len(prices)) ** 0.5
        bollinger_upper = sma + (2 * std_dev)
        bollinger_lower = sma - (2 * std_dev)
        
        # RSI
        rsi = self._calculate_rsi(prices)
        
        return {
            'sma': round(sma, len(str(self.tick_size).split('.')[-1])),
            'bollinger_upper': round(bollinger_upper, len(str(self.tick_size).split('.')[-1])),
            'bollinger_lower': round(bollinger_lower, len(str(self.tick_size).split('.')[-1])),
            'rsi': round(rsi, 2)
        }
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def is_trading_active(self):
        """检查是否在交易时间内"""
        trading_hours = self.get_trading_hours()
        current_time = datetime.now().time()
        
        if trading_hours.get('24h', False):
            return True
        
        start = trading_hours.get('start')
        end = trading_hours.get('end')
        
        if start and end:
            return start <= current_time <= end
        
        return True
    
    def format_price(self, price):
        """格式化价格显示"""
        decimals = len(str(self.tick_size).split('.')[-1]) if '.' in str(self.tick_size) else 0
        return f"{price:.{decimals}f}"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price,
            'currency': self.currency,
            'volatility': self.volatility,
            'tick_size': self.tick_size,
            'contract_size': self.contract_size,
            'price_history': self.price_history,
            'last_updated': self.last_updated.isoformat(),
            'bid_price': self.bid_price,
            'ask_price': self.ask_price,
            'volume_24h': self.volume_24h,
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'change_24h': self.change_24h,
            'change_24h_pct': self.change_24h_pct
        } 