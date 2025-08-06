"""
大宗商品交易管理器
统一管理外汇、期货、现货等商品交易
"""

import json
import random
from datetime import datetime, timedelta
from .forex import create_major_forex_pairs
from .futures import create_futures_contracts  
from .spot_commodities import create_spot_commodities


class CommodityManager:
    """大宗商品交易管理器"""
    
    def __init__(self):
        self.forex_pairs = create_major_forex_pairs()
        self.futures_contracts = create_futures_contracts()
        self.spot_commodities = create_spot_commodities()
        
        # 合并所有商品
        self.all_commodities = {}
        self.all_commodities.update(self.forex_pairs)
        self.all_commodities.update(self.futures_contracts)
        self.all_commodities.update(self.spot_commodities)
        
        # 交易记录
        self.commodity_positions = {}  # 用户持仓
        self.trade_history = []  # 交易历史
        
        # 价格更新线程控制
        self.last_update = datetime.now()
        self.update_interval = 5  # 5秒更新一次
        
        # 货币转换 - USD到JCK的汇率 (1 USD = 7.14 JCK)
        self.usd_to_jck_rate = 7.14
        
    def convert_usd_to_jck(self, usd_amount):
        """将USD金额转换为JCK"""
        return usd_amount * self.usd_to_jck_rate
    
    def convert_jck_to_usd(self, jck_amount):
        """将JCK金额转换为USD"""
        return jck_amount / self.usd_to_jck_rate
    
    def format_jck_price(self, usd_price):
        """格式化价格为JCK显示"""
        jck_price = self.convert_usd_to_jck(usd_price)
        return f"J${jck_price:,.2f}"
    
    def get_commodity_by_symbol(self, symbol):
        """根据代码获取商品"""
        return self.all_commodities.get(symbol.upper())
    
    def get_commodities_by_type(self, commodity_type):
        """根据类型获取商品列表"""
        if commodity_type.lower() == 'forex':
            return self.forex_pairs
        elif commodity_type.lower() == 'futures':
            return self.futures_contracts
        elif commodity_type.lower() == 'spot':
            return self.spot_commodities
        else:
            return self.all_commodities
    
    def update_all_prices(self):
        """更新所有商品价格"""
        now = datetime.now()
        if (now - self.last_update).seconds < self.update_interval:
            return
        
        for commodity in self.all_commodities.values():
            try:
                commodity.update_price()
            except Exception as e:
                print(f"更新 {commodity.symbol} 价格时出错: {e}")
        
        self.last_update = now
    
    def search_commodities(self, query):
        """搜索商品"""
        query = query.lower()
        results = {}
        
        for symbol, commodity in self.all_commodities.items():
            if (query in symbol.lower() or 
                query in commodity.name.lower() or
                query in str(commodity.underlying_asset if hasattr(commodity, 'underlying_asset') else '').lower()):
                results[symbol] = commodity
        
        return results
    
    def get_market_overview(self):
        """获取市场概览"""
        overview = {
            'forex': {'count': len(self.forex_pairs), 'active': 0, 'gainers': 0, 'losers': 0},
            'futures': {'count': len(self.futures_contracts), 'active': 0, 'gainers': 0, 'losers': 0},
            'spot': {'count': len(self.spot_commodities), 'active': 0, 'gainers': 0, 'losers': 0}
        }
        
        # 统计各类型商品的涨跌情况
        for symbol, commodity in self.forex_pairs.items():
            overview['forex']['active'] += 1 if commodity.is_trading_active() else 0
            overview['forex']['gainers'] += 1 if commodity.change_24h_pct > 0 else 0
            overview['forex']['losers'] += 1 if commodity.change_24h_pct < 0 else 0
        
        for symbol, commodity in self.futures_contracts.items():
            overview['futures']['active'] += 1 if commodity.is_trading_active() else 0
            overview['futures']['gainers'] += 1 if commodity.change_24h_pct > 0 else 0
            overview['futures']['losers'] += 1 if commodity.change_24h_pct < 0 else 0
        
        for symbol, commodity in self.spot_commodities.items():
            overview['spot']['active'] += 1 if commodity.is_trading_active() else 0
            overview['spot']['gainers'] += 1 if commodity.change_24h_pct > 0 else 0
            overview['spot']['losers'] += 1 if commodity.change_24h_pct < 0 else 0
        
        return overview
    
    def get_top_movers(self, limit=5):
        """获取涨跌幅最大的商品"""
        all_items = list(self.all_commodities.values())
        
        # 按涨跌幅排序
        gainers = sorted(all_items, key=lambda x: x.change_24h_pct, reverse=True)[:limit]
        losers = sorted(all_items, key=lambda x: x.change_24h_pct)[:limit]
        
        # 按成交量排序
        volume_leaders = sorted(all_items, key=lambda x: x.volume_24h, reverse=True)[:limit]
        
        return {
            'top_gainers': [{'symbol': c.symbol, 'name': c.name, 'change_pct': c.change_24h_pct} for c in gainers],
            'top_losers': [{'symbol': c.symbol, 'name': c.name, 'change_pct': c.change_24h_pct} for c in losers],
            'volume_leaders': [{'symbol': c.symbol, 'name': c.name, 'volume': c.volume_24h} for c in volume_leaders]
        }
    
    def execute_trade(self, username, symbol, trade_type, quantity, leverage=1, order_type='market'):
        """执行交易"""
        commodity = self.get_commodity_by_symbol(symbol)
        if not commodity:
            return {'success': False, 'message': f'未找到商品: {symbol}'}
        
        # 检查交易时间
        if not commodity.is_trading_active():
            return {'success': False, 'message': f'{symbol} 当前不在交易时间'}
        
        # 计算交易价格
        if order_type == 'market':
            if trade_type.lower() in ['buy', 'long']:
                price = commodity.ask_price
            else:
                price = commodity.bid_price
        else:
            price = commodity.current_price  # 限价单等其他类型暂时使用当前价
        
        # 计算所需保证金 (USD)
        margin_required_usd = commodity.calculate_margin_required(quantity, leverage)
        # 转换为JCK
        margin_required_jck = self.convert_usd_to_jck(margin_required_usd)
        
        # 转换价格为JCK显示
        price_jck = self.convert_usd_to_jck(price) if commodity.currency == 'USD' else price
        
        # 创建交易记录
        trade_record = {
            'id': f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}",
            'username': username,
            'symbol': symbol,
            'commodity_type': self._get_commodity_type(symbol),
            'trade_type': trade_type,
            'quantity': quantity,
            'price': price,  # 保存原始USD价格
            'price_jck': price_jck,  # JCK价格
            'leverage': leverage,
            'margin_required': margin_required_jck,  # JCK保证金
            'margin_required_usd': margin_required_usd,  # USD保证金
            'timestamp': datetime.now().isoformat(),
            'status': 'filled'
        }
        
        # 更新持仓
        position_key = f"{username}_{symbol}"
        if position_key not in self.commodity_positions:
            self.commodity_positions[position_key] = {
                'username': username,
                'symbol': symbol,
                'quantity': 0,
                'avg_price': 0,
                'unrealized_pnl': 0,
                'margin_used': 0
            }
        
        position = self.commodity_positions[position_key]
        
        # 计算新的平均价格和数量
        if trade_type.lower() in ['buy', 'long']:
            total_cost = (position['quantity'] * position['avg_price']) + (quantity * price)
            total_quantity = position['quantity'] + quantity
            position['avg_price'] = total_cost / total_quantity if total_quantity != 0 else price
            position['quantity'] = total_quantity
        else:  # sell, short
            if position['quantity'] >= quantity:
                # 平仓
                position['quantity'] -= quantity
                if position['quantity'] == 0:
                    position['avg_price'] = 0
            else:
                # 反向开仓
                position['quantity'] = quantity - position['quantity']
                position['avg_price'] = price
        
        position['margin_used'] = margin_required_jck
        
        # 添加到交易历史
        self.trade_history.append(trade_record)
        
        return {
            'success': True,
            'message': f'交易执行成功',
            'trade_id': trade_record['id'],
            'trade_record': trade_record,
            'position': position
        }
    
    def get_user_positions(self, username):
        """获取用户持仓"""
        positions = []
        for key, position in self.commodity_positions.items():
            if position['username'] == username and position['quantity'] != 0:
                # 计算未实现盈亏
                commodity = self.get_commodity_by_symbol(position['symbol'])
                if commodity:
                    current_price = commodity.current_price
                    unrealized_pnl = (current_price - position['avg_price']) * position['quantity']
                    position['unrealized_pnl'] = unrealized_pnl
                    position['current_price'] = current_price
                    position['market_value'] = current_price * abs(position['quantity'])
                
                positions.append(position)
        
        return positions
    
    def get_user_trade_history(self, username, limit=20):
        """获取用户交易历史"""
        user_trades = [trade for trade in self.trade_history if trade['username'] == username]
        return sorted(user_trades, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def close_position(self, username, symbol, quantity=None):
        """平仓"""
        position_key = f"{username}_{symbol}"
        if position_key not in self.commodity_positions:
            return {'success': False, 'message': '未找到持仓'}
        
        position = self.commodity_positions[position_key]
        close_quantity = quantity if quantity else abs(position['quantity'])
        
        if abs(position['quantity']) < close_quantity:
            return {'success': False, 'message': '平仓数量大于持仓数量'}
        
        # 执行平仓交易
        close_type = 'sell' if position['quantity'] > 0 else 'buy'
        return self.execute_trade(username, symbol, close_type, close_quantity)
    
    def _get_commodity_type(self, symbol):
        """获取商品类型"""
        if symbol in self.forex_pairs:
            return 'forex'
        elif symbol in self.futures_contracts:
            return 'futures'
        elif symbol in self.spot_commodities:
            return 'spot'
        else:
            return 'unknown'
    
    def get_commodity_info(self, symbol):
        """获取商品详细信息"""
        commodity = self.get_commodity_by_symbol(symbol)
        if not commodity:
            return None
        
        base_info = commodity.get_price_info()
        
        # 添加特定类型的信息
        if hasattr(commodity, 'get_market_analysis'):
            base_info['market_analysis'] = commodity.get_market_analysis()
        
        if hasattr(commodity, 'get_contract_info'):
            base_info['contract_info'] = commodity.get_contract_info()
            
        if hasattr(commodity, 'get_supply_demand_analysis'):
            base_info['supply_demand'] = commodity.get_supply_demand_analysis()
        
        if hasattr(commodity, 'get_risk_analysis'):
            base_info['risk_analysis'] = commodity.get_risk_analysis()
        
        base_info['commodity_type'] = self._get_commodity_type(symbol)
        base_info['technical_indicators'] = commodity.get_technical_indicators()
        
        return base_info
    
    def get_market_calendar(self):
        """获取市场日历"""
        calendar = {}
        
        # 外汇市场时间
        calendar['forex'] = {
            'sydney': '05:00-14:00 (悉尼)',
            'tokyo': '07:00-16:00 (东京)', 
            'london': '15:00-24:00 (伦敦)',
            'new_york': '20:00-05:00 (纽约)'
        }
        
        # 期货市场时间
        calendar['futures'] = {
            'day_session': '09:00-15:00 (日盘)',
            'night_session': '21:00-02:30 (夜盘)'
        }
        
        # 现货市场
        calendar['spot'] = {
            'description': '24小时交易，周末可能受限'
        }
        
        return calendar
    
    def save_data(self, filename):
        """保存数据到文件"""
        data = {
            'positions': self.commodity_positions,
            'trade_history': self.trade_history,
            'last_update': self.last_update.isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_data(self, filename):
        """从文件加载数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.commodity_positions = data.get('positions', {})
            self.trade_history = data.get('trade_history', [])
            
            if 'last_update' in data:
                self.last_update = datetime.fromisoformat(data['last_update'])
            
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"加载数据时出错: {e}")
            return False 