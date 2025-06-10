"""
期货交易模块
实现各种期货合约的交易功能
"""

from datetime import datetime, date, time, timedelta
import random
import calendar
from .base_commodity import BaseCommodity


class FuturesContract(BaseCommodity):
    """期货合约类"""
    
    def __init__(self, symbol, name, current_price, underlying_asset, 
                 expiry_date, contract_size, tick_size, currency="USD", 
                 volatility=0.025, margin_rate=0.1):
        super().__init__(symbol, name, current_price, currency, 
                        volatility, tick_size, contract_size)
        
        self.underlying_asset = underlying_asset
        self.expiry_date = expiry_date
        self.margin_rate = margin_rate  # 保证金比例
        self.daily_settlement = True
        
        # 期货特有属性
        self.open_interest = random.randint(10000, 500000)  # 持仓量
        self.settlement_price = current_price
        self.limit_up = current_price * 1.1  # 涨停价
        self.limit_down = current_price * 0.9  # 跌停价
        
        # 交割相关
        self.delivery_method = self._get_delivery_method()
        self.last_trading_day = self._calculate_last_trading_day()
        
    def update_price(self):
        """更新期货价格"""
        # 考虑到期日临近的影响
        days_to_expiry = (self.expiry_date - date.today()).days
        if days_to_expiry <= 0:
            return self.current_price  # 已到期
        
        # 临近到期时波动率降低
        expiry_factor = min(days_to_expiry / 30, 1.0)
        
        # 临时调整波动率
        original_volatility = self.volatility
        self.volatility *= expiry_factor
        
        # 模拟价格变动，考虑涨跌停限制
        new_price = self._simulate_price_movement()
        
        # 检查涨跌停限制
        if new_price > self.limit_up:
            new_price = self.limit_up
        elif new_price < self.limit_down:
            new_price = self.limit_down
        
        # 更新结算价（收盘时）
        if datetime.now().hour == 15:  # 假设15点结算
            self.settlement_price = new_price
            self._update_daily_limits()
        
        # 恢复原始波动率
        self.volatility = original_volatility
        
        return new_price
    
    def get_trading_hours(self):
        """获取期货交易时间"""
        return {
            'day_session': {'start': time(9, 0), 'end': time(15, 0)},
            'night_session': {'start': time(21, 0), 'end': time(2, 30)},
            'description': '日盘:9:00-15:00, 夜盘:21:00-2:30（次日）'
        }
    
    def calculate_margin_required(self, quantity, leverage=1):
        """计算期货保证金需求"""
        contract_value = abs(quantity) * self.contract_size * self.current_price
        margin = contract_value * self.margin_rate
        return margin
    
    def calculate_daily_pnl(self, entry_price, quantity, position_type='long'):
        """计算当日盈亏（基于结算价）"""
        if position_type.lower() == 'long':
            price_diff = self.settlement_price - entry_price
        else:
            price_diff = entry_price - self.settlement_price
        
        return price_diff * self.contract_size * quantity
    
    def calculate_position_value(self, quantity):
        """计算持仓价值"""
        return quantity * self.contract_size * self.current_price
    
    def get_contract_info(self):
        """获取合约详细信息"""
        days_to_expiry = (self.expiry_date - date.today()).days
        
        return {
            'symbol': self.symbol,
            'name': self.name,
            'underlying_asset': self.underlying_asset,
            'current_price': self.current_price,
            'settlement_price': self.settlement_price,
            'contract_size': self.contract_size,
            'tick_size': self.tick_size,
            'margin_rate': f"{self.margin_rate*100:.1f}%",
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d'),
            'days_to_expiry': max(days_to_expiry, 0),
            'last_trading_day': self.last_trading_day.strftime('%Y-%m-%d'),
            'delivery_method': self.delivery_method,
            'limit_up': self.limit_up,
            'limit_down': self.limit_down,
            'open_interest': self.open_interest,
            'volume_24h': self.volume_24h
        }
    
    def _get_delivery_method(self):
        """获取交割方式"""
        if self.underlying_asset in ['原油', '黄金', '白银', '铜', '铝']:
            return '实物交割'
        elif self.underlying_asset in ['股指', '国债']:
            return '现金交割'
        else:
            return '实物交割'
    
    def _calculate_last_trading_day(self):
        """计算最后交易日"""
        # 通常是到期月份的第三个周五
        year = self.expiry_date.year
        month = self.expiry_date.month
        
        # 找到该月第一个周五
        first_day = date(year, month, 1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        
        # 第三个周五
        third_friday = first_friday + timedelta(weeks=2)
        
        return third_friday
    
    def _update_daily_limits(self):
        """更新每日涨跌停限制"""
        self.limit_up = self.settlement_price * 1.1
        self.limit_down = self.settlement_price * 0.9
    
    def is_near_expiry(self, warning_days=30):
        """检查是否临近到期"""
        days_to_expiry = (self.expiry_date - date.today()).days
        return days_to_expiry <= warning_days
    
    def get_risk_analysis(self):
        """获取风险分析"""
        days_to_expiry = (self.expiry_date - date.today()).days
        
        # 风险等级评估
        if days_to_expiry <= 7:
            risk_level = "极高"
            risk_color = "🔴"
        elif days_to_expiry <= 30:
            risk_level = "高"
            risk_color = "🟠"
        elif days_to_expiry <= 90:
            risk_level = "中等"
            risk_color = "🟡"
        else:
            risk_level = "较低"
            risk_color = "🟢"
        
        # 流动性分析
        if self.volume_24h > 1000000:
            liquidity = "高"
        elif self.volume_24h > 100000:
            liquidity = "中"
        else:
            liquidity = "低"
        
        return {
            'risk_level': risk_level,
            'risk_color': risk_color,
            'days_to_expiry': max(days_to_expiry, 0),
            'liquidity': liquidity,
            'volatility': f"{self.volatility*100:.2f}%",
            'margin_requirement': f"{self.margin_rate*100:.1f}%",
            'daily_limit_range': f"{((self.limit_up/self.limit_down)-1)*100:.1f}%"
        }


def create_futures_contracts():
    """创建期货合约"""
    contracts = {}
    
    # 生成不同到期日
    today = date.today()
    next_month = today.replace(day=1) + timedelta(days=32)
    next_month = next_month.replace(day=1)
    
    # 商品期货
    commodity_futures = [
        # 能源
        ('CL2501', '原油期货2025年1月', 75.45, '原油', 0.01, 1000),
        ('NG2501', '天然气期货2025年1月', 3.25, '天然气', 0.001, 10000),
        ('HO2501', '取暖油期货2025年1月', 2.85, '取暖油', 0.0001, 42000),
        
        # 贵金属
        ('GC2502', '黄金期货2025年2月', 2045.60, '黄金', 0.10, 100),
        ('SI2502', '白银期货2025年2月', 24.56, '白银', 0.005, 5000),
        ('PL2502', '铂金期货2025年2月', 1025.40, '铂金', 0.10, 50),
        
        # 工业金属
        ('HG2501', '铜期货2025年1月', 4.25, '铜', 0.0005, 25000),
        ('PA2502', '钯金期货2025年2月', 1125.80, '钯金', 0.05, 100),
        
        # 农产品
        ('ZC2503', '玉米期货2025年3月', 485.25, '玉米', 0.25, 5000),
        ('ZS2503', '大豆期货2025年3月', 1235.50, '大豆', 0.25, 5000),
        ('ZW2503', '小麦期货2025年3月', 652.75, '小麦', 0.25, 5000),
        ('CT2503', '棉花期货2025年3月', 72.45, '棉花', 0.01, 50000),
        ('CC2503', '可可期货2025年3月', 3256.00, '可可', 1.00, 10),
        ('KC2503', '咖啡期货2025年3月', 165.25, '咖啡', 0.05, 37500),
        ('SB2503', '糖期货2025年3月', 20.85, '糖', 0.01, 112000),
    ]
    
    # 金融期货
    financial_futures = [
        ('ES2501', 'E-mini标普500期货', 4750.25, '股指', 0.25, 50),
        ('NQ2501', 'E-mini纳斯达克期货', 16250.50, '股指', 0.25, 20),
        ('YM2501', 'E-mini道琼斯期货', 37850.00, '股指', 1.00, 5),
        ('ZB2501', '30年国债期货', 142.25, '国债', 0.03125, 1000),
        ('ZN2501', '10年国债期货', 109.75, '国债', 0.015625, 1000),
        ('ZF2501', '5年国债期货', 107.125, '国债', 0.0078125, 1000),
    ]
    
    # 创建商品期货合约
    for symbol, name, price, underlying, tick_size, contract_size in commodity_futures:
        # 解析到期月份
        year = int(symbol[-4:-2]) + 2000
        month = int(symbol[-2:])
        expiry_date = date(year, month, 15)  # 假设15日到期
        
        volatility = random.uniform(0.02, 0.05)
        margin_rate = random.uniform(0.08, 0.15)
        
        contracts[symbol] = FuturesContract(
            symbol, name, price, underlying, expiry_date,
            contract_size, tick_size, "USD", volatility, margin_rate
        )
    
    # 创建金融期货合约
    for symbol, name, price, underlying, tick_size, contract_size in financial_futures:
        # 金融期货通常季度到期
        year = int(symbol[-4:-2]) + 2000
        month = int(symbol[-2:])
        expiry_date = date(year, month, 15)
        
        volatility = random.uniform(0.015, 0.035)
        margin_rate = random.uniform(0.05, 0.12)
        
        contracts[symbol] = FuturesContract(
            symbol, name, price, underlying, expiry_date,
            contract_size, tick_size, "USD", volatility, margin_rate
        )
    
    return contracts 