"""
外汇交易模块
实现主要货币对的交易功能
"""

from datetime import datetime, time
import random
from .base_commodity import BaseCommodity


class ForexPair(BaseCommodity):
    """外汇货币对类"""
    
    def __init__(self, symbol, base_currency, quote_currency, current_price, 
                 volatility=0.015, pip_size=0.0001):
        name = f"{base_currency}/{quote_currency}"
        super().__init__(symbol, name, current_price, quote_currency, 
                        volatility, pip_size, 100000)  # 标准手为100,000基础货币
        
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.pip_size = pip_size
        self.pip_value = 10  # 每pip价值，美元
        
        # 外汇特有属性
        self.swap_long = random.uniform(-3.5, 2.5)  # 多头过夜利息
        self.swap_short = random.uniform(-2.5, 3.5)  # 空头过夜利息
        self.session_info = self._get_session_info()
        
    def update_price(self):
        """更新外汇价格"""
        # 考虑交易时段活跃度
        session_multiplier = self._get_session_volatility_multiplier()
        
        # 临时调整波动率
        original_volatility = self.volatility
        self.volatility *= session_multiplier
        
        # 模拟价格变动
        new_price = self._simulate_price_movement()
        
        # 恢复原始波动率
        self.volatility = original_volatility
        
        return new_price
    
    def get_trading_hours(self):
        """外汇市场24小时交易（除周末）"""
        return {
            '24h': True,
            'weekends_closed': True,
            'description': '周一早上5点至周六早上5点（北京时间）'
        }
    
    def calculate_margin_required(self, quantity, leverage=100):
        """计算外汇保证金需求"""
        contract_value = abs(quantity) * self.contract_size * self.current_price
        margin = contract_value / leverage
        return margin
    
    def calculate_pip_value(self, quantity):
        """计算点值"""
        lots = abs(quantity)
        if self.quote_currency == 'USD':
            return lots * 10  # 标准点值
        else:
            # 需要转换为账户货币
            return lots * 10 * self.current_price
    
    def calculate_profit_loss(self, entry_price, current_price, quantity, position_type='long'):
        """计算盈亏"""
        if position_type.lower() == 'long':
            price_diff = current_price - entry_price
        else:
            price_diff = entry_price - current_price
        
        pip_diff = price_diff / self.pip_size
        pip_value = self.calculate_pip_value(quantity)
        
        return pip_diff * pip_value / abs(quantity) if quantity != 0 else 0
    
    def _get_session_info(self):
        """获取交易时段信息"""
        return {
            'sydney': {'start': time(5, 0), 'end': time(14, 0), 'activity': 'low'},
            'tokyo': {'start': time(7, 0), 'end': time(16, 0), 'activity': 'medium'},
            'london': {'start': time(15, 0), 'end': time(23, 59), 'activity': 'high'},
            'new_york': {'start': time(20, 0), 'end': time(5, 0), 'activity': 'high'}
        }
    
    def _get_session_volatility_multiplier(self):
        """根据交易时段调整波动率"""
        current_time = datetime.now().time()
        
        # 伦敦和纽约重叠时段（20:00-24:00）最活跃
        if time(20, 0) <= current_time <= time(23, 59):
            return 1.5
        
        # 伦敦时段
        elif time(15, 0) <= current_time <= time(19, 59):
            return 1.3
        
        # 纽约时段
        elif time(0, 0) <= current_time <= time(5, 0):
            return 1.2
        
        # 东京时段
        elif time(7, 0) <= current_time <= time(16, 0):
            return 1.0
        
        # 悉尼时段
        elif time(5, 0) <= current_time <= time(6, 59):
            return 0.8
        
        # 市场休息时间
        else:
            return 0.5
    
    def get_current_session(self):
        """获取当前交易时段"""
        current_time = datetime.now().time()
        
        sessions = []
        for session_name, session_data in self.session_info.items():
            start = session_data['start']
            end = session_data['end']
            
            # 处理跨日的情况
            if start <= end:
                if start <= current_time <= end:
                    sessions.append(session_name)
            else:  # 跨日情况
                if current_time >= start or current_time <= end:
                    sessions.append(session_name)
        
        return sessions if sessions else ['休市']
    
    def get_market_analysis(self):
        """获取市场分析"""
        indicators = self.get_technical_indicators()
        current_sessions = self.get_current_session()
        
        # 趋势分析
        if len(self.price_history) >= 10:
            recent_trend = self.price_history[-1] - self.price_history[-10]
            if recent_trend > 0:
                trend = "上涨"
                trend_strength = min(abs(recent_trend) / self.pip_size / 50, 5)
            else:
                trend = "下跌" 
                trend_strength = min(abs(recent_trend) / self.pip_size / 50, 5)
        else:
            trend = "震荡"
            trend_strength = 1
        
        # 支撑阻力位
        recent_prices = self.price_history[-20:]
        support = min(recent_prices)
        resistance = max(recent_prices)
        
        return {
            'symbol': self.symbol,
            'trend': trend,
            'trend_strength': round(trend_strength, 1),
            'current_sessions': current_sessions,
            'support': self.format_price(support),
            'resistance': self.format_price(resistance),
            'rsi': indicators.get('rsi', 50),
            'recommendation': self._get_trading_recommendation(indicators),
            'pip_value': self.calculate_pip_value(1),
            'swap_long': self.swap_long,
            'swap_short': self.swap_short
        }
    
    def _get_trading_recommendation(self, indicators):
        """获取交易建议"""
        rsi = indicators.get('rsi', 50)
        current_price = self.current_price
        sma = indicators.get('sma', current_price)
        
        score = 0
        
        # RSI分析
        if rsi > 70:
            score -= 2  # 超买
        elif rsi < 30:
            score += 2  # 超卖
        
        # 趋势分析
        if current_price > sma:
            score += 1
        else:
            score -= 1
        
        # 交易时段活跃度
        sessions = self.get_current_session()
        if 'london' in sessions or 'new_york' in sessions:
            score += 0.5
        
        if score >= 2:
            return "强烈买入"
        elif score >= 1:
            return "买入"
        elif score <= -2:
            return "强烈卖出"
        elif score <= -1:
            return "卖出"
        else:
            return "观望"


def create_major_forex_pairs():
    """创建主要货币对 (以JCK为核心)"""
    pairs = {
        # JCK主要货币对 - JackyCoin作为基础货币
        'JCKUSD': ForexPair('JCKUSD', 'JCK', 'USD', 1.2500, 0.015, 0.0001),  # 1 JCK = 1.25 USD
        'JCKEUR': ForexPair('JCKEUR', 'JCK', 'EUR', 1.1500, 0.016, 0.0001),  # 1 JCK = 1.15 EUR
        'JCKGBP': ForexPair('JCKGBP', 'JCK', 'GBP', 0.9800, 0.017, 0.0001),  # 1 JCK = 0.98 GBP
        'JCKJPY': ForexPair('JCKJPY', 'JCK', 'JPY', 187.50, 0.014, 0.01),    # 1 JCK = 187.5 JPY
        'JCKCHF': ForexPair('JCKCHF', 'JCK', 'CHF', 1.1200, 0.015, 0.0001),  # 1 JCK = 1.12 CHF
        'JCKAUD': ForexPair('JCKAUD', 'JCK', 'AUD', 1.8500, 0.018, 0.0001),  # 1 JCK = 1.85 AUD
        'JCKCAD': ForexPair('JCKCAD', 'JCK', 'CAD', 1.7300, 0.016, 0.0001),  # 1 JCK = 1.73 CAD
        
        # 传统主要货币对 (用于对比交易)
        'EURUSD': ForexPair('EURUSD', 'EUR', 'USD', 1.0856, 0.012, 0.0001),
        'GBPUSD': ForexPair('GBPUSD', 'GBP', 'USD', 1.2634, 0.015, 0.0001),
        'USDJPY': ForexPair('USDJPY', 'USD', 'JPY', 150.245, 0.011, 0.01),
        'USDCHF': ForexPair('USDCHF', 'USD', 'CHF', 0.8756, 0.013, 0.0001),
        'AUDUSD': ForexPair('AUDUSD', 'AUD', 'USD', 0.6534, 0.016, 0.0001),
        'USDCAD': ForexPair('USDCAD', 'USD', 'CAD', 1.3654, 0.014, 0.0001),
        
        # JCK与贵金属
        'JCKXAU': ForexPair('JCKXAU', 'JCK', 'XAU', 0.0006, 0.025, 0.000001),  # JCK对黄金
        'JCKXAG': ForexPair('JCKXAG', 'JCK', 'XAG', 0.051, 0.035, 0.00001),    # JCK对白银
    }
    
    return pairs 