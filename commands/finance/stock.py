from commands.base import Command
from services.stock_service import StockService
from services.currency_service import CurrencyService
from typing import Dict, Any

class StockCommand(Command):
    """股票命令 - 股票市场操作"""
    
    def __init__(self, stock_service: StockService, currency_service: CurrencyService):
        super().__init__()
        self.stock_service = stock_service
        self.currency_service = currency_service
    
    def execute(self, args: list, context: Dict[str, Any]) -> str:
        if not args:
            return self._show_market_summary()
        
        subcommand = args[0].lower()
        
        if subcommand == 'list':
            return self._list_stocks()
        elif subcommand == 'view':
            if len(args) < 2:
                return "用法: stock view <股票代码>"
            ticker = args[1].upper()
            return self._view_stock(ticker)
        elif subcommand == 'buy':
            if len(args) < 3:
                return "用法: stock buy <股票代码> <数量>"
            ticker = args[1].upper()
            try:
                quantity = int(args[2])
                return self._buy_stock(ticker, quantity, context)
            except ValueError:
                return "❌ 数量必须是整数"
        elif subcommand == 'sell':
            if len(args) < 3:
                return "用法: stock sell <股票代码> <数量>"
            ticker = args[1].upper()
            try:
                quantity = int(args[2])
                return self._sell_stock(ticker, quantity, context)
            except ValueError:
                return "❌ 数量必须是整数"
        elif subcommand == 'portfolio':
            return self._show_portfolio(context)
        elif subcommand == 'history':
            if len(args) < 2:
                return "用法: stock history <股票代码> [天数]"
            ticker = args[1].upper()
            days = int(args[2]) if len(args) > 2 else 7
            return self._show_price_history(ticker, days)
        else:
            return "未知的子命令。可用命令: list, view, buy, sell, portfolio, history"
    
    def _show_market_summary(self) -> str:
        """显示市场概况"""
        summary = self.stock_service.get_market_summary()
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📈 JCMarket 概况                         │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│ 🏢 上市公司数量: {summary['total_stocks']:>3}                            │")
        
        if 'total_market_cap' in summary:
            market_cap_str = self.currency_service.format_amount(summary['total_market_cap'], 'JCC')
            output.append(f"│ 💰 总市值: {market_cap_str:>20}                        │")
        
        if 'sectors' in summary:
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append("│ 🏭 行业分布                                                 │")
            output.append("├─────────────────────────────────────────────────────────────┤")
            
            for sector, data in summary['sectors'].items():
                count = data['count']
                market_cap = self.currency_service.format_amount(data['market_cap'], 'JCC')
                output.append(f"│ {sector:<8} {count:>2} 家公司  市值: {market_cap:>15}        │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用提示                                                 │")
        output.append("│ • stock list           - 查看所有股票                       │")
        output.append("│ • stock view <代码>    - 查看股票详情                       │")
        output.append("│ • stock buy <代码> <量> - 买入股票                          │")
        output.append("│ • stock portfolio      - 查看投资组合                       │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _list_stocks(self) -> str:
        """显示股票列表"""
        stocks = self.stock_service.get_all_stocks()
        
        if not stocks:
            return "❌ 暂无股票数据"
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📊 股票列表                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 代码     │ 公司名称        │ 行业   │ 当前价格    │ 涨跌幅  │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for stock in stocks:
            # 计算涨跌幅 (简化计算，实际应该基于历史价格)
            price_change = ((float(stock.current_price) - float(stock.ipo_price)) / float(stock.ipo_price)) * 100
            change_str = f"{price_change:+.1f}%"
            change_color = "📈" if price_change >= 0 else "📉"
            
            price_str = f"{float(stock.current_price):.2f}"
            
            output.append(f"│ {stock.ticker:<8} │ {stock.name:<15} │ {stock.sector:<6} │ {price_str:>8} JCC │ {change_color}{change_str:>6} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用 'stock view <代码>' 查看详细信息                    │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _view_stock(self, ticker: str) -> str:
        """查看股票详情"""
        stock = self.stock_service.get_stock_by_ticker(ticker)
        if not stock:
            return f"❌ 股票代码 '{ticker}' 不存在"
        
        # 计算涨跌幅
        price_change = ((float(stock.current_price) - float(stock.ipo_price)) / float(stock.ipo_price)) * 100
        change_str = f"{price_change:+.1f}%"
        change_color = "📈" if price_change >= 0 else "📉"
        
        market_cap_str = self.currency_service.format_amount(float(stock.market_cap), 'JCC')
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│ 📊 {stock.name} ({stock.ticker})                            │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│ 💰 当前价格: {float(stock.current_price):>8.2f} JCC                      │")
        output.append(f"│ 📈 IPO价格:  {float(stock.ipo_price):>8.2f} JCC                      │")
        output.append(f"│ 📊 涨跌幅:   {change_color} {change_str:>8}                           │")
        output.append(f"│ 🏭 行业:     {stock.sector:<20}                      │")
        output.append(f"│ 💎 市值:     {market_cap_str:>20}                │")
        output.append(f"│ ⚡ 波动率:   {float(stock.volatility)*100:>6.1f}%                        │")
        
        if stock.description:
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append("│ 📝 公司简介                                                 │")
            
            # 分行显示描述
            description_lines = [stock.description[i:i+55] for i in range(0, len(stock.description), 55)]
            for line in description_lines:
                output.append(f"│ {line:<59} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 交易提示                                                 │")
        output.append(f"│ • stock buy {ticker} <数量>   - 买入股票                    │")
        output.append(f"│ • stock sell {ticker} <数量>  - 卖出股票                    │")
        output.append(f"│ • stock history {ticker}      - 查看价格历史                 │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _buy_stock(self, ticker: str, quantity: int, context: Dict[str, Any]) -> str:
        """买入股票"""
        user_id = context.get('user_id')
        if not user_id:
            return "❌ 请先登录"
        
        result = self.stock_service.buy_stock(user_id, ticker, quantity)
        
        if result['success']:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['message']}"
    
    def _sell_stock(self, ticker: str, quantity: int, context: Dict[str, Any]) -> str:
        """卖出股票"""
        user_id = context.get('user_id')
        if not user_id:
            return "❌ 请先登录"
        
        result = self.stock_service.sell_stock(user_id, ticker, quantity)
        
        if result['success']:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['message']}"
    
    def _show_portfolio(self, context: Dict[str, Any]) -> str:
        """显示投资组合"""
        user_id = context.get('user_id')
        if not user_id:
            return "❌ 请先登录"
        
        portfolio = self.stock_service.get_user_portfolio(user_id)
        
        if not portfolio:
            return "📊 您的投资组合为空\n💡 使用 'stock buy <代码> <数量>' 开始投资"
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    💼 我的投资组合                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 代码   │ 数量  │ 成本价  │ 现价    │ 盈亏      │ 盈亏率   │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        total_cost = 0
        total_value = 0
        
        for holding in portfolio:
            ticker = holding['ticker']
            quantity = holding['quantity']
            avg_cost = holding['average_cost']
            current_price = holding['current_price']
            profit_loss = holding['profit_loss']
            profit_loss_pct = holding['profit_loss_pct']
            
            total_cost += holding['cost_value']
            total_value += holding['current_value']
            
            pl_color = "📈" if profit_loss >= 0 else "📉"
            pl_str = f"{profit_loss:+.2f}"
            pl_pct_str = f"{profit_loss_pct:+.1f}%"
            
            output.append(f"│ {ticker:<6} │ {quantity:>4} │ {avg_cost:>6.2f} │ {current_price:>6.2f} │ {pl_color}{pl_str:>7} │ {pl_pct_str:>7} │")
        
        total_profit_loss = total_value - total_cost
        total_profit_loss_pct = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│ 💰 总成本: {total_cost:>10.2f} JCC                              │")
        output.append(f"│ 💎 总市值: {total_value:>10.2f} JCC                              │")
        
        pl_color = "📈" if total_profit_loss >= 0 else "📉"
        output.append(f"│ {pl_color} 总盈亏: {total_profit_loss:>+10.2f} JCC ({total_profit_loss_pct:+.1f}%)           │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用 'stock sell <代码> <数量>' 卖出股票                  │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_price_history(self, ticker: str, days: int) -> str:
        """显示价格历史"""
        stock = self.stock_service.get_stock_by_ticker(ticker)
        if not stock:
            return f"❌ 股票代码 '{ticker}' 不存在"
        
        price_history = self.stock_service.get_stock_price_history(ticker, days)
        
        if not price_history:
            return f"📊 {ticker} 暂无价格历史数据"
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│ 📈 {stock.name} ({ticker}) - {days}天价格历史                 │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 日期时间            │ 价格      │ 成交量     │ 变化      │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        prev_price = None
        for i, price_record in enumerate(price_history[:10]):  # 只显示最近10条记录
            timestamp = price_record.timestamp.strftime("%m-%d %H:%M")
            price = float(price_record.price)
            volume = price_record.volume
            
            if prev_price is not None:
                change = price - prev_price
                change_pct = (change / prev_price) * 100
                change_str = f"{change:+.2f} ({change_pct:+.1f}%)"
                change_color = "📈" if change >= 0 else "📉"
            else:
                change_str = "--"
                change_color = "📊"
            
            output.append(f"│ {timestamp:<19} │ {price:>8.2f} │ {volume:>9,} │ {change_color}{change_str:>8} │")
            prev_price = price
        
        if len(price_history) > 10:
            output.append(f"│ ... 还有 {len(price_history) - 10} 条历史记录                          │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│ 💡 使用 'stock view {ticker}' 查看详细信息                   │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def get_help(self) -> str:
        return """
股票命令 - JCMarket股票交易

用法:
  stock                      - 显示市场概况
  stock list                 - 显示所有股票
  stock view <代码>          - 查看股票详情
  stock buy <代码> <数量>    - 买入股票
  stock sell <代码> <数量>   - 卖出股票
  stock portfolio            - 查看投资组合
  stock history <代码> [天数] - 查看价格历史

示例:
  stock
  stock list
  stock view JCTECH
  stock buy JCTECH 100
  stock sell JCTECH 50
  stock portfolio
  stock history JCTECH 7
"""