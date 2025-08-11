from commands.base import StockCommand, CommandResult
from services.stock_service import StockService
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from datetime import datetime
import asyncio

class JCMarketCommand(StockCommand):
    """JC股票市场命令 - 提供股票交易和市场信息"""
    
    name = "jcmarket"
    aliases = ["jcm", "market"]
    description = "JC股票市场 - 查看股票信息、交易股票"
    usage = "jcmarket [子命令] [参数]"
    
    def __init__(self, stock_service=None):
        super().__init__()
        self.stock_service = stock_service
        self.console = Console()
    
    def _render_rich_object(self, rich_obj):
        """Helper method to properly render Rich objects to string"""
        from io import StringIO
        string_io = StringIO()
        temp_console = Console(file=string_io, width=120)
        temp_console.print(rich_obj)
        return string_io.getvalue()
    
    async def execute(self, args: List[str], context) -> CommandResult:
        """执行股票市场命令"""
        if not args:
            return await self._show_market_overview(context)
        
        subcommand = args[0].lower()
        
        if subcommand in ['help', 'h']:
            return await self._show_help()
        elif subcommand in ['list', 'ls']:
            return await self._list_stocks(args[1:], context)
        elif subcommand in ['info', 'detail']:
            return await self._show_stock_info(args[1:], context)
        elif subcommand in ['buy', 'purchase']:
            return await self._buy_stock(args[1:], context)
        elif subcommand in ['sell']:
            return await self._sell_stock(args[1:], context)
        elif subcommand in ['portfolio', 'holdings']:
            return await self._show_portfolio(context)
        elif subcommand in ['watch', 'monitor']:
            return await self._watch_market(args[1:], context)
        else:
            return CommandResult(
                success=False,
                message=f"未知的子命令: {subcommand}。使用 'jcmarket help' 查看帮助。"
            )
    
    async def _show_market_overview(self, context) -> CommandResult:
        """显示市场概览"""
        try:
            # 获取市场数据
            stocks = await self.stock_service.get_all_stocks()
            market_stats = await self.stock_service.get_market_statistics()
            
            # 创建市场概览面板
            overview_content = []
            
            # 市场统计
            stats_table = Table(show_header=False, box=None, padding=(0, 1))
            stats_table.add_column("指标", style="cyan")
            stats_table.add_column("数值", style="green")
            
            stats_table.add_row("📈 总市值", f"{market_stats.get('total_market_cap', 0):,.0f} JCY")
            stats_table.add_row("📊 上市公司", f"{len(stocks)} 家")
            stats_table.add_row("📈 上涨股票", f"{market_stats.get('rising_stocks', 0)} 只")
            stats_table.add_row("📉 下跌股票", f"{market_stats.get('falling_stocks', 0)} 只")
            from core.game_time import GameTime
            current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
            stats_table.add_row("⏰ 更新时间", current_time.strftime("%H:%M:%S"))
            
            overview_content.append(Panel(
                stats_table,
                title="🏛️ JC股票市场概览",
                border_style="blue"
            ))
            
            # 热门股票
            if stocks:
                hot_table = Table(show_header=True, box=None)
                hot_table.add_column("代码", style="cyan")
                hot_table.add_column("名称", style="white")
                hot_table.add_column("价格", style="green")
                hot_table.add_column("涨跌", style="red")
                hot_table.add_column("涨跌幅", style="red")
                
                # 显示前5只股票
                for stock in stocks[:5]:
                    current_price = stock.current_price or 0
                    previous_close = stock.previous_close or current_price
                    change = current_price - previous_close
                    change_pct = (change / previous_close * 100) if previous_close > 0 else 0
                    
                    change_color = "green" if change >= 0 else "red"
                    change_symbol = "+" if change >= 0 else ""
                    
                    hot_table.add_row(
                        stock.symbol,
                        stock.name,
                        f"{current_price:.2f}",
                        f"[{change_color}]{change_symbol}{change:.2f}[/{change_color}]",
                        f"[{change_color}]{change_symbol}{change_pct:.2f}%[/{change_color}]"
                    )
                
                overview_content.append(Panel(
                    hot_table,
                    title="🔥 热门股票",
                    border_style="yellow"
                ))
            
            # 快捷操作提示
            help_text = Text()
            help_text.append("💡 快捷操作:\n", style="bold cyan")
            help_text.append("  jcmarket list        - 查看所有股票\n", style="white")
            help_text.append("  jcmarket info <代码>  - 查看股票详情\n", style="white")
            help_text.append("  jcmarket buy <代码>   - 购买股票\n", style="white")
            help_text.append("  jcmarket portfolio   - 查看持仓\n", style="white")
            help_text.append("  jcmarket help        - 查看帮助", style="white")
            
            overview_content.append(Panel(
                help_text,
                title="📋 操作指南",
                border_style="green"
            ))
            
            # 组合显示 - 使用helper方法渲染Rich对象
            final_content = "\n\n".join([self._render_rich_object(panel) for panel in overview_content])
            
            return CommandResult(
                success=True,
                message=final_content
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"获取市场数据失败: {str(e)}"
            )
    
    async def _list_stocks(self, args: List[str], context) -> CommandResult:
        """列出所有股票"""
        try:
            stocks = await self.stock_service.get_all_stocks()
            
            if not stocks:
                return CommandResult(
                    success=True,
                    message="📊 当前市场暂无股票上市"
                )
            
            # 创建股票列表表格
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("代码", style="cyan", width=8)
            table.add_column("名称", style="white", width=15)
            table.add_column("当前价格", style="green", width=10)
            table.add_column("涨跌", style="red", width=8)
            table.add_column("涨跌幅", style="red", width=8)
            table.add_column("成交量", style="yellow", width=10)
            table.add_column("市值", style="blue", width=12)
            
            for stock in stocks:
                current_price = stock.current_price or 0
                previous_close = stock.previous_close or current_price
                total_shares = stock.total_shares or 0
                change = current_price - previous_close
                change_pct = (change / previous_close * 100) if previous_close > 0 else 0
                market_cap = current_price * total_shares
                
                change_color = "green" if change >= 0 else "red"
                change_symbol = "+" if change >= 0 else ""
                
                table.add_row(
                    stock.symbol,
                    stock.name,
                    f"{current_price:.2f}",
                    f"[{change_color}]{change_symbol}{change:.2f}[/{change_color}]",
                    f"[{change_color}]{change_symbol}{change_pct:.2f}%[/{change_color}]",
                    f"{stock.volume:,}",
                    f"{market_cap:,.0f}"
                )
            
            panel = Panel(
                table,
                title=f"📈 JC股票市场 - 共 {len(stocks)} 只股票",
                border_style="blue"
            )
            
            return CommandResult(
                success=True,
                message=self._render_rich_object(panel)
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"获取股票列表失败: {str(e)}"
            )
    
    async def _show_stock_info(self, args: List[str], context) -> CommandResult:
        """显示股票详细信息"""
        if not args:
            return CommandResult(
                success=False,
                message="请指定股票代码，例如: jcmarket info AAPL"
            )
        
        symbol = args[0].upper()
        
        try:
            stock = await self.stock_service.get_stock_by_symbol(symbol)
            if not stock:
                return CommandResult(
                    success=False,
                    message=f"未找到股票代码: {symbol}"
                )
            
            # 计算涨跌
            current_price = stock.current_price or 0
            previous_close = stock.previous_close or current_price
            day_high = stock.day_high or current_price
            day_low = stock.day_low or current_price
            total_shares = stock.total_shares or 0
            change = current_price - previous_close
            change_pct = (change / previous_close * 100) if previous_close > 0 else 0
            market_cap = current_price * total_shares
            
            # 创建股票信息面板
            info_table = Table(show_header=False, box=None, padding=(0, 1))
            info_table.add_column("项目", style="cyan", width=12)
            info_table.add_column("数值", style="white")
            
            change_color = "green" if change >= 0 else "red"
            change_symbol = "+" if change >= 0 else ""
            
            info_table.add_row("📊 股票代码", stock.symbol)
            info_table.add_row("🏢 公司名称", stock.name)
            info_table.add_row("💰 当前价格", f"{current_price:.2f} JCY")
            info_table.add_row("📊 涨跌额", f"[{change_color}]{change_symbol}{change:.2f} JCY[/{change_color}]")
            info_table.add_row("📈 涨跌幅", f"[{change_color}]{change_symbol}{change_pct:.2f}%[/{change_color}]")
            info_table.add_row("📅 昨日收盘", f"{previous_close:.2f} JCY")
            info_table.add_row("📈 今日最高", f"{day_high:.2f} JCY")
            info_table.add_row("📉 今日最低", f"{day_low:.2f} JCY")
            info_table.add_row("💹 市值", f"{market_cap:,.0f} JCY")
            info_table.add_row("🏛️ 总股本", f"{total_shares:,} 股")
            info_table.add_row("⏰ 更新时间", stock.last_updated.strftime("%Y-%m-%d %H:%M:%S") if stock.last_updated else "未知")
            
            panel = Panel(
                info_table,
                title=f"📋 {stock.name} ({stock.symbol}) 详细信息",
                border_style="blue"
            )
            
            return CommandResult(
                success=True,
                message=self._render_rich_object(panel)
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"获取股票信息失败: {str(e)}"
            )
    
    async def _buy_stock(self, args: List[str], context) -> CommandResult:
        """购买股票"""
        if len(args) < 2:
            return CommandResult(
                success=False,
                message="请指定股票代码和数量，例如: jcmarket buy AAPL 100"
            )
        
        symbol = args[0].upper()
        try:
            quantity = int(args[1])
        except ValueError:
            return CommandResult(
                success=False,
                message="股票数量必须是整数"
            )
        
        if quantity <= 0:
            return CommandResult(
                success=False,
                message="股票数量必须大于0"
            )
        
        try:
            result = await self.stock_service.buy_stock(
                user_id=context.user.user_id,
                symbol=symbol,
                quantity=quantity
            )
            
            if result['success']:
                return CommandResult(
                    success=True,
                    message=f"✅ 成功购买 {symbol} {quantity} 股，总价: {result['total_cost']:.2f} JCY"
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"❌ 购买失败: {result['message']}"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"购买股票失败: {str(e)}"
            )
    
    async def _sell_stock(self, args: List[str], context) -> CommandResult:
        """卖出股票"""
        if len(args) < 2:
            return CommandResult(
                success=False,
                message="请指定股票代码和数量，例如: jcmarket sell AAPL 50"
            )
        
        symbol = args[0].upper()
        try:
            quantity = int(args[1])
        except ValueError:
            return CommandResult(
                success=False,
                message="股票数量必须是整数"
            )
        
        if quantity <= 0:
            return CommandResult(
                success=False,
                message="股票数量必须大于0"
            )
        
        try:
            result = await self.stock_service.sell_stock(
                user_id=context.user.user_id,
                symbol=symbol,
                quantity=quantity
            )
            
            if result['success']:
                return CommandResult(
                    success=True,
                    message=f"✅ 成功卖出 {symbol} {quantity} 股，总收入: {result['total_income']:.2f} JCY"
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"❌ 卖出失败: {result['message']}"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"卖出股票失败: {str(e)}"
            )
    
    async def _show_portfolio(self, context) -> CommandResult:
        """显示用户持仓"""
        try:
            holdings = await self.stock_service.get_user_holdings(context.user.user_id)
            
            if not holdings:
                return CommandResult(
                    success=True,
                    message="📊 您当前没有持有任何股票"
                )
            
            # 创建持仓表格
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("代码", style="cyan", width=8)
            table.add_column("名称", style="white", width=15)
            table.add_column("持股数", style="yellow", width=8)
            table.add_column("成本价", style="blue", width=8)
            table.add_column("现价", style="green", width=8)
            table.add_column("市值", style="green", width=10)
            table.add_column("盈亏", style="red", width=10)
            table.add_column("盈亏率", style="red", width=8)
            
            total_cost = 0
            total_value = 0
            
            for holding in holdings:
                stock = await self.stock_service.get_stock_by_symbol(holding.symbol)
                if not stock:
                    continue
                
                cost = holding.average_cost * holding.quantity
                current_price = stock.current_price or 0
                current_value = current_price * holding.quantity
                profit_loss = current_value - cost
                profit_loss_pct = (profit_loss / cost * 100) if cost > 0 else 0
                
                total_cost += cost
                total_value += current_value
                
                pl_color = "green" if profit_loss >= 0 else "red"
                pl_symbol = "+" if profit_loss >= 0 else ""
                
                table.add_row(
                    holding.symbol,
                    stock.name,
                    f"{holding.quantity:,}",
                    f"{holding.average_cost:.2f}",
                    f"{current_price:.2f}",
                    f"{current_value:.2f}",
                    f"[{pl_color}]{pl_symbol}{profit_loss:.2f}[/{pl_color}]",
                    f"[{pl_color}]{pl_symbol}{profit_loss_pct:.2f}%[/{pl_color}]"
                )
            
            # 添加总计行
            total_pl = total_value - total_cost
            total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
            total_pl_color = "green" if total_pl >= 0 else "red"
            total_pl_symbol = "+" if total_pl >= 0 else ""
            
            table.add_section()
            table.add_row(
                "[bold]总计[/bold]",
                "",
                "",
                "",
                "",
                f"[bold]{total_value:.2f}[/bold]",
                f"[bold {total_pl_color}]{total_pl_symbol}{total_pl:.2f}[/bold {total_pl_color}]",
                f"[bold {total_pl_color}]{total_pl_symbol}{total_pl_pct:.2f}%[/bold {total_pl_color}]"
            )
            
            panel = Panel(
                table,
                title=f"📊 我的股票持仓 - 总市值: {total_value:.2f} JCY",
                border_style="blue"
            )
            
            return CommandResult(
                success=True,
                message=self._render_rich_object(panel)
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"获取持仓信息失败: {str(e)}"
            )
    
    async def _watch_market(self, args: List[str], context) -> CommandResult:
        """实时监控市场"""
        return CommandResult(
            success=True,
            message="📺 实时监控功能开发中，敬请期待！"
        )
    
    async def _show_help(self) -> CommandResult:
        """显示帮助信息"""
        help_text = Text()
        help_text.append("📈 JC股票市场命令帮助\n\n", style="bold cyan")
        
        help_text.append("🔍 查看命令:\n", style="bold yellow")
        help_text.append("  jcmarket              - 显示市场概览\n", style="white")
        help_text.append("  jcmarket list         - 列出所有股票\n", style="white")
        help_text.append("  jcmarket info <代码>   - 查看股票详情\n", style="white")
        help_text.append("  jcmarket portfolio    - 查看我的持仓\n\n", style="white")
        
        help_text.append("💰 交易命令:\n", style="bold green")
        help_text.append("  jcmarket buy <代码> <数量>   - 购买股票\n", style="white")
        help_text.append("  jcmarket sell <代码> <数量>  - 卖出股票\n\n", style="white")
        
        help_text.append("📊 监控命令:\n", style="bold blue")
        help_text.append("  jcmarket watch        - 实时监控市场\n\n", style="white")
        
        help_text.append("💡 使用示例:\n", style="bold magenta")
        help_text.append("  jcmarket info AAPL    - 查看苹果公司股票信息\n", style="white")
        help_text.append("  jcmarket buy AAPL 100 - 购买100股苹果股票\n", style="white")
        help_text.append("  jcmarket sell AAPL 50 - 卖出50股苹果股票\n", style="white")
        
        panel = Panel(
            help_text,
            title="📋 JC股票市场帮助",
            border_style="cyan"
        )
        
        return CommandResult(
            success=True,
            message=self._render_rich_object(panel)
        )