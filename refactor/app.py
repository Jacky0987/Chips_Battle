import tkinter as tk
from datetime import datetime

# Import modules
from user_manager import UserManager
from login_window import LoginWindow
from core.market_data import MarketDataManager
from core.trading_engine import TradingEngine
from core.achievement_system import AchievementSystem
# MainWindow removed - using ProfessionalTerminal only
from commands.command_processor import CommandProcessor
from features.analysis import AnalysisFeatures
from features.app_market import AppMarket
from admin.admin_manager import AdminManager

# 导入新的系统
from home import HomeManager


class StockTradingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # 界面模式选择
        # Always use professional terminal interface
        
        # Initialize managers
        self.user_manager = UserManager()
        self.market_data = MarketDataManager()
        self.trading_engine = TradingEngine(self.market_data)
        self.achievement_system = AchievementSystem(self.market_data.achievement_definitions)
        self.admin_manager = AdminManager(self.market_data, self.user_manager)
        
        # Initialize currency system
        from core.currency_system import CurrencyManager, ForexTradingEngine
        self.currency_manager = CurrencyManager()
        self.forex_engine = ForexTradingEngine(self.currency_manager)
        
        # User data
        self.user_data = None
        self.cash = 100000.0
        self.portfolio = {}
        self.transaction_history = []
        self.achievements = []
        self.level = 1
        self.experience = 0
        self.total_profit = 0
        self.best_trade = 0
        self.trades_count = 0

        # Command system
        self.command_history = []
        self.history_index = -1
        self.admin_mode = False

        # Initialize UI and processors after login
        self.gui = None
        self.command_processor = None
        self.analysis_features = None

        # Show login first
        self.show_login()

    def setup_window(self):
        self.root.title("Stock Trading Simulator - CLI Interface")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0C0C0C')

    def init_managers(self):
        self.bank_manager = BankManager(self)
        self.company_manager = CompanyManager(self)
        self.home_manager = HomeManager(self)

    def show_login(self):
        """显示bash样式登录"""
        # 使用专业金融终端界面
        try:
            from gui.professional_terminal import ProfessionalTerminal
            self.gui = ProfessionalTerminal(self)
            print("✅ 专业金融终端界面已启用")
        except ImportError as e:
            print(f"❌ 专业终端界面加载失败: {e}")
            raise e
            
        # 启动登录流程
        login_window = LoginWindow(self.user_manager, self.on_login_success)
        login_window.start_bash_login(self.gui)

    def on_login_success(self):
        """登录成功回调"""
        # Load user data
        self.user_data = self.user_manager.get_user_data()
        if self.user_data:
            self.cash = self.user_data.get('cash', 100000.0)
            self.portfolio = self.user_data.get('portfolio', {})
            self.transaction_history = self.user_data.get('transaction_history', [])
            self.achievements = self.user_data.get('achievements', [])
            self.level = self.user_data.get('level', 1)
            self.experience = self.user_data.get('experience', 0)
            self.total_profit = self.user_data.get('total_profit', 0)
            self.best_trade = self.user_data.get('best_trade', 0)
            self.trades_count = self.user_data.get('trades_count', 0)

        # Initialize processors (GUI already initialized in show_login)
        self.command_processor = CommandProcessor(self)
        self.analysis_features = AnalysisFeatures(self.market_data, self.trading_engine)
        self.app_market = AppMarket(self)
        self.home_manager = HomeManager(self)
        
        # Initialize commodity trading system
        from features.commodity_trading import CommodityTrading
        self.commodity_trading = CommodityTrading(self)
        
        # Initialize bank and company systems
        from bank.bank_manager import BankManager
        from company.company_manager import CompanyManager
        self.bank_manager = BankManager(self)
        self.company_manager = CompanyManager(self)

        # 绑定正常的命令处理事件
        self.gui.command_entry.bind('<Return>', self.process_command)
        
        # 更新标题显示用户信息
        self.gui.update_title()

        # Start background threads
        self.market_data.start_price_update_thread()
        self.market_data.start_market_events_thread(self.gui.display_market_event)

        # Display welcome message
        self.display_welcome()
        self.check_login_streak()

    def display_welcome(self):
        """显示欢迎信息"""
        welcome_text = f"""
欢迎回来，{self.user_manager.current_user}！

当前状态:  等级: {self.level}  经验: {self.experience}
输入 'help' 查看可用命令。

"""
        self.print_to_output(welcome_text)

    def check_login_streak(self):
        """检查登录连击奖励"""
        login_bonus, login_message = self.achievement_system.check_login_streak(self.user_data)
        if login_bonus > 0:
            self.cash += login_bonus
            self.print_to_output(login_message, '#FFD700')

    def print_to_output(self, text, color='#00FF00'):
        """输出到终端"""
        if self.gui:
            self.gui.print_to_output(text, color)

    def process_command(self, event):
        """处理命令输入"""
        command = self.gui.get_command_input()
        if not command:
            return

        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = -1

        self.gui.clear_command_input()
        
        # 首先检查是否有活跃的向导
        if hasattr(self.command_processor, 'active_wizard') and self.command_processor.active_wizard:
            # 如果有活跃向导，将输入传递给向导处理
            wizard_handled = self.command_processor.process_wizard_input(command)
            if wizard_handled:
                return
        
        # 正常命令处理
        self.command_processor.process_command(command)

    # Trading methods
    def buy_stock(self, symbol, quantity, order_type="market", limit_price=None):
        """买入股票"""
        success, message, new_cash, *extra = self.trading_engine.buy_stock(
            self.portfolio, symbol, quantity, self.cash, order_type, limit_price
        )
        
        if success:
            self.cash = new_cash
            if order_type == "limit" and "挂单成功" in message:
                # 限价单创建成功
                self.print_to_output(message, '#FFAA00')
            else:
                # 交易立即执行
                transaction = extra[0]
                self.transaction_history.append(transaction)
                self.trades_count += 1
                self.experience += 10
                
                # 更新今日交易计数
                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')
                if self.user_data.get('last_trade_date') != today:
                    self.user_data['today_trades_count'] = 1
                    self.user_data['last_trade_date'] = today
                else:
                    self.user_data['today_trades_count'] = self.user_data.get('today_trades_count', 0) + 1
                
                # 检查时间相关成就
                current_hour = datetime.now().hour
                if current_hour < 6:
                    self.user_data['early_morning_trades'] = self.user_data.get('early_morning_trades', 0) + 1
                elif current_hour >= 23:
                    self.user_data['late_night_trades'] = self.user_data.get('late_night_trades', 0) + 1
                
                self.print_to_output(message, '#00FF00')
                self.check_achievements()
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def sell_stock(self, symbol, quantity, order_type="market", limit_price=None):
        """卖出股票"""
        success, message, new_cash, *extra = self.trading_engine.sell_stock(
            self.portfolio, symbol, quantity, self.cash, order_type, limit_price
        )
        
        if success:
            self.cash = new_cash
            if order_type == "limit" and "挂单成功" in message:
                # 限价单创建成功
                self.print_to_output(message, '#FFAA00')
            else:
                # 交易立即执行
                transaction = extra[0]
                trade_profit = extra[1]
                
                self.transaction_history.append(transaction)
                self.trades_count += 1
                self.experience += 10
                self.total_profit += trade_profit
                if trade_profit > self.best_trade:
                    self.best_trade = trade_profit
                
                self.print_to_output(message, '#00FF00')
                self.check_achievements()
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def short_sell(self, symbol, quantity, order_type="market", limit_price=None):
        """做空股票"""
        success, message, new_cash, *extra = self.trading_engine.short_sell(
            self.portfolio, symbol, quantity, self.cash, order_type, limit_price
        )
        
        if success:
            self.cash = new_cash
            if order_type == "limit" and "挂单成功" in message:
                # 限价单创建成功
                self.print_to_output(message, '#FFAA00')
            else:
                # 交易立即执行
                transaction = extra[0]
                self.transaction_history.append(transaction)
                self.trades_count += 1
                self.experience += 15  # 做空给更多经验
                
                # 更新做空交易统计
                self.user_data['short_trades_count'] = self.user_data.get('short_trades_count', 0) + 1
                
                self.print_to_output(message, '#00AAFF')
                self.check_achievements()
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def cover_short(self, symbol, quantity):
        """平仓做空"""
        success, message, new_cash, *extra = self.trading_engine.cover_short(
            self.portfolio, symbol, quantity, self.cash
        )
        
        if success:
            self.cash = new_cash
            transaction = extra[0]
            trade_profit = extra[1]
            
            self.transaction_history.append(transaction)
            self.trades_count += 1
            self.experience += 15
            self.total_profit += trade_profit
            if trade_profit > self.best_trade:
                self.best_trade = trade_profit
            
            self.print_to_output(message, '#00AAFF')
            self.check_achievements()
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def create_stop_loss(self, symbol, quantity, stop_price):
        """创建止损单"""
        success, message, *extra = self.trading_engine.create_stop_loss_order(
            self.portfolio, symbol, quantity, stop_price, self.cash
        )
        
        if success:
            # 更新止损单使用统计
            self.user_data['stop_loss_used'] = self.user_data.get('stop_loss_used', 0) + 1
            self.print_to_output(message, '#FF6600')
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def create_take_profit(self, symbol, quantity, target_price):
        """创建止盈单"""
        success, message, *extra = self.trading_engine.create_take_profit_order(
            self.portfolio, symbol, quantity, target_price, self.cash
        )
        
        if success:
            # 更新止盈单使用统计
            self.user_data['take_profit_used'] = self.user_data.get('take_profit_used', 0) + 1
            self.print_to_output(message, '#66FF00')
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def cancel_order(self, order_id):
        """取消挂单"""
        success, message = self.trading_engine.cancel_order(self.portfolio, order_id)
        
        if success:
            self.print_to_output(message, '#FFFF00')
            self.save_game_data()
        else:
            self.print_to_output(message, '#FF0000')

    def check_pending_orders(self):
        """检查并执行挂单"""
        try:
            executed_orders, new_cash = self.trading_engine.check_pending_orders(self.portfolio, self.cash)
            
            if executed_orders:
                self.cash = new_cash
                for order in executed_orders:
                    order_type_name = {
                        'BUY': '限价买入',
                        'SELL': '限价卖出', 
                        'SHORT': '限价做空',
                        'STOP_LOSS': '止损',
                        'TAKE_PROFIT': '止盈'
                    }.get(order['order_type'], order['order_type'])
                    
                    message = f"🔔 {order_type_name}订单已执行: {order['symbol']} {order['quantity']}股 @ ${order['executed_price']:.2f}"
                    self.print_to_output(message, '#00FFFF')
                    
                    # 更新交易统计
                    self.trades_count += 1
                    self.experience += 10
                    
                    # 更新限价单执行统计
                    if order['order_type'] in ['BUY', 'SELL', 'SHORT']:
                        self.user_data['limit_orders_executed'] = self.user_data.get('limit_orders_executed', 0) + 1
                
                self.check_achievements()  # 检查成就
                self.save_game_data()
        except Exception as e:
            print(f"检查挂单时出错: {e}")

    def show_pending_orders(self):
        """显示挂单列表"""
        if 'pending_orders' not in self.portfolio or not self.portfolio['pending_orders']:
            self.print_to_output("当前没有挂单", '#FFFF00')
            return

        orders_text = """
挂单列表

订单号   | 类型     | 股票   | 数量 | 触发价格 | 状态   | 创建时间
------------------------------------------------------------------------"""

        for order in self.portfolio['pending_orders']:
            order_type_name = {
                'BUY': '限价买入',
                'SELL': '限价卖出',
                'SHORT': '限价做空',
                'STOP_LOSS': '止损',
                'TAKE_PROFIT': '止盈'
            }.get(order['order_type'], order['order_type'])
            
            trigger_price = order.get('limit_price') or order.get('trigger_price')
            
            orders_text += f"\n{order['id']:<8} | {order_type_name:<8} | {order['symbol']:<6} | {order['quantity']:>4} | ${trigger_price:>8.2f} | {order['status']:<6} | {order['created_time'][:16]}"

        orders_text += f"\n\n总挂单数: {len(self.portfolio['pending_orders'])}"
        
        self.print_to_output(orders_text, '#AAFFFF')

    def check_achievements(self):
        """检查成就"""
        new_achievements, reward, exp_gained, messages = self.achievement_system.check_achievements(
            self.user_data, self.portfolio, self.cash, self.trades_count, self.total_profit
        )
        
        for achievement_id in new_achievements:
            self.achievements.append(achievement_id)
        
        if reward > 0:
            self.cash += reward
            self.experience += exp_gained
            for message in messages:
                self.print_to_output(message, '#FFD700')
        
        # Check level up
        self.level, self.experience, level_reward, level_messages = self.achievement_system.check_level_up(
            self.level, self.experience
        )
        
        if level_reward > 0:
            self.cash += level_reward
            for message in level_messages:
                self.print_to_output(message, '#FFD700')

    # Display methods
    def show_balance(self):
        """显示余额"""
        total_value = self.trading_engine.calculate_total_value(self.cash, self.portfolio)
        profit_loss = total_value - 100000

        balance_text = f"""
账户信息

现金余额: ${self.cash:,.2f}
投资组合价值: ${total_value - self.cash:,.2f}
总资产: ${total_value:,.2f}
盈亏: ${profit_loss:,.2f} ({(profit_loss / 100000) * 100:+.2f}%)

用户等级: {self.level}
当前经验: {self.experience}
交易次数: {self.trades_count}
最佳交易: ${self.best_trade:+,.2f}
"""
        self.print_to_output(balance_text)

    def show_stock_list(self):
        """显示股票列表"""
        list_text = """
    股票列表

    代码   | 公司名称       | 价格      | 涨跌额  | 涨跌幅   | 行业          | 市盈率 | 成交量      | 股息率
    ---------------------------------------------------------------------------------------------"""

        for symbol, data in self.market_data.stocks.items():
            price = data['price']
            change = data['change']
            change_pct = (change / (price - change)) * 100 if (price - change) != 0 else 0
            change_str = f"{change:+.2f}"
            change_pct_str = f"{change_pct:+.2f}%"
            pe_ratio = f"{data['pe_ratio']:.1f}" if data['pe_ratio'] else "N/A"
            volume = f"{data['volume']:,}"
            dividend_yield = f"{data['dividend_yield'] * 100:.1f}%" if data['dividend_yield'] else "0.0%"

            list_text += f"\n{symbol:<6} | {data['name']:<13} | ${price:>7.2f} | {change_str:>7} | {change_pct_str:>8} | {data['sector']:<12} | {pe_ratio:>6} | {volume:>11} | {dividend_yield:>6}"

        self.print_to_output(list_text)

    def show_quote(self, symbol):
        """显示股票详情"""
        if symbol not in self.market_data.stocks:
            self.print_to_output(f"错误: 股票代码 {symbol} 不存在", '#FF0000')
            return

        data = self.market_data.stocks[symbol]
        price = data['price']
        change = data['change']
        change_pct = (change / (price - change)) * 100 if (price - change) != 0 else 0

        # Calculate 52-week high/low from price history
        high_52w = max(data['price_history'])
        low_52w = min(data['price_history'])

        # Calculate moving averages
        sma_20 = sum(data['price_history'][-20:]) / min(len(data['price_history']), 20)
        sma_50 = sum(data['price_history'][-50:]) / min(len(data['price_history']), 50) if len(
            data['price_history']) >= 50 else sma_20

        # 格式化可能为None的值
        pe_ratio_str = f"{data['pe_ratio']:.1f}" if data['pe_ratio'] else 'N/A'
        eps_str = f"${data['eps']:.2f}" if data['eps'] else 'N/A'

        quote_text = f"""
    {symbol} - {data['name']}

    基本信息:
      当前价格: ${price:.2f}
      今日变动: ${change:+.2f} ({change_pct:+.2f}%)
      52周最高: ${high_52w:.2f}
      52周最低: ${low_52w:.2f}
      成交量: {data['volume']:,}
      市值: ${data['market_cap']:,}
      市盈率: {pe_ratio_str}
      股息率: {data['dividend_yield'] * 100:.1f}%
      Beta: {data['beta']:.2f}
      每股收益: {eps_str}
      行业: {data['sector']}
      波动率: {data['volatility'] * 100:.1f}%
      最后更新: {data['last_updated'][:19]}

    技术指标:
      20日均线: ${sma_20:.2f}
      50日均线: ${sma_50:.2f}

    持仓信息:
      当前持股: {self.portfolio.get(symbol, {'quantity': 0})['quantity']} 股
      平均成本: ${self.portfolio.get(symbol, {'avg_cost': 0})['avg_cost']:.2f}
      持仓价值: ${self.portfolio.get(symbol, {'quantity': 0})['quantity'] * price:,.2f}
      未实现盈亏: ${(self.portfolio.get(symbol, {'quantity': 0})['quantity'] * price -
                     self.portfolio.get(symbol, {'quantity': 0})['quantity'] *
                     self.portfolio.get(symbol, {'avg_cost': 0})['avg_cost']):+,.2f}
    """
        self.print_to_output(quote_text)

    def show_portfolio(self):
        """显示投资组合"""
        # 过滤掉pending_orders
        portfolio_positions = {k: v for k, v in self.portfolio.items() if k != 'pending_orders'}
        
        # 获取大宗商品持仓
        commodity_positions = []
        if hasattr(self, 'commodity_trading') and hasattr(self.user_manager, 'current_user') and self.user_manager.current_user:
            commodity_positions = self.commodity_trading.commodity_manager.get_user_positions(self.user_manager.current_user)
        
        if not portfolio_positions and not commodity_positions:
            self.print_to_output("当前无持仓。", '#FFFF00')
            return

        portfolio_text = """
投资组合详情
═══════════════════════════════════════════════════════════════════════════════════════

📈 股票持仓:
代码   | 仓位类型 | 数量  | 当前价格 | 平均成本 | 市值      | 盈亏      | 盈亏%   | 占比
------------------------------------------------------------------------------------------"""

        total_value = self.trading_engine.calculate_total_value(self.cash, self.portfolio)
        portfolio_value = 0

        # 显示股票持仓
        if portfolio_positions:
            for symbol, data in portfolio_positions.items():
                current_price = self.market_data.stocks[symbol]['price']
                quantity = data['quantity']
                avg_cost = data['avg_cost']
                position_type = "多头" if quantity > 0 else "空头"
                
                if quantity > 0:  # 多头仓位
                    market_value = current_price * quantity
                    portfolio_value += market_value
                    profit_loss = market_value - (avg_cost * quantity)
                    profit_loss_pct = (profit_loss / (avg_cost * quantity)) * 100 if avg_cost * quantity > 0 else 0
                    weight = (market_value / total_value) * 100
                else:  # 空头仓位
                    short_quantity = abs(quantity)
                    market_value = avg_cost * short_quantity  # 原始卖出金额
                    # 空头的盈亏计算：卖出价格 - 当前价格
                    profit_loss = (avg_cost - current_price) * short_quantity
                    profit_loss_pct = (profit_loss / market_value) * 100 if market_value > 0 else 0
                    weight = (market_value / total_value) * 100

                portfolio_text += f"\n{symbol:<6} | {position_type:<8} | {abs(quantity):>4} | J${current_price:>7.2f} | J${avg_cost:>7.2f} | J${market_value:>8.2f} | J${profit_loss:>+8.2f} | {profit_loss_pct:>+6.2f}% | {weight:>5.1f}%"
        else:
            portfolio_text += "\n(暂无股票持仓)"

        # 显示大宗商品持仓
        if commodity_positions:
            portfolio_text += "\n\n💰 大宗商品持仓:\n"
            portfolio_text += "代码         | 类型 | 数量      | 平均成本     | 当前价格     | 盈亏        | 保证金\n"
            portfolio_text += "─" * 85 + "\n"
            
            total_commodity_pnl = 0
            for position in commodity_positions:
                symbol = position['symbol']
                commodity_type = self.commodity_trading.commodity_manager._get_commodity_type(symbol)
                quantity = position['quantity']
                avg_price = position['avg_price']
                margin_used = position['margin_used']
                unrealized_pnl = position.get('unrealized_pnl', 0)
                total_commodity_pnl += unrealized_pnl
                
                # 获取当前价格
                commodity = self.commodity_trading.commodity_manager.get_commodity_by_symbol(symbol)
                current_price_jck = self.commodity_trading.commodity_manager.convert_usd_to_jck(commodity.current_price) if commodity else 0
                avg_price_jck = self.commodity_trading.commodity_manager.convert_usd_to_jck(avg_price)
                
                type_str = {'forex': '外汇', 'futures': '期货', 'spot': '现货'}.get(commodity_type, commodity_type)
                
                portfolio_text += f"{symbol:<12} | {type_str:<4} | {quantity:>8.2f} | J${avg_price_jck:>10.2f} | J${current_price_jck:>10.2f} | J${unrealized_pnl:>+9.2f} | J${margin_used:>8.2f}\n"
            
            portfolio_text += f"\n大宗商品总盈亏: J${total_commodity_pnl:+,.2f}"

        portfolio_text += f"\n\n💵 资产汇总:\n现金余额: J${self.cash:.2f}"
        portfolio_text += f"\n总资产: J${total_value:.2f}"
        
        # 显示挂单信息
        if 'pending_orders' in self.portfolio and self.portfolio['pending_orders']:
            portfolio_text += f"\n\n📋 当前挂单: {len(self.portfolio['pending_orders'])}个 (输入 'orders' 查看详情)"

        self.print_to_output(portfolio_text)

    def show_history(self):
        """显示交易历史"""
        if not self.transaction_history:
            self.print_to_output("暂无交易记录。", '#FFFF00')
            return

        history_text = """
交易历史记录

时间     | 类型 | 代码   | 数量 | 价格     | 总额
-----------------------------------------------------"""

        recent_transactions = self.transaction_history[-15:]  # 显示最近15条

        for transaction in recent_transactions:
            time_str = transaction['time'].split()[1][:8]  # 只显示时间部分
            history_text += f"\n{time_str} | {transaction['type']:<4} | {transaction['symbol']:<6} | {transaction['quantity']:>4} | ${transaction['price']:>7.2f} | ${transaction['total']:>8.2f}"

        history_text += f"\n\n总交易次数: {len(self.transaction_history)}"
        history_text += f"\n显示最近: {len(recent_transactions)}条记录"

        self.print_to_output(history_text)

    # Analysis methods
    def show_market_overview(self):
        """显示市场概况"""
        result = self.analysis_features.show_market_overview()
        self.print_to_output(result, '#FFFF00')

    def show_market_news(self):
        """显示市场新闻"""
        result = self.analysis_features.show_market_news()
        self.print_to_output(result, '#FFAA00')

    def show_technical_analysis(self, symbol):
        """显示技术分析"""
        result = self.analysis_features.show_technical_analysis(symbol)
        if "错误" in result:
            self.print_to_output(result, '#FF0000')
        else:
            self.print_to_output(result, '#00FF00')

    def show_sector_analysis(self):
        """显示行业分析"""
        result = self.analysis_features.show_sector_analysis()
        self.print_to_output(result, '#AAFF00')

    def show_risk_assessment(self):
        """显示风险评估"""
        result = self.analysis_features.show_risk_assessment(self.cash, self.portfolio)
        self.print_to_output(result, '#FFAA00')

    # Placeholder methods for features
    def show_leaderboard(self, sort_by='total'):
        """显示本地用户排行榜
        
        Args:
            sort_by: 排序方式 ('total'=总资产, 'profit'=收益率, 'level'=等级, 'trades'=交易次数)
        """
        # 加载所有用户数据
        all_users = self.user_manager.load_users()
        
        if not all_users:
            self.print_to_output("暂无用户数据", '#FFFF00')
            return
        
        # 计算每个用户的排行榜数据
        leaderboard_data = []
        for username, user_info in all_users.items():
            game_data = user_info.get('game_data', {})
            if not game_data:
                continue
                
            cash = game_data.get('cash', 100000.0)
            portfolio = game_data.get('portfolio', {})
            level = game_data.get('level', 1)
            trades_count = game_data.get('trades_count', 0)
            total_profit = game_data.get('total_profit', 0)
            created_date = user_info.get('created_date', '')
            
            # 计算总资产
            total_value = cash
            for symbol, data in portfolio.items():
                if symbol == 'pending_orders':
                    continue
                if symbol in self.market_data.stocks and isinstance(data, dict):
                    quantity = data.get('quantity', 0)
                    current_price = self.market_data.stocks[symbol]['price']
                    
                    if quantity > 0:  # 多头仓位
                        total_value += current_price * quantity
                    else:  # 空头仓位的浮动盈亏
                        avg_cost = data.get('avg_cost', current_price)
                        short_quantity = abs(quantity)
                        total_value += (avg_cost - current_price) * short_quantity
            
            # 计算收益率
            profit_loss = total_value - 100000
            profit_rate = (profit_loss / 100000) * 100
            
            # 计算交易天数
            if created_date:
                try:
                    from datetime import datetime
                    if isinstance(created_date, str):
                        create_time = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    else:
                        create_time = created_date
                    days_since_created = (datetime.now() - create_time).days + 1
                except:
                    days_since_created = 1
            else:
                days_since_created = 1
            
            leaderboard_data.append({
                'username': username,
                'total_value': total_value,
                'profit_rate': profit_rate,
                'level': level,
                'trades_count': trades_count,
                'total_profit': total_profit,
                'days_active': days_since_created,
                'avg_daily_profit': total_profit / max(days_since_created, 1)
            })
        
        # 根据排序方式排序
        sort_configs = {
            'total': ('total_value', '总资产'),
            'profit': ('profit_rate', '收益率'), 
            'level': ('level', '等级'),
            'trades': ('trades_count', '交易次数'),
            'daily': ('avg_daily_profit', '日均收益')
        }
        
        if sort_by not in sort_configs:
            sort_by = 'total'
        
        sort_key, sort_name = sort_configs[sort_by]
        leaderboard_data.sort(key=lambda x: x[sort_key], reverse=True)
        
        # 生成排行榜文本
        leaderboard_text = f"""
排行榜 - 本地交易精英 (按{sort_name}排序)

排名 | 用户名           | 总资产         | 收益率      | 等级 | 交易次数 | 日均收益
-------------------------------------------------------------------------------------"""

        current_user_rank = 0
        for i, user_data in enumerate(leaderboard_data[:10], 1):  # 显示前10名
            username = user_data['username']
            total_value = user_data['total_value']
            profit_rate = user_data['profit_rate']
            level = user_data['level']
            trades_count = user_data['trades_count']
            avg_daily_profit = user_data['avg_daily_profit']
            
            # 标记当前用户
            if username == self.user_manager.current_user:
                current_user_rank = i
                username_display = f"★{username}"
            else:
                username_display = username
            
            leaderboard_text += f"\n{i:>2}   | {username_display:<15} | ${total_value:>12,.0f} | {profit_rate:>+8.1f}% | {level:>2}   | {trades_count:>6}   | ${avg_daily_profit:>+8.0f}"

        # 如果当前用户不在前10名，显示其排名
        if current_user_rank == 0:
            for i, user_data in enumerate(leaderboard_data, 1):
                if user_data['username'] == self.user_manager.current_user:
                    current_user_rank = i
                    break
        
        # 添加统计信息
        if leaderboard_data:
            best_performer = leaderboard_data[0]
            total_users = len(leaderboard_data)
            avg_profit = sum(u['total_profit'] for u in leaderboard_data) / total_users
            
            leaderboard_text += f"""

📊 统计信息:
  总用户数: {total_users}
  您的排名: 第{current_user_rank}名 {'🏆' if current_user_rank <= 3 else ''}
  平均收益: ${avg_profit:,.0f}
  
🏆 榜首信息:
  用户名: {best_performer['username']}
  总资产: ${best_performer['total_value']:,.0f}
  收益率: {best_performer['profit_rate']:+.1f}%
  等级: {best_performer['level']}
  
💡 提升排名的方法:
  - 增加交易频率获得更多经验
  - 合理配置投资组合降低风险
  - 利用高级交易功能如限价单、止损止盈
  - 关注市场动态和技术分析
  - 完成成就获得额外奖励
"""
        else:
            leaderboard_text += "\n\n暂无排行榜数据"
        
        self.print_to_output(leaderboard_text, '#FFFF00')

    def show_achievements(self, category=None, show_progress=False):
        """显示成就系统"""
        if show_progress:
            self.show_achievement_progress()
            return
        
        if category:
            self.show_achievements_by_category(category)
            return
            
        # 获取成就统计
        stats = self.achievement_system.get_achievement_statistics(self.user_data)
        categories = self.achievement_system.get_achievements_by_category(self.user_data)
        
        achievements_text = f"""
═══════════════════════════════════════════════════════════════════
                         🏆 成就系统总览 🏆                         
═══════════════════════════════════════════════════════════════════

📊 整体统计:
  完成度: {stats['completion_rate']:.1f}% ({stats['completed']}/{stats['total']})
  总奖励: ${stats['total_reward']:,}
  总经验: {stats['total_experience']:,}

🏅 等级分布:
  🥉 铜牌成就: {stats['tier_stats']['bronze']}个
  🥈 银牌成就: {stats['tier_stats']['silver']}个  
  🥇 金牌成就: {stats['tier_stats']['gold']}个

📂 分类概览:"""

        for category, data in categories.items():
            completion = len(data['unlocked']) / data['total'] * 100 if data['total'] > 0 else 0
            achievements_text += f"\n  {data['name']}: {len(data['unlocked'])}/{data['total']} ({completion:.0f}%)"

        # 显示即将完成的成就
        nearly_completed = self.achievement_system.get_nearly_completed_achievements(
            self.user_data, self.portfolio, self.cash, self.trades_count, self.total_profit, threshold=70
        )
        
        if nearly_completed:
            achievements_text += "\n\n🎯 即将完成:"
            for achievement in nearly_completed[:3]:
                tier_emoji = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇'}.get(achievement['tier'], '🏆')
                achievements_text += f"\n  {tier_emoji} {achievement['name']} - {achievement['progress']:.0f}% ({achievement['current']}/{achievement['target']})"

        achievements_text += f"""

🎮 使用指南:
  achievements progress     - 查看成就进度详情
  achievements <类别>       - 查看特定类别成就
  
📚 可用类别:
  trading, profit, portfolio, wealth, loyalty, risk, 
  advanced, banking, skill, special, progress, meta

💡 提示: 完成更多成就可以获得丰厚奖励和经验值！
═══════════════════════════════════════════════════════════════════
"""
        self.print_to_output(achievements_text, '#FFAA00')

    def show_achievement_progress(self):
        """显示成就进度详情"""
        progress_list = self.achievement_system.get_achievement_progress(
            self.user_data, self.portfolio, self.cash, self.trades_count, self.total_profit
        )
        
        if not progress_list:
            self.print_to_output("🎉 恭喜！您已完成所有可见成就！", '#00FF00')
            return
        
        # 按进度排序
        progress_list.sort(key=lambda x: x['progress'], reverse=True)
        
        progress_text = """
🎯 成就进度追踪

进度 | 成就名称                | 当前/目标         | 等级
-----|------------------------|------------------|------"""

        for achievement in progress_list[:15]:  # 显示前15个
            if not achievement['hidden']:
                tier_emoji = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇'}.get(achievement['tier'], '🏆')
                progress_bar = self.create_progress_bar(achievement['progress'])
                progress_text += f"\n{achievement['progress']:>3.0f}% | {achievement['name']:<22} | {achievement['current']:>8}/{achievement['target']:<8} | {tier_emoji}"
                if achievement['progress'] >= 90:
                    progress_text += " ⚡"

        progress_text += f"\n\n💡 提示: 即将完成的成就标记为 ⚡"
        self.print_to_output(progress_text, '#AAFFFF')

    def show_achievements_by_category(self, category):
        """显示特定类别的成就"""
        categories = self.achievement_system.get_achievements_by_category(self.user_data)
        
        if category not in categories:
            valid_categories = list(categories.keys())
            self.print_to_output(f"无效的成就类别: {category}", '#FF0000')
            self.print_to_output(f"可用类别: {', '.join(valid_categories)}", '#FFAA00')
            return
        
        cat_data = categories[category]
        category_text = f"""
{cat_data['name']} 成就详情

完成度: {len(cat_data['unlocked'])}/{cat_data['total']} ({len(cat_data['unlocked'])/cat_data['total']*100:.0f}%)

✅ 已解锁成就:"""

        for achievement in cat_data['unlocked']:
            tier_emoji = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇'}.get(achievement['tier'], '🏆')
            category_text += f"\n  {tier_emoji} {achievement['name']} - {achievement['desc']}"
            category_text += f"\n     奖励: ${achievement['reward']:,} + {achievement['experience']}经验"

        if cat_data['locked']:
            category_text += "\n\n⏳ 待解锁成就:"
            for achievement in cat_data['locked']:
                tier_emoji = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇'}.get(achievement['tier'], '🏆')
                category_text += f"\n  {tier_emoji} {achievement['name']} - {achievement['desc']}"
                category_text += f"\n     奖励: ${achievement['reward']:,} + {achievement['experience']}经验"

        self.print_to_output(category_text, '#AAFFFF')

    def create_progress_bar(self, progress, width=10):
        """创建进度条"""
        filled = int(progress / 100 * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"{bar} {progress:.0f}%"

    def show_profile(self):
        """显示个人资料"""
        total_value = self.trading_engine.calculate_total_value(self.cash, self.portfolio)
        profit_loss = total_value - 100000

        profile_text = f"""
个人资料 - {self.user_manager.current_user}

基本信息:
  注册时间: {self.user_data.get('created_date', '未知')[:10] if isinstance(self.user_data.get('created_date'), str) else '未知'}
  当前等级: {self.level}
  当前经验: {self.experience}
  连续登录: {self.user_data.get('login_streak', 0)}天

财务状况:
  初始资金: $100,000
  当前现金: ${self.cash:,.2f}
  投资价值: ${total_value - self.cash:,.2f}
  总资产: ${total_value:,.2f}
  总盈亏: ${profit_loss:+,.2f} ({(profit_loss / 100000) * 100:+.2f}%)

交易统计:
  总交易次数: {self.trades_count}
  最佳单笔交易: ${self.best_trade:+,.2f}
  平均每笔交易: ${(profit_loss / max(self.trades_count, 1)):+,.2f}
  持仓种类: {len(self.portfolio)}

成就统计:
  已解锁成就: {len(self.achievements)}
  成就完成度: {(len(self.achievements) / len(self.market_data.achievement_definitions)) * 100:.1f}%
"""
        self.print_to_output(profile_text, '#AAFF00')

    # Admin methods
    def verify_admin(self):
        """验证管理员"""
        from login_window import AdminLogin
        admin_login = AdminLogin(self.gui)
        admin_login.start_admin_verification(self.enter_admin_mode)

    def enter_admin_mode(self):
        """进入管理员模式"""
        self.admin_mode = True
        self.print_to_output("已进入管理员模式. 输入 'admin_help' 查看可用命令.", '#FF5500')
        self.print_to_output("警告: 管理员命令可能会影响系统稳定性和用户数据.", '#FF0000')

    def exit_admin_mode(self):
        """退出管理员模式"""
        self.admin_mode = False
        self.print_to_output("已退出管理员模式.", '#00FF00')

    def show_admin_help(self):
        """显示管理员帮助"""
        result = self.admin_manager.show_admin_help()
        self.print_to_output(result, '#FF5500')

    def admin_add_stock(self, symbol, name, price, sector, volatility):
        """添加股票"""
        result = self.admin_manager.add_stock(symbol, name, price, sector, volatility)
        color = '#00FF00' if '成功' in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_remove_stock(self, symbol):
        """删除股票"""
        # 检查当前用户是否持有该股票
        current_user_has_stock = symbol in self.portfolio
        
        result = self.admin_manager.remove_stock(symbol)
        color = '#00FF00' if '成功' in result else '#FF0000'
        self.print_to_output(result, color)
        
        # 如果当前用户持有该股票，需要重新加载用户数据
        if current_user_has_stock and '成功' in result:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def admin_modify_stock_price(self, symbol, price):
        """修改股票价格"""
        result = self.admin_manager.modify_stock_price(symbol, price)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_view_all_users(self):
        """查看所有用户"""
        result = self.admin_manager.view_all_users()
        self.print_to_output(result, '#AAFFFF')

    # === 新增用户管理方法 ===
    def admin_get_user_info(self, username):
        """获取用户详细信息"""
        result = self.admin_manager.get_user_info(username)
        color = '#AAFFFF' if '错误' not in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_modify_user_level(self, username, level):
        """修改用户等级"""
        result = self.admin_manager.modify_user_level(username, level)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)
        
        # 如果修改的是当前登录用户，重新加载数据
        if username == self.user_manager.current_user and '已修改' in result:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def admin_modify_user_experience(self, username, experience):
        """修改用户经验值"""
        result = self.admin_manager.modify_user_experience(username, experience)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)
        
        if username == self.user_manager.current_user and '已修改' in result:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def admin_modify_user_credit(self, username, credit_rating):
        """修改用户信用等级"""
        result = self.admin_manager.modify_user_credit_rating(username, credit_rating)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)
        
        if username == self.user_manager.current_user and '已修改' in result:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def admin_unban_user(self, username):
        """解封用户"""
        result = self.admin_manager.unban_user(username)
        self.print_to_output(result, '#00FF00')

    # === 新增股票管理方法 ===
    def admin_get_stock_info(self, symbol):
        """获取股票详细信息"""
        result = self.admin_manager.get_stock_info(symbol)
        color = '#AAFFFF' if '错误' not in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_list_all_stocks(self):
        """列出所有股票"""
        self.show_stock_list()

    def admin_modify_stock_volatility(self, symbol, volatility):
        """修改股票波动率"""
        result = self.admin_manager.modify_stock_volatility(symbol, volatility)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)

    # === 新增银行管理方法 ===
    def admin_modify_loan_rate(self, rate):
        """修改贷款利率"""
        result = self.admin_manager.modify_loan_base_rate(rate)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_modify_deposit_rate(self, rate):
        """修改存款利率"""
        result = self.admin_manager.modify_deposit_base_rate(rate)
        color = '#00FF00' if '已修改' in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_force_loan(self, username, amount, days=30):
        """强制发放贷款"""
        result = self.admin_manager.force_loan(username, amount, days)
        color = '#00FF00' if '已向用户' in result else '#FF0000'
        self.print_to_output(result, color)
        
        if username == self.user_manager.current_user and '已向用户' in result:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def admin_forgive_loan(self, username, loan_id):
        """免除贷款"""
        result = self.admin_manager.forgive_loan(username, loan_id)
        color = '#00FF00' if '已免除' in result else '#FF0000'
        self.print_to_output(result, color)

    # === 新增系统管理方法 ===
    def admin_reset_market_prices(self):
        """重置市场价格"""
        result = self.admin_manager.reset_market_prices()
        self.print_to_output(result, '#00FF00')

    def admin_backup_system(self):
        """备份系统数据"""
        result = self.admin_manager.backup_system_data()
        color = '#00FF00' if '完成' in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_set_maintenance(self, mode):
        """设置维护模式"""
        result = self.admin_manager.set_maintenance_mode(mode)
        color = '#FFAA00' if '错误' not in result else '#FF0000'
        self.print_to_output(result, color)

    def admin_modify_cash(self, username, amount):
        """修改用户资金"""
        result = self.admin_manager.modify_cash(username, amount)
        color = '#00FF00' if '已' in result else '#FF0000'
        self.print_to_output(result, color)
        
        # 如果修改的是当前登录用户，需要重新加载用户数据
        if username == self.user_manager.current_user and '已' in result:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def reload_user_data(self):
        """重新加载当前用户数据"""
        self.user_data = self.user_manager.get_user_data()
        if self.user_data:
            self.cash = self.user_data.get('cash', 100000.0)
            self.portfolio = self.user_data.get('portfolio', {})
            self.transaction_history = self.user_data.get('transaction_history', [])
            self.achievements = self.user_data.get('achievements', [])
            self.level = self.user_data.get('level', 1)
            self.experience = self.user_data.get('experience', 0)
            self.total_profit = self.user_data.get('total_profit', 0)
            self.best_trade = self.user_data.get('best_trade', 0)
            self.trades_count = self.user_data.get('trades_count', 0)
            
            # 重新加载应用市场和家庭投资数据
            if hasattr(self, 'app_market'):
                self.app_market.load_user_apps()
            if hasattr(self, 'home_manager'):
                self.home_manager.load_user_assets()

    def admin_reset_user(self, username):
        """重置用户"""
        result = self.admin_manager.reset_user(username)
        self.print_to_output(result, '#00FF00')
        
        # 如果重置的是当前登录用户，需要重新加载用户数据
        if username == self.user_manager.current_user:
            self.reload_user_data()
            self.print_to_output("当前用户数据已同步更新", '#00FF00')

    def ban_user(self, username):
        """封禁用户"""
        result = self.admin_manager.ban_user(username)
        self.print_to_output(result, '#00FF00')
        if username == self.user_manager.current_user:
            self.print_to_output("您的账户已被封禁", '#FF0000')
            self.root.after(3000, self.logout)

    def create_market_event(self, event_text):
        """创建市场事件"""
        result = self.admin_manager.create_market_event(event_text)
        self.print_to_output(result, '#00FF00')
        # Also display in events panel
        if self.gui:
            event_time = datetime.now().strftime("%H:%M:%S")
            self.gui.events_text.config(state=tk.NORMAL)
            self.gui.events_text.insert(tk.END, f"[{event_time}] {event_text} [管理员创建]\n")
            self.gui.events_text.config(state=tk.DISABLED)
            self.gui.events_text.see(tk.END)

    # Placeholder methods
    def show_alerts_menu(self):
        self.print_to_output("价格提醒功能开发中...", '#FFAAFF')

    def start_trading_simulator(self):
        self.print_to_output("模拟交易功能开发中...", '#00AAFF')

    def show_settings(self):
        """显示和管理用户设置"""
        current_settings = self.user_data.get('game_settings', {
            'sound_enabled': True,
            'notifications_enabled': True,
            'auto_save': True,
            'auto_save_interval': 30,
            'default_quantity': 10,
            'confirm_trades': True,
            'color_theme': 'dark',
            'font_size': 'medium',
            'show_advanced_info': True,
            'price_alerts_enabled': True
        })
        
        settings_text = f"""
⚙️  用户设置

📱 界面设置:
  [1] 颜色主题: {current_settings.get('color_theme', 'dark')} (dark/light)
  [2] 字体大小: {current_settings.get('font_size', 'medium')} (small/medium/large)
  [3] 显示高级信息: {'开启' if current_settings.get('show_advanced_info', True) else '关闭'}

🔊 通知设置:
  [4] 声音通知: {'开启' if current_settings.get('sound_enabled', True) else '关闭'}
  [5] 弹窗通知: {'开启' if current_settings.get('notifications_enabled', True) else '关闭'}
  [6] 价格提醒: {'开启' if current_settings.get('price_alerts_enabled', True) else '关闭'}

💾 数据设置:
  [7] 自动保存: {'开启' if current_settings.get('auto_save', True) else '关闭'}
  [8] 保存间隔: {current_settings.get('auto_save_interval', 30)}秒

📈 交易设置:
  [9] 默认交易数量: {current_settings.get('default_quantity', 10)}股
  [10] 交易确认提示: {'开启' if current_settings.get('confirm_trades', True) else '关闭'}

使用方法:
  set <编号> <值>  - 修改设置项
  settings export  - 导出设置
  settings import  - 导入设置
  settings reset   - 重置为默认设置

示例:
  set 1 light      - 切换到亮色主题
  set 9 50         - 设置默认交易数量为50股
  set 4 false      - 关闭声音通知
"""
        self.print_to_output(settings_text, '#00FFAA')
    
    def modify_setting(self, setting_id, value):
        """修改用户设置"""
        if 'game_settings' not in self.user_data:
            self.user_data['game_settings'] = {}
        
        settings_map = {
            '1': ('color_theme', str),
            '2': ('font_size', str), 
            '3': ('show_advanced_info', lambda x: x.lower() in ['true', '1', 'on', '开启']),
            '4': ('sound_enabled', lambda x: x.lower() in ['true', '1', 'on', '开启']),
            '5': ('notifications_enabled', lambda x: x.lower() in ['true', '1', 'on', '开启']),
            '6': ('price_alerts_enabled', lambda x: x.lower() in ['true', '1', 'on', '开启']),
            '7': ('auto_save', lambda x: x.lower() in ['true', '1', 'on', '开启']),
            '8': ('auto_save_interval', int),
            '9': ('default_quantity', int),
            '10': ('confirm_trades', lambda x: x.lower() in ['true', '1', 'on', '开启'])
        }
        
        if setting_id not in settings_map:
            self.print_to_output(f"错误: 无效的设置编号 {setting_id}", '#FF0000')
            return
        
        setting_key, converter = settings_map[setting_id]
        
        try:
            # 特殊处理某些设置的值验证
            if setting_key == 'color_theme' and value not in ['dark', 'light']:
                self.print_to_output("错误: 颜色主题只能设置为 dark 或 light", '#FF0000')
                return
            elif setting_key == 'font_size' and value not in ['small', 'medium', 'large']:
                self.print_to_output("错误: 字体大小只能设置为 small、medium 或 large", '#FF0000')
                return
            elif setting_key == 'auto_save_interval' and (int(value) < 10 or int(value) > 300):
                self.print_to_output("错误: 自动保存间隔必须在10-300秒之间", '#FF0000')
                return
            elif setting_key == 'default_quantity' and (int(value) < 1 or int(value) > 10000):
                self.print_to_output("错误: 默认交易数量必须在1-10000股之间", '#FF0000')
                return
            
            # 转换并保存新值
            new_value = converter(value)
            old_value = self.user_data['game_settings'].get(setting_key, None)
            self.user_data['game_settings'][setting_key] = new_value
            
            # 保存数据
            self.save_game_data()
            
            self.print_to_output(f"✓ 设置已更新: {setting_key} = {new_value} (原值: {old_value})", '#00FF00')
            
        except ValueError:
            self.print_to_output(f"错误: 无效的设置值 '{value}'", '#FF0000')
        except Exception as e:
            self.print_to_output(f"错误: 设置更新失败 - {str(e)}", '#FF0000')
    
    def export_settings(self):
        """导出用户设置"""
        settings = self.user_data.get('game_settings', {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"settings_export_{self.user_manager.current_user}_{timestamp}.json"
        
        try:
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.print_to_output(f"✓ 设置已导出到: {filename}", '#00FF00')
        except Exception as e:
            self.print_to_output(f"错误: 导出设置失败 - {str(e)}", '#FF0000')
    
    def import_settings(self, filename=None):
        """导入用户设置"""
        if not filename:
            self.print_to_output("请指定要导入的设置文件名", '#FF0000')
            return
            
        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            if 'game_settings' not in self.user_data:
                self.user_data['game_settings'] = {}
            
            self.user_data['game_settings'].update(imported_settings)
            self.save_game_data()
            
            self.print_to_output(f"✓ 设置已从 {filename} 导入", '#00FF00')
        except FileNotFoundError:
            self.print_to_output(f"错误: 找不到文件 {filename}", '#FF0000')
        except Exception as e:
            self.print_to_output(f"错误: 导入设置失败 - {str(e)}", '#FF0000')
    
    def reset_settings(self):
        """重置设置为默认值"""
        default_settings = {
            'sound_enabled': True,
            'notifications_enabled': True,
            'auto_save': True,
            'auto_save_interval': 30,
            'default_quantity': 10,
            'confirm_trades': True,
            'color_theme': 'dark',
            'font_size': 'medium',
            'show_advanced_info': True,
            'price_alerts_enabled': True
        }
        
        self.user_data['game_settings'] = default_settings
        self.save_game_data()
        self.print_to_output("✓ 设置已重置为默认值", '#00FF00')

    def show_performance(self):
        self.print_to_output("绩效分析功能开发中...", '#00AAFF')

    def show_chart(self, symbol, time_range='5d'):
        """显示股票价格历史图表"""
        if symbol not in self.market_data.stocks:
            self.print_to_output(f"❌ 股票代码 {symbol} 不存在", '#FF0000')
            return

        stock_data = self.market_data.stocks[symbol]
        price_history = stock_data.get('price_history', [])
        
        if len(price_history) < 2:
            self.print_to_output(f"❌ {symbol} 的历史数据不足", '#FF0000')
            return

        chart_text = self._create_price_chart(symbol, stock_data, price_history, time_range)
        self.print_to_output(chart_text, '#00FFFF')

    def _create_price_chart(self, symbol, stock_data, price_history, time_range):
        """创建股票价格ASCII图表"""
        current_price = stock_data['price']
        change = stock_data['change']
        change_pct = (change / (current_price - change)) * 100 if (current_price - change) != 0 else 0
        
        # 根据时间范围选择数据点数量
        time_ranges = {
            '1d': 1, '5d': 5, '1w': 7, '2w': 14, '1m': 20
        }
        days = time_ranges.get(time_range, 5)
        chart_data = price_history[-days:] if len(price_history) >= days else price_history
        
        if len(chart_data) < 2:
            return f"❌ {symbol} 历史数据不足以生成 {time_range} 图表"

        chart_text = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                     📊 {symbol} - {stock_data['name']} 价格图表                                ║
║                                        {time_range.upper()} 时间范围 图表                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

💹 当前价格: ${current_price:.2f} ({change:+.2f} / {change_pct:+.2f}%)

📈 价格走势图 ({len(chart_data)}个数据点):
{self._create_ascii_line_chart(chart_data, symbol)}

📊 技术指标:
{self._calculate_chart_indicators(chart_data, stock_data)}

💡 图表说明:
  • 纵轴: 价格区间 (${min(chart_data):.2f} - ${max(chart_data):.2f})
  • 横轴: 时间序列 (最新 -> 最旧)
  • 符号: ● 实际价格点  ─ 趋势线  📈📉 方向指示
"""
        return chart_text

    def _create_ascii_line_chart(self, data, symbol, height=12, width=70):
        """创建ASCII线型图表"""
        if len(data) < 2:
            return "数据不足"
        
        min_price = min(data)
        max_price = max(data)
        price_range = max_price - min_price if max_price != min_price else 1
        
        # 创建图表网格
        chart_lines = []
        
        # 标题行
        chart_lines.append("─" * width)
        
        # 价格轴和图表内容
        for row in range(height):
            # 计算当前行的价格水平
            price_level = max_price - (row / (height - 1)) * price_range
            
            line = "│"
            price_label = f"{price_level:.2f}"
            
            # 为每个数据点画线
            for col in range(width - 8):  # 留出价格标签空间
                data_index = int(col * (len(data) - 1) / (width - 8))
                data_price = data[data_index]
                
                # 判断该位置是否应该有点
                tolerance = price_range / height * 0.5
                if abs(data_price - price_level) <= tolerance:
                    # 判断趋势
                    if data_index > 0:
                        prev_price = data[data_index - 1]
                        if data_price > prev_price:
                            line += "▲"
                        elif data_price < prev_price:
                            line += "▼"
                        else:
                            line += "●"
                    else:
                        line += "●"
                elif col > 0:
                    # 检查是否需要连接线
                    prev_index = int((col - 1) * (len(data) - 1) / (width - 8))
                    if prev_index != data_index and prev_index < len(data):
                        prev_price = data[prev_index]
                        curr_price = data[data_index]
                        
                        # 插值判断是否在连线上
                        if min(prev_price, curr_price) <= price_level <= max(prev_price, curr_price):
                            line += "─"
                        else:
                            line += " "
                    else:
                        line += " "
                else:
                    line += " "
            
            # 添加价格标签
            line += f" {price_label:>6}│"
            chart_lines.append(line)
        
        # 底部边框
        chart_lines.append("─" * width)
        
        # 添加时间轴标签
        time_axis = " " * 8 + "最新" + " " * (width - 20) + "最旧"
        chart_lines.append(time_axis)
        
        return "\n".join(chart_lines)

    def _calculate_chart_indicators(self, price_history, stock_data):
        """计算图表技术指标"""
        if len(price_history) < 2:
            return "数据不足以计算指标"
        
        current_price = price_history[-1]
        prev_price = price_history[-2] if len(price_history) >= 2 else current_price
        
        # 计算各种指标
        sma_5 = sum(price_history[-5:]) / min(5, len(price_history))
        sma_10 = sum(price_history[-10:]) / min(10, len(price_history))
        
        # 计算波动率
        if len(price_history) >= 3:
            returns = [(price_history[i] / price_history[i-1] - 1) for i in range(1, len(price_history))]
            volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * 100
        else:
            volatility = 0
        
        # 支撑位和阻力位
        support = min(price_history[-10:]) if len(price_history) >= 10 else min(price_history)
        resistance = max(price_history[-10:]) if len(price_history) >= 10 else max(price_history)
        
        # 趋势判断
        if len(price_history) >= 5:
            recent_trend = "上升" if price_history[-1] > price_history[-5] else "下降"
        else:
            recent_trend = "横盘"
        
        indicators = f"""
  🔍 技术分析:
    5日均线: ${sma_5:.2f} {'📈' if current_price > sma_5 else '📉'}
    10日均线: ${sma_10:.2f} {'📈' if current_price > sma_10 else '📉'}
    支撑位: ${support:.2f}
    阻力位: ${resistance:.2f}
    波动率: {volatility:.2f}%
    
  📊 趋势分析:
    短期趋势: {recent_trend}
    均线信号: {'多头排列' if sma_5 > sma_10 else '空头排列' if sma_5 < sma_10 else '均线粘合'}
    价格位置: {'阻力位附近' if abs(current_price - resistance) / resistance < 0.02 else '支撑位附近' if abs(current_price - support) / support < 0.02 else '中性区域'}"""
        
        return indicators

    def show_sector_chart(self, sector_name=None):
        """显示行业图表分析"""
        result = self.analysis_features.show_sector_chart(sector_name)
        self.print_to_output(result, '#FFFF00')

    def compare_stocks(self, symbol1, symbol2):
        """对比两支股票的表现"""
        if symbol1 not in self.market_data.stocks:
            self.print_to_output(f"❌ 股票代码 {symbol1} 不存在", '#FF0000')
            return
        
        if symbol2 not in self.market_data.stocks:
            self.print_to_output(f"❌ 股票代码 {symbol2} 不存在", '#FF0000')
            return

        stock1 = self.market_data.stocks[symbol1]
        stock2 = self.market_data.stocks[symbol2]
        
        comparison_text = self._create_stock_comparison(symbol1, stock1, symbol2, stock2)
        self.print_to_output(comparison_text, '#AAFFAA')

    def _create_stock_comparison(self, symbol1, stock1, symbol2, stock2):
        """创建股票对比分析"""
        comparison_text = f"""
══════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                          📊 股票对比分析                                                      
                          {symbol1} vs {symbol2}                                                               
══════════════════════════════════════════════════════════════════════════════════════════════════════════════

🏢 基本信息对比:
─────────────────────────────────────────────────────
 指标              {symbol1:<19}   {symbol2:<19} 
─────────────────────────────────────────────────────
 公司名称          {stock1['name'][:19]:<19}   {stock2['name'][:19]:<19} 
 当前价格          ${stock1['price']:<18.2f}   ${stock2['price']:<18.2f} 
 今日涨跌          {stock1['change']:+<18.2f}   {stock2['change']:+<18.2f} 
 涨跌幅            {((stock1['change']/(stock1['price']-stock1['change']))*100):+<17.2f}%   {((stock2['change']/(stock2['price']-stock2['change']))*100):+<17.2f}% 
 市值(亿)          {stock1['market_cap']/1e8:<18.1f}   {stock2['market_cap']/1e8:<18.1f} 
 市盈率            {stock1.get('pe_ratio', 'N/A'):<19}   {stock2.get('pe_ratio', 'N/A'):<19} 
 股息率            {stock1['dividend_yield']*100:<17.2f}%   {stock2['dividend_yield']*100:<17.2f}% 
 Beta值            {stock1['beta']:<18.2f}   {stock2['beta']:<18.2f} 
 波动率            {stock1['volatility']*100:<17.2f}%   {stock2['volatility']*100:<17.2f}% 
 成交量(万)        {stock1['volume']/10000:<18.0f}   {stock2['volume']/10000:<18.0f} 
─────────────────────────────────────────────────────

📊 性能对比图表:
{self._create_comparison_chart(symbol1, stock1, symbol2, stock2)}

💡 投资建议:
{self._generate_comparison_advice(symbol1, stock1, symbol2, stock2)}
"""
        return comparison_text

    def _create_comparison_chart(self, symbol1, stock1, symbol2, stock2, chart_width=50):
        """创建对比图表"""
        metrics = [
            ('涨跌幅', stock1['change']/(stock1['price']-stock1['change'])*100, stock2['change']/(stock2['price']-stock2['change'])*100, '%'),
            ('市盈率', stock1.get('pe_ratio', 0) or 0, stock2.get('pe_ratio', 0) or 0, '倍'),
            ('波动率', stock1['volatility']*100, stock2['volatility']*100, '%'),
            ('Beta值', stock1['beta'], stock2['beta'], ''),
            ('股息率', stock1['dividend_yield']*100, stock2['dividend_yield']*100, '%')
        ]
        
        chart_text = ""
        for metric_name, value1, value2, unit in metrics:
            max_val = max(abs(value1), abs(value2), 1)
            
            # 计算条形长度
            bar1_len = int(abs(value1) / max_val * chart_width * 0.4)
            bar2_len = int(abs(value2) / max_val * chart_width * 0.4)
            
            # 选择颜色和方向
            bar1 = ('🟩' if value1 >= 0 else '🟥') * bar1_len
            bar2 = ('🟩' if value2 >= 0 else '🟥') * bar2_len
            
            chart_text += f"{metric_name:<6} │ {symbol1}: {bar1:<20} {value1:+7.2f}{unit}\n"
            chart_text += f"{'':>6} │ {symbol2}: {bar2:<20} {value2:+7.2f}{unit}\n\n"
        
        return chart_text

    def _generate_comparison_advice(self, symbol1, stock1, symbol2, stock2):
        """生成对比投资建议"""
        # 计算综合评分
        score1 = 0
        score2 = 0
        
        # 价格表现
        change1 = stock1['change']/(stock1['price']-stock1['change'])*100
        change2 = stock2['change']/(stock2['price']-stock2['change'])*100
        if change1 > change2:
            score1 += 1
        else:
            score2 += 1
        
        # 市盈率(越低越好)
        pe1 = stock1.get('pe_ratio') or 999
        pe2 = stock2.get('pe_ratio') or 999
        if pe1 < pe2:
            score1 += 1
        else:
            score2 += 1
        
        # 股息率(越高越好)
        if stock1['dividend_yield'] > stock2['dividend_yield']:
            score1 += 1
        else:
            score2 += 1
        
        # 波动率(越低越好，稳健性)
        if stock1['volatility'] < stock2['volatility']:
            score1 += 1
        else:
            score2 += 1
        
        winner = symbol1 if score1 > score2 else symbol2 if score2 > score1 else "平手"
        
        advice = f"""
  🎯 综合评分: {symbol1}({score1}分) vs {symbol2}({score2}分)
  🏆 推荐选择: {winner}
  
  📈 {symbol1} 优势:
    {'• 价格表现更佳' if change1 > change2 else ''}
    {'• 估值更合理' if pe1 < pe2 else ''}
    {'• 分红收益更高' if stock1['dividend_yield'] > stock2['dividend_yield'] else ''}
    {'• 波动风险更小' if stock1['volatility'] < stock2['volatility'] else ''}
  
  📈 {symbol2} 优势:
    {'• 价格表现更佳' if change2 > change1 else ''}
    {'• 估值更合理' if pe2 < pe1 else ''}
    {'• 分红收益更高' if stock2['dividend_yield'] > stock1['dividend_yield'] else ''}
    {'• 波动风险更小' if stock2['volatility'] < stock1['volatility'] else ''}
  
  💡 投资策略建议:
    • 如果追求稳健: 选择波动率较低的股票
    • 如果追求成长: 关注价格动量和市场表现
    • 如果追求收益: 考虑股息率和分红政策
    • 风险控制: 注意Beta值，高Beta在牛市有优势，熊市风险大"""
        
        return advice

    # Banking system methods
    def show_banking_menu(self):
        """显示银行菜单"""
        result = self.bank_manager.show_bank_system_menu()
        self.print_to_output(result, '#00FFAA')

    def apply_bank_loan(self, amount, days=30):
        """申请银行贷款"""
        result = self.bank_manager.apply_loan(amount)
        color = '#00FF00' if '✅' in result else '#FF0000'
        self.print_to_output(result, color)

    def repay_bank_loan(self, loan_id):
        """偿还银行贷款"""
        result = self.bank_manager.repay_loan(loan_id)
        color = '#00FF00' if '✅' in result else '#FF0000'
        self.print_to_output(result, color)

    def make_bank_deposit(self, amount, term_type='demand'):
        """银行存款"""
        result = self.bank_manager.apply_deposit(amount, term_type)
        color = '#00FF00' if '✅' in result else '#FF0000'
        self.print_to_output(result, color)

    def withdraw_bank_deposit(self, deposit_id):
        """提取银行存款"""
        result = self.bank_manager.withdraw_deposit(deposit_id)
        color = '#00FF00' if '✅' in result else '#FF0000'
        self.print_to_output(result, color)

    def request_emergency_assistance(self):
        """申请紧急救助"""
        # 紧急救助功能暂时不可用
        result = "❌ 紧急救助功能正在维护中，请联系银行客服"
        color = '#FFAA00'
        self.print_to_output(result, color)

    def show_bank_contracts(self):
        """显示银行合约"""
        result = self.bank_manager.show_bank_tasks()
        self.print_to_output(result, '#AAFFFF')

    def generate_new_bank_contracts(self):
        """生成新银行合约"""
        # 新银行系统中合约是自动生成的
        result = "💡 银行任务和合约会自动更新，请查看银行任务列表"
        color = '#00FF00'
        self.print_to_output(result, color)

    def show_bank_status(self):
        """显示详细银行状态"""
        result = self.bank_manager.show_account_summary()
        self.print_to_output(result, '#AAFFFF')

    def show_bank_rates(self):
        """显示银行利率表"""
        result = self.bank_manager.show_bank_list()
        self.print_to_output(result, '#FFAAAA')

    # 指数系统相关方法
    def show_indices_overview(self):
        """显示指数概览"""
        if hasattr(self.market_data, 'index_manager') and self.market_data.index_manager:
            result = self.market_data.index_manager.show_indices_overview()
            self.print_to_output(result)
        else:
            self.print_to_output("❌ 指数系统未就绪", '#FF0000')
    
    def show_index_detail(self, index_code):
        """显示指数详情"""
        if hasattr(self.market_data, 'index_manager') and self.market_data.index_manager:
            result = self.market_data.index_manager.show_index_detail(index_code)
            self.print_to_output(result)
        else:
            self.print_to_output("❌ 指数系统未就绪", '#FF0000')
    
    def show_index_list(self):
        """显示指数列表"""
        if hasattr(self.market_data, 'index_manager') and self.market_data.index_manager:
            result = self.market_data.index_manager.get_index_list()
            self.print_to_output(result)
        else:
            self.print_to_output("❌ 指数系统未就绪", '#FF0000')
    
    def show_indices_by_category(self, category):
        """按类别显示指数"""
        if hasattr(self.market_data, 'index_manager') and self.market_data.index_manager:
            result = self.market_data.index_manager.show_indices_by_category(category)
            self.print_to_output(result)
        else:
            self.print_to_output("❌ 指数系统未就绪", '#FF0000')
    
    def compare_indices(self, index1, index2):
        """比较两个指数"""
        if hasattr(self.market_data, 'index_manager') and self.market_data.index_manager:
            result = self.market_data.index_manager.compare_indices(index1, index2)
            self.print_to_output(result)
        else:
            self.print_to_output("❌ 指数系统未就绪", '#FF0000')

    def add_advanced_commands(self, command):
        self.print_to_output(f"高级功能开发中: {command}", '#AAAAFF')

    # System methods
    def save_game_data(self):
        """保存游戏数据"""
        if not self.user_manager.current_user:
            return
            
        try:
            # 确保user_data存在
            if not self.user_data:
                self.user_data = {}
            
            # 保存核心游戏数据
            game_data = {
                'cash': self.cash,
                'portfolio': self.portfolio,
                'transaction_history': self.transaction_history,
                'achievements': self.achievements,
                'level': self.level,
                'experience': self.experience,
                'total_profit': self.total_profit,
                'best_trade': self.best_trade,
                'trades_count': self.trades_count,
                'login_streak': self.user_data.get('login_streak', 0),
                'last_login': self.user_data.get('last_login', datetime.now().isoformat()),
                'game_settings': self.user_data.get('game_settings', {}),
                
                # 保存时间相关统计数据
                'last_trade_date': self.user_data.get('last_trade_date'),
                'today_trades_count': self.user_data.get('today_trades_count', 0),
                'early_morning_trades': self.user_data.get('early_morning_trades', 0),
                'late_night_trades': self.user_data.get('late_night_trades', 0),
                
                # 保存交易相关统计
                'short_trades_count': self.user_data.get('short_trades_count', 0),
                'stop_loss_used': self.user_data.get('stop_loss_used', 0),
                'take_profit_used': self.user_data.get('take_profit_used', 0),
                'limit_orders_executed': self.user_data.get('limit_orders_executed', 0),
                'on_time_loan_repayments': self.user_data.get('on_time_loan_repayments', 0),
                'total_deposits': self.user_data.get('total_deposits', 0),
                
                # 保存银行数据
                'bank_data': self.user_data.get('bank_data', {}),
                
                # 保存应用市场数据
                'installed_apps': self.user_data.get('installed_apps', {}),
                
                # 保存家庭投资数据
                'home_assets': self.user_data.get('home_assets', {}),
                
                # 保存创建时间
                'created_date': self.user_data.get('created_date', datetime.now().isoformat())
            }
            
            # 调用用户管理器保存数据
            self.user_manager.save_user_data(game_data)
            
        except Exception as e:
            print(f"保存游戏数据时出错: {e}")
            # 尝试至少保存最基础的数据
            try:
                basic_data = {
                    'cash': self.cash,
                    'portfolio': self.portfolio,
                    'transaction_history': self.transaction_history[-50:],  # 只保存最近50条记录
                    'achievements': self.achievements,
                    'level': self.level,
                    'experience': self.experience,
                    'total_profit': self.total_profit,
                    'best_trade': self.best_trade,
                    'trades_count': self.trades_count
                }
                self.user_manager.save_user_data(basic_data)
                print("已保存基础游戏数据")
            except Exception as backup_error:
                print(f"保存基础数据也失败: {backup_error}")
                self.print_to_output("❌ 数据保存失败，请检查磁盘空间和权限", '#FF0000')

    def clear_screen(self):
        """清屏"""
        if self.gui:
            self.gui.clear_screen()
            self.display_welcome()

    def logout(self):
        """退出登录"""
        self.save_game_data()
        self.print_to_output(f"再见，{self.user_manager.current_user}！数据已保存。", '#FFFF00')
        self.root.after(2000, self.root.quit)

    def run(self):
        """运行应用"""
        # 定期自动保存
        def auto_save():
            self.save_game_data()
            self.root.after(30000, auto_save)  # 每30秒自动保存

        # 定期检查挂单
        def check_orders():
            if self.user_manager.current_user:  # 确保用户已登录
                self.check_pending_orders()
            self.root.after(5000, check_orders)  # 每5秒检查一次挂单

        auto_save()
        check_orders()
        self.root.mainloop()

    def show_jc_stock_analysis(self, symbol):
        """显示JC股票专业分析"""
        try:
            # 获取JC股票更新器的分析数据
            if hasattr(self, 'company_manager') and hasattr(self.company_manager, 'jc_stock_updater'):
                analysis_data = self.company_manager.jc_stock_updater.get_stock_analysis_data(symbol)
                
                if analysis_data:
                    # 生成专业分析报告
                    report = self._generate_jc_analysis_report(symbol, analysis_data)
                    self.print_to_output(report, '#00FFFF')
                else:
                    self.print_to_output(f"❌ 无法获取JC股票 {symbol} 的分析数据", '#FF0000')
            else:
                self.print_to_output("❌ JC股票分析系统未初始化", '#FF0000')
                
        except Exception as e:
            self.print_to_output(f"❌ 分析JC股票时出错: {str(e)}", '#FF0000')
    
    def show_jc_stock_chart(self, symbol, time_range='5d'):
        """显示JC股票图表"""
        try:
            # 获取JC股票更新器的分析数据
            if hasattr(self, 'company_manager') and hasattr(self.company_manager, 'jc_stock_updater'):
                analysis_data = self.company_manager.jc_stock_updater.get_stock_analysis_data(symbol)
                
                if analysis_data and 'price_history' in analysis_data:
                    # 生成JC股票图表
                    chart = self._create_jc_stock_chart(symbol, analysis_data, time_range)
                    self.print_to_output(chart, '#FFAAFF')
                else:
                    self.print_to_output(f"❌ 无法获取JC股票 {symbol} 的图表数据", '#FF0000')
            else:
                self.print_to_output("❌ JC股票图表系统未初始化", '#FF0000')
                
        except Exception as e:
            self.print_to_output(f"❌ 生成JC股票图表时出错: {str(e)}", '#FF0000')
    
    def _generate_jc_analysis_report(self, symbol, analysis_data):
        """生成JC股票分析报告"""
        try:
            company = analysis_data.get('company')
            fundamentals = analysis_data.get('fundamentals', {})
            technical = analysis_data.get('technical_indicators', {})
            sentiment = analysis_data.get('sentiment', {})
            price_history = analysis_data.get('price_history', [])
            
            current_price = price_history[-1] if price_history else 0
            
            # 基础信息
            report = f"""
🏢 JC股票深度分析 - {symbol}

📊 基本信息:
  公司名称: {company.name if company else 'N/A'}
  当前股价: J${current_price:.2f}
  行业分类: {company.industry.value if company else 'N/A'}
  上市时间: {company.ipo_date if company and company.ipo_date else 'N/A'}
  总股本: {company.shares_outstanding:,}股 (如果有的话)
  市值: J${company.market_cap:,.0f} (如果有的话)

💰 财务分析:"""
            
            if fundamentals:
                report += f"""
  营业收入: J${fundamentals.get('revenue', 0):,.0f}
  净利润: J${fundamentals.get('profit', 0):,.0f}
  总资产: J${fundamentals.get('assets', 0):,.0f}
  净资产: J${fundamentals.get('equity', 0):,.0f}
  市盈率: {fundamentals.get('pe_ratio', 'N/A')}倍
  市净率: {fundamentals.get('pb_ratio', 'N/A')}倍
  ROE: {fundamentals.get('roe', 0)*100:.1f}%
  负债率: {fundamentals.get('debt_ratio', 0)*100:.1f}%"""
            
            # 技术分析
            if technical:
                report += f"""

📈 技术指标:
  移动平均线:
    MA5: J${technical.get('ma5', 0):.2f}
    MA20: J${technical.get('ma20', 0):.2f}
    MA60: J${technical.get('ma60', 0):.2f}
  
  趋势指标:
    RSI: {technical.get('rsi', 0):.1f}
    MACD: {technical.get('macd', 0):.3f}
    布林带上轨: J${technical.get('bollinger_upper', 0):.2f}
    布林带下轨: J${technical.get('bollinger_lower', 0):.2f}
  
  成交量:
    平均成交量: {technical.get('avg_volume', 0):,.0f}
    成交量比率: {technical.get('volume_ratio', 1):.2f}"""
            
            # 市场情绪
            if sentiment:
                sentiment_score = sentiment.get('overall_score', 50)
                sentiment_text = self._get_sentiment_text(sentiment_score)
                
                report += f"""

😊 市场情绪:
  整体情绪: {sentiment_text} ({sentiment_score:.1f}/100)
  新闻影响: {sentiment.get('news_impact', 'neutral')}
  社交媒体: {sentiment.get('social_sentiment', 'neutral')}
  机构观点: {sentiment.get('institutional_view', 'neutral')}"""
            
            # 投资建议
            performance_score = company.performance_score if company else 50
            rating, grade = self._get_jc_investment_rating(performance_score, technical, fundamentals)
            
            report += f"""

🎯 投资建议:
  综合评分: {performance_score:.1f}/100
  投资等级: {rating} ({grade})
  风险等级: {'⭐' * (company.risk_level if company else 3)} ({company.risk_level if company else 3}/5)
  
📋 关键风险:
  • 个股集中风险较高
  • JC公司业绩波动性
  • 市场流动性风险
  • 行业竞争风险

💡 投资策略:
  • 建议分散投资，控制单只股票仓位
  • 关注公司基本面变化
  • 设置合理止损和止盈点
  • 定期跟踪公司经营状况
"""
            
            # 最新消息
            if company and company.news_events:
                recent_news = sorted(company.news_events, key=lambda x: x.publish_date, reverse=True)[:3]
                report += "\n📰 最新资讯:\n"
                for news in recent_news:
                    impact_icon = "📈" if news.impact_type == "positive" else "📉" if news.impact_type == "negative" else "📊"
                    report += f"  {impact_icon} {news.title}\n"
                    report += f"     {news.publish_date[:10]} | 影响程度: {news.impact_magnitude:.1%}\n"
            
            return report
            
        except Exception as e:
            return f"❌ 生成分析报告时出错: {str(e)}"
    
    def _create_jc_stock_chart(self, symbol, analysis_data, time_range):
        """创建JC股票图表"""
        try:
            price_history = analysis_data.get('price_history', [])
            technical = analysis_data.get('technical_indicators', {})
            
            if not price_history:
                return f"❌ {symbol} 没有足够的价格数据生成图表"
            
            # 根据时间范围截取数据
            range_map = {'1d': 1, '5d': 5, '1m': 30, '3m': 90, '1y': 365}
            days = range_map.get(time_range, 5)
            chart_data = price_history[-days:] if len(price_history) >= days else price_history
            
            if not chart_data:
                return f"❌ {symbol} 没有足够的数据生成{time_range}图表"
            
            # 生成ASCII价格图表
            chart = self._create_jc_ascii_chart(chart_data, symbol, time_range)
            
            # 添加技术指标信息
            current_price = chart_data[-1]
            prev_price = chart_data[-2] if len(chart_data) > 1 else current_price
            change = current_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price > 0 else 0
            
            change_color = "🔴" if change < 0 else "🟢" if change > 0 else "⚪"
            
            header = f"""
📊 JC股票图表 - {symbol} ({time_range})

💰 价格信息:
  当前价格: J${current_price:.2f}
  涨跌金额: {change:+.2f}
  涨跌幅度: {change_pct:+.2f}% {change_color}
  最高价: J${max(chart_data):.2f}
  最低价: J${min(chart_data):.2f}
"""
            
            if technical:
                header += f"""
📈 技术指标:
  RSI: {technical.get('rsi', 0):.1f} {'超买' if technical.get('rsi', 50) > 70 else '超卖' if technical.get('rsi', 50) < 30 else '正常'}
  MACD: {technical.get('macd', 0):.3f}
  MA20: J${technical.get('ma20', 0):.2f}
"""
            
            return header + chart
            
        except Exception as e:
            return f"❌ 生成图表时出错: {str(e)}"
    
    def _create_jc_ascii_chart(self, data, symbol, time_range, height=12, width=60):
        """创建JC股票ASCII图表"""
        if not data or len(data) < 2:
            return "❌ 数据不足，无法生成图表"
        
        # 计算价格范围
        min_price = min(data)
        max_price = max(data)
        price_range = max_price - min_price
        
        if price_range == 0:
            return f"📊 {symbol} 价格保持稳定在 J${data[0]:.2f}"
        
        # 创建图表网格
        chart_lines = []
        
        # 绘制价格线
        for row in range(height):
            line = []
            threshold = max_price - (row / (height - 1)) * price_range
            
            # 显示价格刻度
            price_label = f"{threshold:.2f}"
            line.append(f"{price_label:>6}")
            line.append("│")
            
            # 绘制数据点
            for i, price in enumerate(data[-width:]):
                if abs(price - threshold) <= price_range / height / 2:
                    if i == len(data[-width:]) - 1:
                        line.append("●")  # 最新价格点
                    else:
                        line.append("█")  # 历史价格点
                else:
                    line.append(" ")
            
            chart_lines.append("".join(line))
        
        # 添加底部时间轴
        time_axis = "       └" + "─" * min(width, len(data)) + ">"
        chart_lines.append(time_axis)
        
        # 添加图例
        legend = f"       {len(data)}个数据点 | 最新: J${data[-1]:.2f}"
        chart_lines.append(legend)
        
        return "\n" + "\n".join(chart_lines) + "\n"
    
    def _get_sentiment_text(self, score):
        """根据情绪分数获取文本描述"""
        if score >= 80:
            return "极度乐观"
        elif score >= 65:
            return "乐观"
        elif score >= 50:
            return "中性偏多"
        elif score >= 35:
            return "中性偏空"
        elif score >= 20:
            return "悲观"
        else:
            return "极度悲观"
    
    def _get_jc_investment_rating(self, performance_score, technical, fundamentals):
        """获取JC股票投资评级"""
        # 综合考虑公司表现、技术指标和基本面
        base_score = performance_score
        
        # 技术面调整
        if technical:
            rsi = technical.get('rsi', 50)
            if rsi > 80:  # 超买
                base_score -= 5
            elif rsi < 20:  # 超卖，可能是机会
                base_score += 3
        
        # 基本面调整
        if fundamentals:
            roe = fundamentals.get('roe', 0)
            if roe > 0.15:  # ROE > 15%
                base_score += 5
            elif roe < 0:  # 负ROE
                base_score -= 10
                
            debt_ratio = fundamentals.get('debt_ratio', 0)
            if debt_ratio > 0.7:  # 负债率过高
                base_score -= 5
        
        # 评级划分
        if base_score >= 85:
            return "强烈推荐", "A+"
        elif base_score >= 75:
            return "推荐买入", "A"
        elif base_score >= 65:
            return "谨慎乐观", "B+"
        elif base_score >= 55:
            return "中性持有", "B"
        elif base_score >= 45:
            return "观望等待", "B-"
        elif base_score >= 35:
            return "谨慎看空", "C"
        else:
            return "建议回避", "D"


if __name__ == "__main__":
    app = StockTradingApp()
    app.run() 