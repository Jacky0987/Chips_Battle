import json
import random
import threading
import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import os

class Currency:
    """货币类"""
    
    def __init__(self, code, name, symbol, base_rate=1.0, volatility=0.02):
        self.code = code  # 货币代码 如 USD, EUR, CNY
        self.name = name  # 货币名称
        self.symbol = symbol  # 货币符号
        self.base_rate = base_rate  # 相对于基础货币的汇率
        self.current_rate = base_rate
        self.volatility = volatility  # 汇率波动率
        self.history = [base_rate] * 20  # 汇率历史
        self.last_updated = datetime.now()
        
    def update_rate(self):
        """更新汇率"""
        change_factor = random.gauss(0, self.volatility)
        self.current_rate = max(0.001, self.current_rate * (1 + change_factor))
        
        # 更新历史记录
        self.history.append(self.current_rate)
        if len(self.history) > 100:
            self.history.pop(0)
            
        self.last_updated = datetime.now()
        
    def get_trend(self):
        """获取汇率趋势"""
        if len(self.history) < 2:
            return "横盘"
        
        recent_avg = sum(self.history[-5:]) / 5
        earlier_avg = sum(self.history[-10:-5]) / 5
        
        if recent_avg > earlier_avg * 1.01:
            return "上升"
        elif recent_avg < earlier_avg * 0.99:
            return "下降"
        else:
            return "横盘"

class TradableInstrument(ABC):
    """可交易工具基类"""
    
    def __init__(self, symbol, name, category, price, contract_size=1):
        self.symbol = symbol
        self.name = name
        self.category = category  # forex, commodity, futures
        self.price = price
        self.contract_size = contract_size
        self.history = [price] * 20
        self.last_updated = datetime.now()
        
    @abstractmethod
    def update_price(self):
        """更新价格"""
        pass
        
    @abstractmethod
    def get_margin_requirement(self):
        """获取保证金要求"""
        pass

class ForexPair(TradableInstrument):
    """外汇货币对"""
    
    def __init__(self, symbol, base_currency, quote_currency, price, volatility=0.015):
        super().__init__(symbol, f"{base_currency}/{quote_currency}", "forex", price)
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.volatility = volatility
        self.spread = 0.0002  # 点差
        
    def update_price(self):
        """更新汇率"""
        change = random.gauss(0, self.volatility)
        self.price = max(0.0001, self.price * (1 + change))
        
        self.history.append(self.price)
        if len(self.history) > 100:
            self.history.pop(0)
            
        self.last_updated = datetime.now()
        
    def get_margin_requirement(self):
        """外汇保证金要求 (通常1:100杠杆)"""
        return 0.01  # 1%保证金
        
    def get_bid_ask(self):
        """获取买卖价"""
        half_spread = self.spread / 2
        bid = self.price - half_spread
        ask = self.price + half_spread
        return bid, ask

class Commodity(TradableInstrument):
    """大宗商品"""
    
    def __init__(self, symbol, name, price, unit, volatility=0.025):
        super().__init__(symbol, name, "commodity", price)
        self.unit = unit  # 计量单位
        self.volatility = volatility
        self.margin_rate = 0.05  # 5%保证金
        
    def update_price(self):
        """更新商品价格"""
        # 商品价格受供需影响较大，波动可能更剧烈
        change = random.gauss(0, self.volatility)
        # 添加一些季节性/周期性影响
        seasonal_factor = 0.01 * random.uniform(-1, 1)
        total_change = change + seasonal_factor
        
        self.price = max(0.01, self.price * (1 + total_change))
        
        self.history.append(self.price)
        if len(self.history) > 100:
            self.history.pop(0)
            
        self.last_updated = datetime.now()
        
    def get_margin_requirement(self):
        """商品保证金要求"""
        return self.margin_rate

class FuturesContract(TradableInstrument):
    """期货合约"""
    
    def __init__(self, symbol, name, underlying_price, expiry_date, contract_size=1, volatility=0.03):
        super().__init__(symbol, name, "futures", underlying_price, contract_size)
        self.underlying_price = underlying_price
        self.expiry_date = expiry_date
        self.volatility = volatility
        self.margin_rate = 0.08  # 8%保证金
        
    def update_price(self):
        """更新期货价格"""
        # 期货价格基于标的资产价格
        change = random.gauss(0, self.volatility)
        
        # 临近交割期时价格趋向标的资产价格
        days_to_expiry = (self.expiry_date - datetime.now()).days
        if days_to_expiry <= 30:
            convergence_factor = (30 - days_to_expiry) / 30 * 0.1
            self.price = self.price * (1 + change - convergence_factor)
        else:
            self.price = max(0.01, self.price * (1 + change))
        
        self.history.append(self.price)
        if len(self.history) > 100:
            self.history.pop(0)
            
        self.last_updated = datetime.now()
        
    def get_margin_requirement(self):
        """期货保证金要求"""
        return self.margin_rate
        
    def is_expired(self):
        """检查是否已到期"""
        return datetime.now() >= self.expiry_date

class CurrencyManager:
    """货币管理器"""
    
    def __init__(self):
        self.base_currency = "JCD"  # JackyCoin Dollars
        self.currencies = {}
        self.forex_pairs = {}
        self.commodities = {}
        self.futures = {}
        self.exchange_rates = {}
        self.price_update_thread = None
        self.is_running = False
        
        self.init_currencies()
        self.init_forex_pairs()
        self.init_commodities()
        self.init_futures()
        
    def init_currencies(self):
        """初始化货币"""
        currencies_data = [
            ("JCD", "JackyCoin Dollar", "J$", 1.0, 0.01),  # 基础货币
            ("USD", "US Dollar", "$", 0.14, 0.015),        # 美元
            ("EUR", "Euro", "€", 0.13, 0.016),            # 欧元
            ("GBP", "British Pound", "£", 0.11, 0.018),   # 英镑
            ("JPY", "Japanese Yen", "¥", 15.8, 0.017),    # 日元
            ("CNY", "Chinese Yuan", "¥", 1.0, 0.012),     # 人民币
            ("AUD", "Australian Dollar", "A$", 0.21, 0.019), # 澳元
            ("CAD", "Canadian Dollar", "C$", 0.19, 0.017),   # 加元
            ("CHF", "Swiss Franc", "Fr", 0.13, 0.014),       # 瑞士法郎
            ("NZD", "New Zealand Dollar", "NZ$", 0.23, 0.021), # 新西兰元
        ]
        
        for code, name, symbol, rate, volatility in currencies_data:
            self.currencies[code] = Currency(code, name, symbol, rate, volatility)
            
    def init_forex_pairs(self):
        """初始化外汇货币对"""
        pairs_data = [
            ("JCD/USD", "JCD", "USD", 0.14, 0.015),
            ("JCD/EUR", "JCD", "EUR", 0.13, 0.016),
            ("JCD/GBP", "JCD", "GBP", 0.11, 0.018),
            ("JCD/JPY", "JCD", "JPY", 15.8, 0.020),
            ("JCD/CNY", "JCD", "CNY", 1.0, 0.012),
            ("USD/EUR", "USD", "EUR", 0.92, 0.012),
            ("GBP/USD", "GBP", "USD", 1.27, 0.014),
            ("USD/JPY", "USD", "JPY", 112.5, 0.016),
            ("EUR/JPY", "EUR", "JPY", 122.8, 0.018),
            ("AUD/USD", "AUD", "USD", 0.67, 0.019),
        ]
        
        for symbol, base, quote, price, volatility in pairs_data:
            self.forex_pairs[symbol] = ForexPair(symbol, base, quote, price, volatility)
            
    def init_commodities(self):
        """初始化大宗商品"""
        commodities_data = [
            ("GOLD", "黄金", 1850.0, "盎司", 0.020),
            ("SILVER", "白银", 22.5, "盎司", 0.035),
            ("OIL", "原油", 75.2, "桶", 0.045),
            ("COPPER", "铜", 3.8, "磅", 0.030),
            ("WHEAT", "小麦", 5.4, "蒲式耳", 0.028),
            ("CORN", "玉米", 4.2, "蒲式耳", 0.025),
            ("COTTON", "棉花", 0.68, "磅", 0.032),
            ("SUGAR", "糖", 0.19, "磅", 0.038),
            ("COFFEE", "咖啡", 1.35, "磅", 0.033),
            ("NATGAS", "天然气", 2.8, "百万英热单位", 0.055),
        ]
        
        for symbol, name, price, unit, volatility in commodities_data:
            self.commodities[symbol] = Commodity(symbol, name, price, unit, volatility)
            
    def init_futures(self):
        """初始化期货合约"""
        # 生成未来几个月的期货合约
        base_date = datetime.now()
        
        futures_data = [
            ("GOLD_F", "黄金期货", 1855.0, 1, 0.022),
            ("OIL_F", "原油期货", 76.0, 1000, 0.048),
            ("WHEAT_F", "小麦期货", 5.45, 5000, 0.030),
            ("COPPER_F", "铜期货", 3.82, 25000, 0.032),
            ("NATGAS_F", "天然气期货", 2.85, 10000, 0.058),
        ]
        
        for symbol, name, price, contract_size, volatility in futures_data:
            # 创建3个不同到期日的合约
            for i in range(1, 4):
                expiry = base_date + timedelta(days=30*i)
                contract_symbol = f"{symbol}{i:02d}"
                self.futures[contract_symbol] = FuturesContract(
                    contract_symbol, f"{name} {i}月", price, expiry, contract_size, volatility
                )
                
    def start_price_updates(self):
        """启动价格更新线程"""
        if self.is_running:
            return
            
        self.is_running = True
        self.price_update_thread = threading.Thread(target=self._price_update_loop, daemon=True)
        self.price_update_thread.start()
        
    def stop_price_updates(self):
        """停止价格更新"""
        self.is_running = False
        
    def _price_update_loop(self):
        """价格更新循环"""
        while self.is_running:
            try:
                # 更新货币汇率
                for currency in self.currencies.values():
                    if currency.code != self.base_currency:
                        currency.update_rate()
                
                # 更新外汇对
                for pair in self.forex_pairs.values():
                    pair.update_price()
                
                # 更新商品价格
                for commodity in self.commodities.values():
                    commodity.update_price()
                
                # 更新期货价格
                for futures_contract in list(self.futures.values()):
                    if futures_contract.is_expired():
                        # 移除已到期的合约
                        del self.futures[futures_contract.symbol]
                    else:
                        futures_contract.update_price()
                
                time.sleep(10)  # 每10秒更新一次
                
            except Exception as e:
                print(f"价格更新错误: {e}")
                time.sleep(5)
                
    def get_exchange_rate(self, from_currency, to_currency):
        """获取汇率"""
        if from_currency == to_currency:
            return 1.0
            
        if from_currency == self.base_currency:
            return self.currencies[to_currency].current_rate
        elif to_currency == self.base_currency:
            return 1.0 / self.currencies[from_currency].current_rate
        else:
            # 通过基础货币转换
            from_to_base = 1.0 / self.currencies[from_currency].current_rate
            base_to_target = self.currencies[to_currency].current_rate
            return from_to_base * base_to_target
            
    def convert_currency(self, amount, from_currency, to_currency):
        """货币转换"""
        rate = self.get_exchange_rate(from_currency, to_currency)
        return amount * rate
        
    def get_currency_info(self, currency_code):
        """获取货币信息"""
        if currency_code not in self.currencies:
            return None
        return self.currencies[currency_code]
        
    def get_forex_pair_info(self, pair_symbol):
        """获取外汇对信息"""
        if pair_symbol not in self.forex_pairs:
            return None
        return self.forex_pairs[pair_symbol]
        
    def get_commodity_info(self, symbol):
        """获取商品信息"""
        if symbol not in self.commodities:
            return None
        return self.commodities[symbol]
        
    def get_futures_info(self, symbol):
        """获取期货信息"""
        if symbol not in self.futures:
            return None
        return self.futures[symbol]
        
    def get_all_instruments(self):
        """获取所有交易工具"""
        return {
            'forex': self.forex_pairs,
            'commodities': self.commodities,
            'futures': self.futures
        }
        
    def save_data(self):
        """保存货币数据"""
        try:
            os.makedirs('data', exist_ok=True)
            
            data = {
                'currencies': {
                    code: {
                        'current_rate': curr.current_rate,
                        'history': curr.history[-20:],  # 只保存最近20个数据点
                        'last_updated': curr.last_updated.isoformat()
                    } for code, curr in self.currencies.items()
                },
                'last_saved': datetime.now().isoformat()
            }
            
            with open('data/currency_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存货币数据失败: {e}")
            
    def load_data(self):
        """加载货币数据"""
        try:
            if os.path.exists('data/currency_data.json'):
                with open('data/currency_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 恢复货币数据
                currencies_data = data.get('currencies', {})
                for code, curr_data in currencies_data.items():
                    if code in self.currencies:
                        self.currencies[code].current_rate = curr_data['current_rate']
                        self.currencies[code].history = curr_data['history']
                        
        except Exception as e:
            print(f"加载货币数据失败: {e}")

class ForexTradingEngine:
    """外汇交易引擎"""
    
    def __init__(self, currency_manager):
        self.currency_manager = currency_manager
        
    def open_position(self, user_portfolio, symbol, position_type, lot_size, leverage=100):
        """开仓
        
        Args:
            symbol: 交易对符号
            position_type: 'buy' 或 'sell'
            lot_size: 手数
            leverage: 杠杆倍数
        """
        instrument = self.currency_manager.get_forex_pair_info(symbol)
        if not instrument:
            return False, f"交易对 {symbol} 不存在"
            
        bid, ask = instrument.get_bid_ask()
        entry_price = ask if position_type == 'buy' else bid
        
        # 计算保证金要求
        notional_value = entry_price * lot_size * 100000  # 标准手
        margin_required = notional_value / leverage
        
        # 检查保证金
        available_margin = self._calculate_available_margin(user_portfolio)
        if margin_required > available_margin:
            return False, f"保证金不足，需要 J${margin_required:,.2f}，可用 J${available_margin:,.2f}"
        
        # 创建持仓
        position_id = f"FX_{len(user_portfolio.get('forex_positions', {})) + 1:06d}"
        position = {
            'id': position_id,
            'symbol': symbol,
            'type': position_type,
            'lot_size': lot_size,
            'entry_price': entry_price,
            'leverage': leverage,
            'margin_used': margin_required,
            'open_time': datetime.now().isoformat(),
            'unrealized_pnl': 0.0,
            'swap': 0.0  # 隔夜利息
        }
        
        if 'forex_positions' not in user_portfolio:
            user_portfolio['forex_positions'] = {}
        user_portfolio['forex_positions'][position_id] = position
        
        return True, f"外汇仓位已开启: {symbol} {position_type.upper()} {lot_size}手 @{entry_price:.5f}"
        
    def close_position(self, user_portfolio, position_id):
        """平仓"""
        if 'forex_positions' not in user_portfolio or position_id not in user_portfolio['forex_positions']:
            return False, "持仓不存在"
            
        position = user_portfolio['forex_positions'][position_id]
        symbol = position['symbol']
        
        instrument = self.currency_manager.get_forex_pair_info(symbol)
        if not instrument:
            return False, f"交易对 {symbol} 不存在"
            
        bid, ask = instrument.get_bid_ask()
        exit_price = bid if position['type'] == 'buy' else ask
        
        # 计算盈亏
        pnl = self._calculate_position_pnl(position, exit_price)
        
        # 移除持仓
        del user_portfolio['forex_positions'][position_id]
        
        return True, f"持仓已平仓: 盈亏 J${pnl:+,.2f}", pnl
        
    def _calculate_position_pnl(self, position, current_price):
        """计算持仓盈亏"""
        entry_price = position['entry_price']
        lot_size = position['lot_size']
        position_type = position['type']
        
        if position_type == 'buy':
            price_diff = current_price - entry_price
        else:
            price_diff = entry_price - current_price
            
        pnl = price_diff * lot_size * 100000  # 标准手
        return pnl
        
    def _calculate_available_margin(self, user_portfolio):
        """计算可用保证金"""
        # 简化版本，实际应该更复杂
        cash = user_portfolio.get('cash', 0)
        used_margin = sum(
            pos['margin_used'] for pos in user_portfolio.get('forex_positions', {}).values()
        )
        return cash - used_margin
        
    def update_positions(self, user_portfolio):
        """更新所有持仓的未实现盈亏"""
        if 'forex_positions' not in user_portfolio:
            return
            
        for position in user_portfolio['forex_positions'].values():
            symbol = position['symbol']
            instrument = self.currency_manager.get_forex_pair_info(symbol)
            if instrument:
                bid, ask = instrument.get_bid_ask()
                current_price = bid if position['type'] == 'buy' else ask
                position['unrealized_pnl'] = self._calculate_position_pnl(position, current_price) 