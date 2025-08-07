from commands.base import FinanceCommand
from services.stock_service import StockService
from services.currency_service import CurrencyService
from typing import Dict, Any

class PortfolioCommand(FinanceCommand):
    """投资组合命令 - 查看和管理投资组合"""
    
    def __init__(self, stock_service: StockService, currency_service: CurrencyService):
        super().__init__()
        self.stock_service = stock_service
        self.currency_service = currency_service
    
    def execute(self, args: list, context: Dict[str, Any]) -> str:
        user_id = context.get('user_id')
        if not user_id:
            return "❌ 请先登录"
        
        if not args:
            return self._show_portfolio_summary(user_id)
        
        subcommand = args[0].lower()
        
        if subcommand == 'summary':
            return self._show_portfolio_summary(user_id)
        elif subcommand == 'performance':
            return self._show_performance_analysis(user_id)
        elif subcommand == 'allocation':
            return self._show_sector_allocation(user_id)
        elif subcommand == 'history':
            days = int(args[1]) if len(args) > 1 else 30
            return self._show_portfolio_history(user_id, days)
        else:
            return "未知的子命令。可用命令: summary, performance, allocation, history"
    
    def _show_portfolio_summary(self, user_id: int) -> str:
        """显示投资组合概况"""
        portfolio = self.stock_service.get_user_portfolio(user_id)
        
        if not portfolio:
            return self._show_empty_portfolio()
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    💼 投资组合概况                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        total_cost = 0
        total_value = 0
        total_dividend = 0
        
        # 计算总体数据
        for holding in portfolio:
            total_cost += holding['cost_value']
            total_value += holding['current_value']
            total_dividend += holding.get('dividend_received', 0)
        
        total_profit_loss = total_value - total_cost
        total_profit_loss_pct = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
        
        # 显示总体统计
        output.append(f"│ 💰 总投资成本: {self.currency_service.format_amount(total_cost, 'JCC'):>20}        │")
        output.append(f"│ 💎 当前市值:   {self.currency_service.format_amount(total_value, 'JCC'):>20}        │")
        
        pl_color = "📈" if total_profit_loss >= 0 else "📉"
        pl_str = self.currency_service.format_amount(abs(total_profit_loss), 'JCC')
        pl_sign = "+" if total_profit_loss >= 0 else "-"
        output.append(f"│ {pl_color} 浮动盈亏:   {pl_sign}{pl_str:>20} ({total_profit_loss_pct:+.1f}%)    │")
        
        if total_dividend > 0:
            output.append(f"│ 💵 累计分红:   {self.currency_service.format_amount(total_dividend, 'JCC'):>20}        │")
        
        output.append(f"│ 📊 持仓数量:   {len(portfolio):>3} 只股票                              │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📈 持仓明细                                                 │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 代码   │ 数量  │ 成本价  │ 现价    │ 市值      │ 盈亏率   │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 按市值排序显示持仓
        sorted_portfolio = sorted(portfolio, key=lambda x: x['current_value'], reverse=True)
        
        for holding in sorted_portfolio:
            ticker = holding['ticker']
            quantity = holding['quantity']
            avg_cost = holding['average_cost']
            current_price = holding['current_price']
            current_value = holding['current_value']
            profit_loss_pct = holding['profit_loss_pct']
            
            pl_color = "📈" if profit_loss_pct >= 0 else "📉"
            value_str = f"{current_value:,.0f}"
            
            output.append(f"│ {ticker:<6} │ {quantity:>4} │ {avg_cost:>6.2f} │ {current_price:>6.2f} │ {value_str:>8} │ {pl_color}{profit_loss_pct:>+5.1f}% │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 更多功能                                                 │")
        output.append("│ • portfolio performance - 查看收益分析                      │")
        output.append("│ • portfolio allocation  - 查看行业配置                      │")
        output.append("│ • portfolio history     - 查看历史表现                      │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_empty_portfolio(self) -> str:
        """显示空投资组合"""
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    💼 投资组合                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│                                                             │")
        output.append("│                    📊 投资组合为空                          │")
        output.append("│                                                             │")
        output.append("│                  🚀 开始您的投资之旅！                      │")
        output.append("│                                                             │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 投资建议                                                 │")
        output.append("│ • stock list           - 查看可投资股票                     │")
        output.append("│ • stock view <代码>    - 研究股票基本面                     │")
        output.append("│ • stock buy <代码> <量> - 开始投资                          │")
        output.append("│ • news                 - 关注市场动态                       │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 🎯 投资小贴士                                               │")
        output.append("│ • 分散投资，降低风险                                        │")
        output.append("│ • 长期持有，复利增长                                        │")
        output.append("│ • 关注新闻，把握时机                                        │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_performance_analysis(self, user_id: int) -> str:
        """显示收益分析"""
        portfolio = self.stock_service.get_user_portfolio(user_id)
        
        if not portfolio:
            return "📊 投资组合为空，无法进行收益分析"
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📊 收益分析报告                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 计算各种收益指标
        total_cost = sum(h['cost_value'] for h in portfolio)
        total_value = sum(h['current_value'] for h in portfolio)
        total_profit_loss = total_value - total_cost
        total_profit_loss_pct = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
        
        # 最佳和最差表现
        best_performer = max(portfolio, key=lambda x: x['profit_loss_pct'])
        worst_performer = min(portfolio, key=lambda x: x['profit_loss_pct'])
        
        # 盈利和亏损股票数量
        profitable_stocks = [h for h in portfolio if h['profit_loss_pct'] > 0]
        losing_stocks = [h for h in portfolio if h['profit_loss_pct'] < 0]
        
        output.append(f"│ 📈 总收益率:     {total_profit_loss_pct:>+8.2f}%                        │")
        output.append(f"│ 💰 绝对收益:     {self.currency_service.format_amount(abs(total_profit_loss), 'JCC'):>15}              │")
        output.append(f"│ 🎯 盈利股票:     {len(profitable_stocks):>3} / {len(portfolio)} 只                      │")
        output.append(f"│ 📉 亏损股票:     {len(losing_stocks):>3} / {len(portfolio)} 只                      │")
        
        if profitable_stocks:
            win_rate = len(profitable_stocks) / len(portfolio) * 100
            output.append(f"│ 🏆 胜率:         {win_rate:>6.1f}%                              │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 🏆 最佳表现                                                 │")
        output.append(f"│ {best_performer['ticker']:<6} {best_performer['profit_loss_pct']:>+7.2f}% │ 市值: {best_performer['current_value']:>8,.0f} JCC        │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📉 最差表现                                                 │")
        output.append(f"│ {worst_performer['ticker']:<6} {worst_performer['profit_loss_pct']:>+7.2f}% │ 市值: {worst_performer['current_value']:>8,.0f} JCC        │")
        
        # 显示收益分布
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📊 收益分布                                                 │")
        
        profit_ranges = [
            (float('inf'), 20, "🚀 超级收益 (>20%)"),
            (20, 10, "📈 优秀收益 (10-20%)"),
            (10, 5, "✅ 良好收益 (5-10%)"),
            (5, 0, "📊 小幅收益 (0-5%)"),
            (0, -5, "📉 小幅亏损 (0 to -5%)"),
            (-5, -10, "⚠️ 中等亏损 (-5 to -10%)"),
            (-10, float('-inf'), "💥 重大亏损 (<-10%)"),
        ]
        
        for upper, lower, label in profit_ranges:
            if upper == float('inf'):
                count = len([h for h in portfolio if h['profit_loss_pct'] > lower])
            elif lower == float('-inf'):
                count = len([h for h in portfolio if h['profit_loss_pct'] < upper])
            else:
                count = len([h for h in portfolio if lower < h['profit_loss_pct'] <= upper])
            
            if count > 0:
                output.append(f"│ {label:<25} {count:>2} 只                    │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 投资建议                                                 │")
        
        if total_profit_loss_pct > 10:
            output.append("│ 🎉 投资表现优秀！考虑适当获利了结                        │")
        elif total_profit_loss_pct > 0:
            output.append("│ 👍 投资有盈利，继续保持投资策略                          │")
        elif total_profit_loss_pct > -5:
            output.append("│ ⚖️ 投资基本持平，关注市场动态调整策略                    │")
        else:
            output.append("│ 🔄 投资有亏损，考虑分析原因并调整投资组合                │")
        
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_sector_allocation(self, user_id: int) -> str:
        """显示行业配置"""
        portfolio = self.stock_service.get_user_portfolio(user_id)
        
        if not portfolio:
            return "📊 投资组合为空，无法进行行业分析"
        
        # 按行业分组统计
        sector_stats = {}
        total_value = sum(h['current_value'] for h in portfolio)
        
        for holding in portfolio:
            # 获取股票信息以确定行业
            stock = self.stock_service.get_stock_by_ticker(holding['ticker'])
            if stock:
                sector = stock.sector
                if sector not in sector_stats:
                    sector_stats[sector] = {
                        'value': 0,
                        'cost': 0,
                        'count': 0,
                        'stocks': []
                    }
                
                sector_stats[sector]['value'] += holding['current_value']
                sector_stats[sector]['cost'] += holding['cost_value']
                sector_stats[sector]['count'] += 1
                sector_stats[sector]['stocks'].append(holding)
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    🏭 行业配置分析                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 行业     │ 股票数 │ 市值占比 │ 市值(JCC) │ 行业收益率 │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 按市值排序显示行业
        sorted_sectors = sorted(sector_stats.items(), key=lambda x: x[1]['value'], reverse=True)
        
        for sector, stats in sorted_sectors:
            allocation_pct = (stats['value'] / total_value) * 100
            sector_return = ((stats['value'] - stats['cost']) / stats['cost']) * 100 if stats['cost'] > 0 else 0
            
            return_color = "📈" if sector_return >= 0 else "📉"
            
            output.append(f"│ {sector:<8} │ {stats['count']:>6} │ {allocation_pct:>7.1f}% │ {stats['value']:>8,.0f} │ {return_color}{sector_return:>+6.1f}% │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📊 配置建议                                                 │")
        
        # 分析配置集中度
        max_allocation = max(stats['value'] / total_value for stats in sector_stats.values()) * 100
        
        if max_allocation > 50:
            output.append("│ ⚠️ 行业配置过于集中，建议分散投资降低风险                │")
        elif max_allocation > 30:
            output.append("│ 💡 行业配置较为集中，可考虑适当分散                      │")
        else:
            output.append("│ ✅ 行业配置较为均衡，风险分散良好                        │")
        
        # 显示各行业详细持仓
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📈 行业持仓明细                                             │")
        
        for sector, stats in sorted_sectors:
            output.append(f"├─ {sector} ─────────────────────────────────────────────────┤")
            
            for stock in stats['stocks']:
                ticker = stock['ticker']
                value = stock['current_value']
                return_pct = stock['profit_loss_pct']
                return_color = "📈" if return_pct >= 0 else "📉"
                
                output.append(f"│   {ticker:<6} 市值: {value:>8,.0f} JCC  收益: {return_color}{return_pct:>+6.1f}%        │")
        
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_portfolio_history(self, user_id: int, days: int) -> str:
        """显示投资组合历史表现"""
        # 这里应该从数据库获取历史数据，暂时返回模拟数据
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│                📈 投资组合 {days} 天历史表现                  │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📊 功能开发中...                                            │")
        output.append("│                                                             │")
        output.append("│ 即将支持：                                                  │")
        output.append("│ • 每日净值变化                                              │")
        output.append("│ • 累计收益曲线                                              │")
        output.append("│ • 最大回撤分析                                              │")
        output.append("│ • 夏普比率计算                                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 当前可用功能                                             │")
        output.append("│ • portfolio          - 查看当前持仓                         │")
        output.append("│ • portfolio performance - 收益分析                          │")
        output.append("│ • portfolio allocation  - 行业配置                          │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def get_help(self) -> str:
        return """
投资组合命令 - 查看和分析投资组合

用法:
  portfolio                    - 显示投资组合概况
  portfolio summary            - 显示投资组合概况
  portfolio performance        - 显示收益分析
  portfolio allocation         - 显示行业配置分析
  portfolio history [天数]     - 显示历史表现 (开发中)

示例:
  portfolio
  portfolio performance
  portfolio allocation
  portfolio history 30

说明:
  投资组合命令提供全面的投资分析功能，帮助您:
  • 了解投资组合整体表现
  • 分析个股和行业收益
  • 优化资产配置策略
  • 控制投资风险
"""