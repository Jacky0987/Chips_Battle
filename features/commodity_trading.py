"""
大宗商品交易功能模块
处理外汇、期货、现货等商品交易命令
"""

from commodities.commodity_manager import CommodityManager
from datetime import datetime


class CommodityTrading:
    """大宗商品交易功能类"""
    
    def __init__(self, app):
        self.app = app
        self.commodity_manager = CommodityManager()
        self.commodity_manager.load_data('data/commodity_data.json')
        
    def handle_forex_command(self, args):
        """处理外汇命令"""
        if not args:
            return self.show_forex_overview()
        
        command = args[0].lower()
        
        if command == 'list':
            return self.show_forex_overview()  # 使用已有的方法
        elif command == 'info' and len(args) > 1:
            return self.show_forex_info(args[1])
        elif command == 'buy' and len(args) >= 3:
            return self.execute_forex_trade(args[1], 'buy', float(args[2]), args[3:])
        elif command == 'sell' and len(args) >= 3:
            return self.execute_forex_trade(args[1], 'sell', float(args[2]), args[3:])
        elif command == 'sessions':
            return self.show_trading_sessions()
        else:
            return self.show_forex_help()
    
    def handle_futures_command(self, args):
        """处理期货命令"""
        if not args:
            return self.show_futures_overview()
        
        command = args[0].lower()
        
        if command == 'list':
            return self.show_futures_list()
        elif command == 'info' and len(args) > 1:
            return self.show_futures_info(args[1])
        elif command == 'buy' and len(args) >= 3:
            return self.execute_futures_trade(args[1], 'buy', int(args[2]), args[3:])
        elif command == 'sell' and len(args) >= 3:
            return self.execute_futures_trade(args[1], 'sell', int(args[2]), args[3:])
        elif command == 'contracts':
            return self.show_active_contracts()
        else:
            return self.show_futures_help()
    
    def handle_spot_command(self, args):
        """处理现货命令"""
        if not args:
            return self.show_spot_overview()
        
        command = args[0].lower()
        
        if command == 'list':
            return self.show_spot_list()
        elif command == 'info' and len(args) > 1:
            return self.show_spot_info(args[1])
        elif command == 'buy' and len(args) >= 3:
            return self.execute_spot_trade(args[1], 'buy', float(args[2]), args[3:])
        elif command == 'sell' and len(args) >= 3:
            return self.execute_spot_trade(args[1], 'sell', float(args[2]), args[3:])
        elif command == 'delivery':
            return self.show_delivery_info()
        else:
            return self.show_spot_help()
    
    def handle_commodity_command(self, args):
        """处理通用商品命令"""
        if not args:
            return self.show_commodity_overview()
        
        command = args[0].lower()
        
        if command == 'search' and len(args) > 1:
            return self.search_commodities(args[1])
        elif command == 'positions':
            return self.show_positions()
        elif command == 'history':
            return self.show_trade_history()
        elif command == 'close' and len(args) > 1:
            return self.close_position(args[1])
        elif command == 'movers':
            return self.show_top_movers()
        elif command == 'calendar':
            return self.show_market_calendar()
        else:
            return self.show_commodity_help()
    
    def show_forex_overview(self):
        """显示外汇市场概览"""
        overview = self.commodity_manager.get_market_overview()['forex']
        pairs = self.commodity_manager.get_commodities_by_type('forex')
        
        result = "\n🌍 外汇市场概览\n"
        result += "═" * 60 + "\n"
        result += f"总货币对数量: {overview['count']}\n"
        result += f"当前活跃: {overview['active']}\n"
        result += f"上涨货币对: {overview['gainers']}\n"
        result += f"下跌货币对: {overview['losers']}\n\n"
        
        result += "主要货币对:\n"
        result += "─" * 60 + "\n"
        result += f"{'货币对':<12} {'当前价格':<12} {'涨跌':<10} {'点差':<8} {'状态':<8}\n"
        result += "─" * 60 + "\n"
        
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD']
        for symbol in major_pairs:
            if symbol in pairs:
                pair = pairs[symbol]
                # 转换为JCK显示
                price_jck = self.commodity_manager.convert_usd_to_jck(pair.current_price) if pair.currency == 'USD' else pair.current_price
                change_str = f"{pair.change_24h_pct:+.2f}%"
                spread_pips = (pair.spread / pair.pip_size)
                status = "活跃" if pair.is_trading_active() else "休市"
                result += f"{symbol:<12} J${price_jck:<11.4f} {change_str:<10} {spread_pips:<8.1f} {status:<8}\n"
        
        result += "─" * 60 + "\n"
        result += "输入 'forex help' 查看详细命令\n"
        
        return result
    
    def show_futures_overview(self):
        """显示期货市场概览"""
        overview = self.commodity_manager.get_market_overview()['futures']
        contracts = self.commodity_manager.get_commodities_by_type('futures')
        
        result = "\n📈 期货市场概览\n"
        result += "═" * 70 + "\n"
        result += f"总合约数量: {overview['count']}\n"
        result += f"当前活跃: {overview['active']}\n"
        result += f"上涨合约: {overview['gainers']}\n"
        result += f"下跌合约: {overview['losers']}\n\n"
        
        # 按类别显示
        categories = {
            '能源': ['CL2501', 'NG2501', 'HO2501'],
            '贵金属': ['GC2502', 'SI2502', 'PL2502'],
            '农产品': ['ZC2503', 'ZS2503', 'ZW2503'],
            '股指': ['ES2501', 'NQ2501', 'YM2501']
        }
        
        for category, symbols in categories.items():
            result += f"\n{category}期货:\n"
            result += f"{'合约':<12} {'价格':<10} {'涨跌':<10} {'到期日':<12} {'风险':<8}\n"
            result += "─" * 60 + "\n"
            
            for symbol in symbols:
                if symbol in contracts:
                    contract = contracts[symbol]
                    price_jck = self.commodity_manager.convert_usd_to_jck(contract.current_price)
                    change_str = f"{contract.change_24h_pct:+.2f}%"
                    expiry = contract.expiry_date.strftime('%m-%d')
                    risk = contract.get_risk_analysis()['risk_color']
                    result += f"{symbol:<12} J${price_jck:<9.2f} {change_str:<10} {expiry:<12} {risk:<8}\n"
        
        result += "\n输入 'futures help' 查看详细命令\n"
        
        return result
    
    def show_spot_overview(self):
        """显示现货市场概览"""
        overview = self.commodity_manager.get_market_overview()['spot']
        commodities = self.commodity_manager.get_commodities_by_type('spot')
        
        result = "\n🏪 现货市场概览\n"
        result += "═" * 70 + "\n"
        result += f"总商品数量: {overview['count']}\n"
        result += f"当前活跃: {overview['active']}\n"
        result += f"上涨商品: {overview['gainers']}\n"
        result += f"下跌商品: {overview['losers']}\n\n"
        
        # 按类别显示
        categories = {
            '贵金属': ['XAUUSD_SPOT', 'XAGUSD_SPOT', 'XPTUSD_SPOT'],
            '能源': ['WTI_SPOT', 'BRENT_SPOT', 'NATGAS_SPOT'],
            '工业金属': ['COPPER_SPOT', 'ALUMINUM_SPOT', 'ZINC_SPOT'],
            '农产品': ['CORN_SPOT', 'WHEAT_SPOT', 'COFFEE_SPOT']
        }
        
        for category, symbols in categories.items():
            result += f"\n{category}:\n"
            result += f"{'商品':<15} {'价格':<12} {'涨跌':<10} {'单位':<8} {'库存':<8}\n"
            result += "─" * 60 + "\n"
            
            for symbol in symbols:
                if symbol in commodities:
                    commodity = commodities[symbol]
                    price_jck = self.commodity_manager.convert_usd_to_jck(commodity.current_price)
                    change_str = f"{commodity.change_24h_pct:+.2f}%"
                    supply_demand = commodity.get_supply_demand_analysis()
                    inventory = supply_demand['inventory_status'][:2]
                    result += f"{symbol:<15} J${price_jck:<11.2f} {change_str:<10} {commodity.unit:<8} {inventory:<8}\n"
        
        result += "\n输入 'spot help' 查看详细命令\n"
        
        return result
    
    def execute_forex_trade(self, symbol, trade_type, quantity, options):
        """执行外汇交易"""
        # 解析选项
        leverage = 100  # 默认杠杆
        for opt in options:
            if opt.startswith('leverage='):
                leverage = int(opt.split('=')[1])
        
        result = self.commodity_manager.execute_trade(
            self.app.user_manager.current_user,
            symbol.upper(),
            trade_type,
            quantity,
            leverage
        )
        
        if result['success']:
            trade = result['trade_record']
            position = result['position']
            
            output = f"\n✅ 外汇交易执行成功\n"
            output += "═" * 50 + "\n"
            output += f"交易ID: {trade['id']}\n"
            output += f"货币对: {trade['symbol']}\n"
            output += f"操作: {'买入' if trade_type == 'buy' else '卖出'}\n"
            output += f"数量: {quantity} 手\n"
            output += f"价格: J${trade['price_jck']:.4f}\n"
            output += f"杠杆: 1:{leverage}\n"
            output += f"保证金: J${trade['margin_required']:.2f}\n\n"
            
            output += f"当前持仓:\n"
            output += f"数量: {position['quantity']} 手\n"
            avg_price_jck = self.commodity_manager.convert_usd_to_jck(position['avg_price'])
            output += f"平均成本: J${avg_price_jck:.4f}\n"
            output += f"未实现盈亏: J${position.get('unrealized_pnl', 0):.2f}\n"
            
            # 保存数据
            self.commodity_manager.save_data('data/commodity_data.json')
            
            return output
        else:
            return f"❌ 交易失败: {result['message']}"
    
    def show_positions(self):
        """显示当前持仓"""
        positions = self.commodity_manager.get_user_positions(self.app.user_manager.current_user)
        
        if not positions:
            return "\n📊 当前无持仓\n"
        
        result = "\n📊 当前持仓\n"
        result += "═" * 80 + "\n"
        result += f"{'商品':<12} {'类型':<8} {'数量':<10} {'成本价':<12} {'现价':<12} {'盈亏':<12}\n"
        result += "─" * 80 + "\n"
        
        total_pnl = 0
        for position in positions:
            symbol = position['symbol']
            commodity_type = self.commodity_manager._get_commodity_type(symbol)
            quantity = position['quantity']
            avg_price = position['avg_price']
            current_price = position.get('current_price', 0)
            pnl = position.get('unrealized_pnl', 0)
            total_pnl += pnl
            
            # 转换为JCK显示
            avg_price_jck = self.commodity_manager.convert_usd_to_jck(avg_price)
            current_price_jck = self.commodity_manager.convert_usd_to_jck(current_price) if current_price > 0 else 0
            pnl_jck = self.commodity_manager.convert_usd_to_jck(pnl)
            
            pnl_str = f"J${pnl_jck:+.2f}" if pnl != 0 else "J$0.00"
            type_str = {'forex': '外汇', 'futures': '期货', 'spot': '现货'}.get(commodity_type, commodity_type)
            
            result += f"{symbol:<12} {type_str:<8} {quantity:<10.2f} J${avg_price_jck:<11.4f} J${current_price_jck:<11.4f} {pnl_str:<12}\n"
        
        result += "─" * 80 + "\n"
        total_pnl_jck = self.commodity_manager.convert_usd_to_jck(total_pnl)
        result += f"总盈亏: J${total_pnl_jck:+.2f}\n"
        
        return result
    
    def show_top_movers(self):
        """显示涨跌幅排行"""
        movers = self.commodity_manager.get_top_movers(10)
        
        result = "\n📈 今日涨跌幅排行\n"
        result += "═" * 60 + "\n"
        
        result += "涨幅榜:\n"
        result += f"{'商品':<15} {'名称':<20} {'涨幅':<10}\n"
        result += "─" * 50 + "\n"
        for item in movers['top_gainers']:
            result += f"{item['symbol']:<15} {item['name'][:18]:<20} {item['change_pct']:+.2f}%\n"
        
        result += "\n跌幅榜:\n"
        result += f"{'商品':<15} {'名称':<20} {'跌幅':<10}\n"
        result += "─" * 50 + "\n"
        for item in movers['top_losers']:
            result += f"{item['symbol']:<15} {item['name'][:18]:<20} {item['change_pct']:+.2f}%\n"
        
        result += "\n成交量排行:\n"
        result += f"{'商品':<15} {'名称':<20} {'成交量':<15}\n"
        result += "─" * 50 + "\n"
        for item in movers['volume_leaders']:
            volume_str = f"{item['volume']:,.0f}"
            result += f"{item['symbol']:<15} {item['name'][:18]:<20} {volume_str:<15}\n"
        
        return result
    
    def show_forex_help(self):
        """显示外汇帮助信息"""
        return """\n🌍 外汇交易命令帮助
═══════════════════════════════════════════════════════════
基础命令:
  forex                    - 显示外汇市场概览
  forex list              - 显示所有货币对
  forex sessions          - 显示交易时段信息

查询命令:
  forex info <货币对>     - 显示货币对详细信息
  
交易命令:  
  forex buy <货币对> <手数> [leverage=杠杆]   - 买入
  forex sell <货币对> <手数> [leverage=杠杆]  - 卖出
  
示例:
  forex buy EURUSD 0.1 leverage=100   - 以100倍杠杆买入0.1手欧美
  forex info GBPUSD                   - 查看英镑美元信息
  forex sessions                      - 查看全球交易时段
═══════════════════════════════════════════════════════════"""
    
    def show_futures_help(self):
        """显示期货帮助信息"""
        return """\n📈 期货交易命令帮助
═══════════════════════════════════════════════════════════
基础命令:
  futures                     - 显示期货市场概览
  futures list               - 显示所有期货合约
  futures contracts          - 显示活跃合约信息

查询命令:
  futures info <合约代码>    - 显示合约详细信息
  
交易命令:
  futures buy <合约> <数量>   - 买入期货合约
  futures sell <合约> <数量>  - 卖出期货合约
  
示例:
  futures buy CL2501 1       - 买入1手原油期货
  futures info GC2502        - 查看黄金期货信息
  futures contracts          - 查看即将到期的合约
═══════════════════════════════════════════════════════════"""
    
    def show_spot_help(self):
        """显示现货帮助信息"""
        return """\n🏪 现货交易命令帮助
═══════════════════════════════════════════════════════════
基础命令:
  spot                       - 显示现货市场概览
  spot list                 - 显示所有现货商品
  spot delivery             - 显示交割信息

查询命令:
  spot info <商品代码>      - 显示商品详细信息
  
交易命令:
  spot buy <商品> <数量>     - 买入现货商品
  spot sell <商品> <数量>    - 卖出现货商品
  
示例:
  spot buy XAUUSD_SPOT 10   - 买入10盎司现货黄金
  spot info WTI_SPOT        - 查看WTI原油现货信息
  spot delivery             - 查看交割地点和费用
═══════════════════════════════════════════════════════════"""
    
    def show_commodity_help(self):
        """显示商品交易通用帮助"""
        return """\n💼 大宗商品交易系统帮助
═══════════════════════════════════════════════════════════
通用命令:
  commodity                  - 显示商品市场概览
  commodity search <关键词>  - 搜索商品
  commodity positions        - 显示当前持仓
  commodity history          - 显示交易历史
  commodity close <商品>     - 平仓指定商品
  commodity movers           - 显示涨跌幅排行
  commodity calendar         - 显示市场时间

专项命令:
  forex [参数]              - 外汇交易 (输入 'forex help' 查看详情)
  futures [参数]            - 期货交易 (输入 'futures help' 查看详情)  
  spot [参数]               - 现货交易 (输入 'spot help' 查看详情)

示例:
  commodity search 黄金      - 搜索黄金相关商品
  commodity positions        - 查看所有持仓
  commodity movers           - 查看今日涨跌排行
═══════════════════════════════════════════════════════════"""