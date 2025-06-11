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

    def show_futures_list(self):
        """显示期货合约列表"""
        contracts = self.commodity_manager.get_commodities_by_type('futures')
        
        result = "\n📈 期货合约列表\n"
        result += "═" * 90 + "\n"
        result += f"{'合约代码':<12} {'名称':<25} {'价格(JCK)':<12} {'涨跌%':<8} {'到期日':<12} {'状态':<8}\n"
        result += "─" * 90 + "\n"
        
        # 按到期日排序
        sorted_contracts = sorted(contracts.items(), key=lambda x: x[1].expiry_date)
        
        for symbol, contract in sorted_contracts:
            price_jck = self.commodity_manager.convert_usd_to_jck(contract.current_price)
            change_str = f"{contract.change_24h_pct:+.2f}%"
            expiry = contract.expiry_date.strftime('%Y-%m-%d')
            status = "活跃" if contract.is_trading_active() else "休市"
            name_short = contract.name[:23] if len(contract.name) > 23 else contract.name
            
            result += f"{symbol:<12} {name_short:<25} J${price_jck:<11.2f} {change_str:<8} {expiry:<12} {status:<8}\n"
        
        result += "─" * 90 + "\n"
        result += f"总计: {len(contracts)} 个期货合约\n"
        result += "输入 'futures info <合约代码>' 查看详细信息\n"
        
        return result
    
    def show_futures_info(self, symbol):
        """显示期货合约详细信息"""
        contract = self.commodity_manager.get_commodity_by_symbol(symbol)
        
        if not contract or not hasattr(contract, 'expiry_date'):
            return f"❌ 未找到期货合约: {symbol}"
        
        # 获取合约信息
        info = contract.get_contract_info()
        price_jck = self.commodity_manager.convert_usd_to_jck(contract.current_price)
        settlement_jck = self.commodity_manager.convert_usd_to_jck(contract.settlement_price)
        
        result = f"\n📈 期货合约详情 - {symbol}\n"
        result += "═" * 70 + "\n"
        result += f"合约名称: {contract.name}\n"
        result += f"标的资产: {contract.underlying_asset}\n"
        result += f"当前价格: J${price_jck:.4f}\n"
        result += f"结算价格: J${settlement_jck:.4f}\n"
        result += f"24小时涨跌: {contract.change_24h_pct:+.2f}%\n\n"
        
        result += "合约规格:\n"
        result += "─" * 40 + "\n"
        result += f"合约乘数: {contract.contract_size:,}\n"
        result += f"最小跳动: {contract.tick_size}\n"
        result += f"保证金比例: {info['margin_rate']}\n"
        result += f"到期日期: {info['expiry_date']}\n"
        result += f"最后交易日: {info['last_trading_day']}\n"
        result += f"交割方式: {info['delivery_method']}\n\n"
        
        result += "市场数据:\n"
        result += "─" * 40 + "\n"
        limit_up_jck = self.commodity_manager.convert_usd_to_jck(contract.limit_up)
        limit_down_jck = self.commodity_manager.convert_usd_to_jck(contract.limit_down)
        result += f"涨停价: J${limit_up_jck:.4f}\n"
        result += f"跌停价: J${limit_down_jck:.4f}\n"
        result += f"持仓量: {contract.open_interest:,} 手\n"
        result += f"成交量: {contract.volume_24h:,} 手\n"
        result += f"距离到期: {info['days_to_expiry']} 天\n\n"
        
        # 风险分析
        risk_analysis = contract.get_risk_analysis()
        result += "风险评估:\n"
        result += "─" * 40 + "\n"
        result += f"风险等级: {risk_analysis['risk_level']}\n"
        result += f"波动率: {contract.volatility*100:.2f}%\n"
        result += f"流动性: {risk_analysis.get('liquidity', '良好')}\n"
        
        return result
    
    def execute_futures_trade(self, symbol, trade_type, quantity, options):
        """执行期货交易"""
        result = self.commodity_manager.execute_trade(
            self.app.user_manager.current_user,
            symbol.upper(),
            trade_type,
            quantity,
            1  # 期货通常不使用杠杆，因为已经是杠杆产品
        )
        
        if result['success']:
            trade = result['trade_record']
            position = result['position']
            
            output = f"\n✅ 期货交易执行成功\n"
            output += "═" * 50 + "\n"
            output += f"交易ID: {trade['id']}\n"
            output += f"期货合约: {trade['symbol']}\n"
            output += f"操作: {'买入开仓' if trade_type == 'buy' else '卖出开仓'}\n"
            output += f"数量: {quantity} 手\n"
            output += f"价格: J${trade['price_jck']:.4f}\n"
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
            return f"❌ 期货交易失败: {result['message']}"
    
    def show_active_contracts(self):
        """显示活跃期货合约"""
        contracts = self.commodity_manager.get_commodities_by_type('futures')
        
        result = "\n📈 活跃期货合约\n"
        result += "═" * 80 + "\n"
        
        # 按到期时间分组
        from datetime import date, timedelta
        today = date.today()
        near_expiry = []
        active_contracts = []
        
        for symbol, contract in contracts.items():
            days_to_expiry = (contract.expiry_date - today).days
            if days_to_expiry <= 30:
                near_expiry.append((symbol, contract, days_to_expiry))
            else:
                active_contracts.append((symbol, contract, days_to_expiry))
        
        # 显示即将到期的合约
        if near_expiry:
            result += "⚠️  即将到期合约 (30天内):\n"
            result += f"{'合约':<12} {'名称':<20} {'到期天数':<10} {'价格':<12} {'持仓量':<10}\n"
            result += "─" * 75 + "\n"
            
            near_expiry.sort(key=lambda x: x[2])  # 按到期天数排序
            for symbol, contract, days in near_expiry:
                price_jck = self.commodity_manager.convert_usd_to_jck(contract.current_price)
                name_short = contract.name[:18] if len(contract.name) > 18 else contract.name
                result += f"{symbol:<12} {name_short:<20} {days:<10} J${price_jck:<11.2f} {contract.open_interest:<10,}\n"
            
            result += "\n"
        
        # 显示主力合约
        result += "🔥 主力合约:\n"
        result += f"{'合约':<12} {'名称':<20} {'价格':<12} {'涨跌%':<8} {'成交量':<10}\n"
        result += "─" * 75 + "\n"
        
        # 按成交量排序，取前10个
        active_sorted = sorted(active_contracts, key=lambda x: x[1].volume_24h, reverse=True)[:10]
        for symbol, contract, days in active_sorted:
            price_jck = self.commodity_manager.convert_usd_to_jck(contract.current_price)
            change_str = f"{contract.change_24h_pct:+.2f}%"
            name_short = contract.name[:18] if len(contract.name) > 18 else contract.name
            result += f"{symbol:<12} {name_short:<20} J${price_jck:<11.2f} {change_str:<8} {contract.volume_24h:<10,}\n"
        
        return result
    
    def show_spot_list(self):
        """显示现货商品列表"""
        commodities = self.commodity_manager.get_commodities_by_type('spot')
        
        result = "\n🏪 现货商品列表\n"
        result += "═" * 85 + "\n"
        result += f"{'商品代码':<15} {'名称':<20} {'价格(JCK)':<12} {'涨跌%':<8} {'单位':<8} {'状态':<8}\n"
        result += "─" * 85 + "\n"
        
        # 按类别分组显示
        categories = {
            '贵金属': [],
            '能源': [],
            '工业金属': [],
            '农产品': []
        }
        
        for symbol, commodity in commodities.items():
            if any(metal in symbol for metal in ['XAU', 'XAG', 'XPT', 'XPD']):
                categories['贵金属'].append((symbol, commodity))
            elif any(energy in symbol for energy in ['WTI', 'BRENT', 'NATGAS']):
                categories['能源'].append((symbol, commodity))
            elif any(metal in symbol for metal in ['COPPER', 'ALUMINUM', 'ZINC', 'NICKEL']):
                categories['工业金属'].append((symbol, commodity))
            else:
                categories['农产品'].append((symbol, commodity))
        
        for category, items in categories.items():
            if items:
                result += f"\n{category}:\n"
                for symbol, commodity in items:
                    price_jck = self.commodity_manager.convert_usd_to_jck(commodity.current_price)
                    change_str = f"{commodity.change_24h_pct:+.2f}%"
                    status = "活跃" if commodity.is_trading_active() else "休市"
                    name_short = commodity.name[:18] if len(commodity.name) > 18 else commodity.name
                    
                    result += f"{symbol:<15} {name_short:<20} J${price_jck:<11.2f} {change_str:<8} {commodity.unit:<8} {status:<8}\n"
        
        result += "\n─" * 85 + "\n"
        result += f"总计: {len(commodities)} 种现货商品\n"
        result += "输入 'spot info <商品代码>' 查看详细信息\n"
        
        return result
    
    def show_spot_info(self, symbol):
        """显示现货商品详细信息"""
        commodity = self.commodity_manager.get_commodity_by_symbol(symbol)
        
        if not commodity or not hasattr(commodity, 'quality_grade'):
            return f"❌ 未找到现货商品: {symbol}"
        
        price_jck = self.commodity_manager.convert_usd_to_jck(commodity.current_price)
        
        result = f"\n🏪 现货商品详情 - {symbol}\n"
        result += "═" * 70 + "\n"
        result += f"商品名称: {commodity.name}\n"
        result += f"当前价格: J${price_jck:.4f} / {commodity.unit}\n"
        result += f"24小时涨跌: {commodity.change_24h_pct:+.2f}%\n"
        result += f"交易单位: {commodity.unit}\n"
        result += f"最小变动: {commodity.tick_size}\n\n"
        
        # 供需分析
        supply_demand = commodity.get_supply_demand_analysis()
        result += "供需分析:\n"
        result += "─" * 40 + "\n"
        result += f"库存状态: {supply_demand['inventory_status']}\n"
        result += f"需求趋势: {supply_demand['demand_trend']}\n"
        result += f"供应趋势: {supply_demand['supply_trend']}\n"
        result += f"库存水平: {supply_demand['inventory_level']}\n\n"
        
        # 质量信息
        result += "产品规格:\n"
        result += "─" * 40 + "\n"
        result += f"质量等级: {commodity.quality_grade}\n"
        result += f"产地信息: {commodity.origin}\n"
        result += f"存储条件: {commodity.storage_requirements}\n\n"
        
        # 交割信息
        delivery_info = commodity.get_delivery_info()
        result += "交割信息:\n"
        result += "─" * 40 + "\n"
        result += f"交割地点: {', '.join(delivery_info['locations'])}\n"
        result += f"交割费用: J${self.commodity_manager.convert_usd_to_jck(delivery_info['cost']):.2f}\n"
        result += f"交割时间: {delivery_info['timeframe']}\n"
        result += f"最小交割量: {delivery_info['min_quantity']} {commodity.unit}\n"
        
        return result
    
    def execute_spot_trade(self, symbol, trade_type, quantity, options):
        """执行现货交易"""
        result = self.commodity_manager.execute_trade(
            self.app.user_manager.current_user,
            symbol.upper(),
            trade_type,
            quantity,
            1  # 现货交易无杠杆
        )
        
        if result['success']:
            trade = result['trade_record']
            position = result['position']
            
            output = f"\n✅ 现货交易执行成功\n"
            output += "═" * 50 + "\n"
            output += f"交易ID: {trade['id']}\n"
            output += f"现货商品: {trade['symbol']}\n"
            output += f"操作: {'买入' if trade_type == 'buy' else '卖出'}\n"
            output += f"数量: {quantity} 单位\n"
            output += f"价格: J${trade['price_jck']:.4f}\n"
            output += f"总金额: J${trade['price_jck'] * quantity:.2f}\n\n"
            
            output += f"当前持仓:\n"
            output += f"数量: {position['quantity']} 单位\n"
            avg_price_jck = self.commodity_manager.convert_usd_to_jck(position['avg_price'])
            output += f"平均成本: J${avg_price_jck:.4f}\n"
            output += f"市值: J${avg_price_jck * abs(position['quantity']):.2f}\n"
            
            # 保存数据
            self.commodity_manager.save_data('data/commodity_data.json')
            
            return output
        else:
            return f"❌ 现货交易失败: {result['message']}"
    
    def show_delivery_info(self):
        """显示现货交割信息"""
        commodities = self.commodity_manager.get_commodities_by_type('spot')
        
        result = "\n🚚 现货交割信息\n"
        result += "═" * 80 + "\n"
        
        result += "主要交割仓库:\n"
        result += "─" * 50 + "\n"
        warehouses = [
            "上海期货交易所指定仓库",
            "大连商品交易所指定仓库", 
            "郑州商品交易所指定仓库",
            "香港金银业贸易场认可库房",
            "伦敦金属交易所认可仓库"
        ]
        for warehouse in warehouses:
            result += f"• {warehouse}\n"
        
        result += "\n交割费用标准:\n"
        result += "─" * 50 + "\n"
        result += f"{'商品类别':<15} {'交割费用':<15} {'仓储费/天':<15}\n"
        result += "─" * 50 + "\n"
        
        fee_info = [
            ("贵金属", "J$50/盎司", "J$0.1/盎司"),
            ("能源产品", "J$200/桶", "J$5/桶"),
            ("工业金属", "J$100/吨", "J$2/吨"),
            ("农产品", "J$50/吨", "J$1/吨")
        ]
        
        for category, delivery_fee, storage_fee in fee_info:
            result += f"{category:<15} {delivery_fee:<15} {storage_fee:<15}\n"
        
        result += "\n交割流程:\n"
        result += "─" * 50 + "\n"
        result += "1. 提交交割申请 (交割月前5个工作日)\n"
        result += "2. 缴纳交割保证金 (合约价值的10%)\n"
        result += "3. 买方资金到账确认\n"
        result += "4. 卖方商品入库检验\n"
        result += "5. 办理货权转移手续\n"
        result += "6. 买方提货或委托存储\n"
        
        result += "\n注意事项:\n"
        result += "─" * 50 + "\n"
        result += "• 实物交割需要满足最小交割量要求\n"
        result += "• 交割商品必须符合交易所质量标准\n"
        result += "• 交割地点仅限指定仓库\n"
        result += "• 个人投资者不能进行实物交割\n"
        
        return result
    
    def show_forex_info(self, symbol):
        """显示外汇对详细信息"""
        forex_pair = self.commodity_manager.get_commodity_by_symbol(symbol)
        
        if not forex_pair or not hasattr(forex_pair, 'base_currency'):
            return f"❌ 未找到外汇对: {symbol}"
        
        price_jck = self.commodity_manager.convert_usd_to_jck(forex_pair.current_price)
        bid_jck = self.commodity_manager.convert_usd_to_jck(forex_pair.bid_price)
        ask_jck = self.commodity_manager.convert_usd_to_jck(forex_pair.ask_price)
        
        result = f"\n🌍 外汇对详情 - {symbol}\n"
        result += "═" * 70 + "\n"
        result += f"货币对名称: {forex_pair.name}\n"
        result += f"基础货币: {forex_pair.base_currency}\n"
        result += f"报价货币: {forex_pair.quote_currency}\n"
        result += f"当前价格: J${price_jck:.5f}\n"
        result += f"买入价: J${bid_jck:.5f}\n"
        result += f"卖出价: J${ask_jck:.5f}\n"
        result += f"24小时涨跌: {forex_pair.change_24h_pct:+.2f}%\n\n"
        
        # 点差信息
        spread_pips = (forex_pair.ask_price - forex_pair.bid_price) / forex_pair.pip_size
        result += "交易信息:\n"
        result += "─" * 40 + "\n"
        result += f"点差: {spread_pips:.1f} 点\n"
        result += f"点值: {forex_pair.pip_size}\n"
        result += f"合约大小: {forex_pair.contract_size:,}\n"
        result += f"最小交易量: 0.01 手\n\n"
        
        # 交易时段
        sessions = forex_pair._get_session_info()
        result += "交易时段 (北京时间):\n"
        result += "─" * 40 + "\n"
        for session_name, session_info in sessions.items():
            activity_level = session_info['activity']
            activity_desc = {'low': '低', 'medium': '中', 'high': '高'}[activity_level]
            start_time = session_info['start'].strftime('%H:%M')
            end_time = session_info['end'].strftime('%H:%M')
            result += f"{session_name.title()}: {start_time}-{end_time} (活跃度: {activity_desc})\n"
        
        result += "\n保证金要求:\n"
        result += "─" * 40 + "\n"
        margin_100 = forex_pair.calculate_margin_required(1, 100)
        margin_200 = forex_pair.calculate_margin_required(1, 200)
        margin_500 = forex_pair.calculate_margin_required(1, 500)
        result += f"1:100杠杆: J${self.commodity_manager.convert_usd_to_jck(margin_100):.2f}/手\n"
        result += f"1:200杠杆: J${self.commodity_manager.convert_usd_to_jck(margin_200):.2f}/手\n"
        result += f"1:500杠杆: J${self.commodity_manager.convert_usd_to_jck(margin_500):.2f}/手\n"
        
        return result
    
    def show_trading_sessions(self):
        """显示全球外汇交易时段"""
        result = "\n🌍 全球外汇交易时段\n"
        result += "═" * 70 + "\n"
        
        result += "主要交易时段 (北京时间):\n"
        result += "─" * 50 + "\n"
        result += f"{'市场':<10} {'开盘时间':<10} {'收盘时间':<10} {'活跃度':<10} {'特点':<20}\n"
        result += "─" * 50 + "\n"
        
        sessions = [
            ("悉尼", "05:00", "14:00", "低", "亚洲开盘"),
            ("东京", "07:00", "16:00", "中", "亚洲主力"),
            ("伦敦", "15:00", "23:59", "高", "欧洲主力"),
            ("纽约", "20:00", "05:00", "高", "美洲主力")
        ]
        
        for market, open_time, close_time, activity, feature in sessions:
            result += f"{market:<10} {open_time:<10} {close_time:<10} {activity:<10} {feature:<20}\n"
        
        result += "\n重叠交易时段 (流动性最佳):\n"
        result += "─" * 50 + "\n"
        result += "• 东京-伦敦重叠: 15:00-16:00 (1小时)\n"
        result += "• 伦敦-纽约重叠: 20:00-23:59 (4小时)\n"
        result += "• 纽约-悉尼重叠: 05:00-05:00 (微重叠)\n"
        
        result += "\n最佳交易时间建议:\n"
        result += "─" * 50 + "\n"
        result += "🔥 伦敦-纽约重叠 (20:00-24:00)\n"
        result += "   • 流动性最高，点差最窄\n"
        result += "   • 适合所有主要货币对\n"
        result += "   • 重要经济数据发布时间\n\n"
        result += "⚠️  亚洲午间 (12:00-14:00)\n"
        result += "   • 流动性较低，点差较宽\n"
        result += "   • 适合长期趋势交易\n"
        result += "   • 避免短线交易\n\n"
        result += "🚫 周末市场休市\n"
        result += "   • 周六05:00-周一05:00\n"
        result += "   • 节假日可能影响交易时间\n"
        
        return result
    
    def show_commodity_overview(self):
        """显示商品市场概览"""
        overview = self.commodity_manager.get_market_overview()
        
        result = "\n💼 大宗商品市场概览\n"
        result += "═" * 80 + "\n"
        
        result += "市场统计:\n"
        result += "─" * 50 + "\n"
        total_count = overview['forex']['count'] + overview['futures']['count'] + overview['spot']['count']
        total_active = overview['forex']['active'] + overview['futures']['active'] + overview['spot']['active']
        
        result += f"总商品数量: {total_count}\n"
        result += f"当前活跃: {total_active}\n"
        result += f"外汇货币对: {overview['forex']['count']} (活跃: {overview['forex']['active']})\n"
        result += f"期货合约: {overview['futures']['count']} (活跃: {overview['futures']['active']})\n"
        result += f"现货商品: {overview['spot']['count']} (活跃: {overview['spot']['active']})\n\n"
        
        result += "各类别涨跌情况:\n"
        result += "─" * 50 + "\n"
        result += f"{'类别':<10} {'上涨':<8} {'下跌':<8} {'平盘':<8} {'涨跌比':<10}\n"
        result += "─" * 50 + "\n"
        
        for category in ['forex', 'futures', 'spot']:
            cat_data = overview[category]
            gainers = cat_data['gainers']
            losers = cat_data['losers']
            flat = cat_data['count'] - gainers - losers
            ratio = f"{gainers}/{losers}" if losers > 0 else f"{gainers}/0"
            
            cat_name = {'forex': '外汇', 'futures': '期货', 'spot': '现货'}[category]
            result += f"{cat_name:<10} {gainers:<8} {losers:<8} {flat:<8} {ratio:<10}\n"
        
        result += "\n市场热点:\n"
        result += "─" * 50 + "\n"
        
        # 获取涨跌幅排行数据
        movers = self.commodity_manager.get_top_movers(5)
        
        result += "今日涨幅榜 TOP 5:\n"
        for i, item in enumerate(movers['top_gainers'][:5], 1):
            result += f"{i}. {item['symbol']} ({item['name'][:15]}) +{item['change_pct']:.2f}%\n"
        
        result += "\n今日跌幅榜 TOP 5:\n"
        for i, item in enumerate(movers['top_losers'][:5], 1):
            result += f"{i}. {item['symbol']} ({item['name'][:15]}) {item['change_pct']:.2f}%\n"
        
        result += "\n成交活跃榜 TOP 5:\n"
        for i, item in enumerate(movers['volume_leaders'][:5], 1):
            volume_str = f"{item['volume']:,.0f}"
            result += f"{i}. {item['symbol']} ({item['name'][:15]}) {volume_str}\n"
        
        result += "\n使用命令:\n"
        result += "─" * 50 + "\n"
        result += "• commodity search <关键词> - 搜索商品\n"
        result += "• commodity movers - 完整涨跌榜\n"
        result += "• commodity positions - 查看持仓\n"
        result += "• forex/futures/spot - 进入专项交易\n"
        
        return result
    
    def search_commodities(self, keyword):
        """搜索商品"""
        results = []
        keyword_lower = keyword.lower()
        
        # 在所有商品中搜索
        for symbol, commodity in self.commodity_manager.all_commodities.items():
            if (keyword_lower in symbol.lower() or 
                keyword_lower in commodity.name.lower() or
                keyword_lower in getattr(commodity, 'underlying_asset', '').lower()):
                
                commodity_type = self.commodity_manager._get_commodity_type(symbol)
                results.append((symbol, commodity, commodity_type))
        
        if not results:
            return f"❌ 未找到包含 '{keyword}' 的商品"
        
        result = f"\n🔍 搜索结果: '{keyword}' (共{len(results)}个)\n"
        result += "═" * 80 + "\n"
        result += f"{'代码':<15} {'名称':<25} {'类型':<8} {'价格(JCK)':<12} {'涨跌%':<10}\n"
        result += "─" * 80 + "\n"
        
        for symbol, commodity, commodity_type in results[:20]:  # 限制显示20个
            price_jck = self.commodity_manager.convert_usd_to_jck(commodity.current_price)
            change_str = f"{commodity.change_24h_pct:+.2f}%"
            type_str = {'forex': '外汇', 'futures': '期货', 'spot': '现货'}.get(commodity_type, commodity_type)
            name_short = commodity.name[:23] if len(commodity.name) > 23 else commodity.name
            
            result += f"{symbol:<15} {name_short:<25} {type_str:<8} J${price_jck:<11.2f} {change_str:<10}\n"
        
        if len(results) > 20:
            result += f"\n... 还有 {len(results)-20} 个结果未显示\n"
        
        result += "\n使用方法:\n"
        result += "• <类型> info <代码> - 查看详情 (如: forex info EURUSD)\n"
        result += "• <类型> buy/sell <代码> <数量> - 交易\n"
        
        return result
    
    def show_trade_history(self):
        """显示交易历史"""
        history = self.commodity_manager.get_user_trade_history(self.app.user_manager.current_user, 20)
        
        if not history:
            return "\n📈 暂无交易历史\n"
        
        result = "\n📈 交易历史记录\n"
        result += "═" * 90 + "\n"
        result += f"{'时间':<12} {'商品':<12} {'类型':<8} {'操作':<6} {'数量':<10} {'价格(JCK)':<12} {'金额(JCK)':<12}\n"
        result += "─" * 90 + "\n"
        
        total_trades = 0
        total_volume_jck = 0
        
        for trade in history:
            timestamp = datetime.fromisoformat(trade['timestamp'])
            time_str = timestamp.strftime('%m-%d %H:%M')
            
            symbol = trade['symbol']
            commodity_type = {'forex': '外汇', 'futures': '期货', 'spot': '现货'}.get(trade['commodity_type'], trade['commodity_type'])
            trade_type = {'buy': '买入', 'sell': '卖出'}.get(trade['trade_type'], trade['trade_type'])
            quantity = trade['quantity']
            price_jck = trade['price_jck']
            
            # 计算交易金额
            if trade['commodity_type'] == 'forex':
                amount_jck = quantity * 100000 * price_jck / trade.get('leverage', 100)  # 外汇按手数计算
            else:
                amount_jck = quantity * price_jck
            
            result += f"{time_str:<12} {symbol:<12} {commodity_type:<8} {trade_type:<6} {quantity:<10.2f} J${price_jck:<11.4f} J${amount_jck:<11.2f}\n"
            
            total_trades += 1
            total_volume_jck += amount_jck
        
        result += "─" * 90 + "\n"
        result += f"总交易笔数: {total_trades}    总交易金额: J${total_volume_jck:,.2f}\n"
        
        return result
    
    def close_position(self, symbol):
        """平仓指定商品"""
        position_key = f"{self.app.user_manager.current_user}_{symbol.upper()}"
        
        if position_key not in self.commodity_manager.commodity_positions:
            return f"❌ 未找到 {symbol.upper()} 的持仓"
        
        position = self.commodity_manager.commodity_positions[position_key]
        quantity = abs(position['quantity'])
        
        if quantity == 0:
            return f"❌ {symbol.upper()} 持仓数量为0"
        
        # 确定平仓方向
        close_type = 'sell' if position['quantity'] > 0 else 'buy'
        
        result = self.commodity_manager.close_position(
            self.app.user_manager.current_user,
            symbol.upper(),
            quantity
        )
        
        if result['success']:
            trade = result['trade_record']
            
            output = f"\n✅ 平仓成功\n"
            output += "═" * 50 + "\n"
            output += f"商品: {symbol.upper()}\n"
            output += f"平仓数量: {quantity}\n"
            output += f"平仓价格: J${trade['price_jck']:.4f}\n"
            output += f"平仓金额: J${trade['price_jck'] * quantity:.2f}\n"
            
            # 如果有盈亏信息，显示盈亏
            if 'pnl' in result:
                pnl_jck = self.commodity_manager.convert_usd_to_jck(result['pnl'])
                pnl_str = f"J${pnl_jck:+.2f}"
                output += f"平仓盈亏: {pnl_str}\n"
            
            # 保存数据
            self.commodity_manager.save_data('data/commodity_data.json')
            
            return output
        else:
            return f"❌ 平仓失败: {result['message']}"
    
    def show_market_calendar(self):
        """显示市场时间"""
        from datetime import datetime, time
        
        result = "\n📅 市场交易时间\n"
        result += "═" * 70 + "\n"
        
        current_time = datetime.now()
        current_hour = current_time.hour
        
        result += f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)\n\n"
        
        # 外汇市场时间
        result += "🌍 外汇市场 (24小时交易):\n"
        result += "─" * 50 + "\n"
        
        forex_sessions = [
            ("悉尼", 5, 14, "低"),
            ("东京", 7, 16, "中"), 
            ("伦敦", 15, 24, "高"),
            ("纽约", 20, 5, "高")  # 跨日处理
        ]
        
        for market, start, end, activity in forex_sessions:
            if market == "纽约":
                if current_hour >= 20 or current_hour < 5:
                    status = "🟢 开市"
                else:
                    status = "🔴 休市"
            else:
                if start <= current_hour < end:
                    status = "🟢 开市"
                else:
                    status = "🔴 休市"
            
            if market == "纽约":
                time_str = f"20:00-05:00(次日)"
            else:
                time_str = f"{start:02d}:00-{end:02d}:00"
            
            result += f"{market:<8} {time_str:<15} 活跃度:{activity:<3} {status}\n"
        
        # 期货市场时间
        result += "\n📈 期货市场:\n"
        result += "─" * 50 + "\n"
        result += "日盘交易: 09:00-15:00\n"
        result += "夜盘交易: 21:00-02:30(次日)\n"
        
        # 判断期货市场状态
        if (9 <= current_hour < 15) or (21 <= current_hour <= 23) or (0 <= current_hour < 3):
            futures_status = "🟢 开市"
        else:
            futures_status = "🔴 休市"
        result += f"当前状态: {futures_status}\n"
        
        # 现货市场时间
        result += "\n🏪 现货市场:\n"
        result += "─" * 50 + "\n"
        result += "交易时间: 24小时连续交易\n"
        result += "结算时间: 每日 17:00\n"
        result += "当前状态: 🟢 开市\n"
        
        # 重要提醒
        result += "\n⚠️  重要提醒:\n"
        result += "─" * 50 + "\n"
        result += "• 周末外汇市场休市 (周六05:00-周一05:00)\n"
        result += "• 节假日可能影响交易时间\n"
        result += "• 重要经济数据发布时段流动性可能剧烈波动\n"
        result += "• 夜盘交易风险较高，请谨慎操作\n"
        
        # 下个重要时间点
        result += "\n⏰ 下个重要时间点:\n"
        result += "─" * 50 + "\n"
        
        next_events = []
        if current_hour < 9:
            next_events.append(("期货日盘开市", "09:00"))
        elif current_hour < 15:
            next_events.append(("期货日盘收市", "15:00"))
        elif current_hour < 17:
            next_events.append(("现货结算时间", "17:00"))
        elif current_hour < 20:
            next_events.append(("纽约外汇开市", "20:00"))
        elif current_hour < 21:
            next_events.append(("期货夜盘开市", "21:00"))
        else:
            next_events.append(("期货夜盘收市", "02:30(次日)"))
        
        for event, time_str in next_events:
            result += f"• {event}: {time_str}\n"
        
        return result