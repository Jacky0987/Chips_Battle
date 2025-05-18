import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")

from views.charts.price_chart import PriceChart
from views.charts.portfolio_chart import PortfolioChart
from views.charts.comparison_chart import ComparisonChart
from views.charts.sector_chart import SectorChart
from views.widgets.stock_list import StockList
from views.widgets.portfolio_view import PortfolioView
from views.widgets.trading_panel import TradingPanel
from views.widgets.news_feed import NewsFeed

class StockMarketGameApp:
    def __init__(self, root):
        self.root = root
        root.title("Stock Market Simulator")
        root.geometry("1600x800")
        
        # Create navigation buttons frame at the top
        self.nav_frame = ttk.Frame(root)
        self.nav_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=5)
        
        # Add navigation buttons to the top
        self.next_day_button = ttk.Button(self.nav_frame, text="Next Day")
        self.next_day_button.pack(side=tk.LEFT, padx=10)
        
        self.next_week_button = ttk.Button(self.nav_frame, text="Next Week (5 Days)")
        self.next_week_button.pack(side=tk.LEFT, padx=10)
        
        self.next_month_button = ttk.Button(self.nav_frame, text="Next Month (21 Days)")
        self.next_month_button.pack(side=tk.LEFT, padx=10)
        
        # Set up the main notebook with tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the main game tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        
        # Create portfolio tab
        self.portfolio_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.portfolio_tab, text="Portfolio")
        
        # Create charts tab
        self.charts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_tab, text="Charts")
        
        # Set up the main tab layout
        self.setup_main_tab()
        
        # Set up portfolio tab
        self.setup_portfolio_tab()
        
        # Set up charts tab
        self.setup_charts_tab()
        
        # Create status bar (now without navigation buttons)
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        # 取消注释这两行，创建必要的变量
        self.day_var = tk.StringVar(value="Day: 0")
        ttk.Label(self.status_frame, textvariable=self.day_var).pack(side=tk.LEFT, padx=10)
        
        self.cash_var = tk.StringVar(value="Cash: $10,000.00")
        ttk.Label(self.status_frame, textvariable=self.cash_var).pack(side=tk.LEFT, padx=10)
        
        # Reference to the game controller (to be set later)
        self.controller = None
        
    # 在trading_panel中添加交易完成后的回调函数
    def setup_main_tab(self):
        # Create a main container with configurable weights
        main_container = ttk.PanedWindow(self.main_tab, orient=tk.VERTICAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Upper section for stocks and charts
        upper_section = ttk.Frame(main_container)
        main_container.add(upper_section, weight=2)  # Give upper section more weight
        
        # Left side - stock list
        left_frame = ttk.Frame(upper_section)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.stock_list = StockList(left_frame)
        self.stock_list.get_frame().pack(fill=tk.BOTH, expand=True)
        
        # Right side - details and trading
        right_frame = ttk.Frame(upper_section)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # Stock price chart - make it smaller
        self.price_chart = PriceChart(right_frame)  # Removed height parameter
        self.price_chart.get_frame().pack(fill=tk.X)  # Don't expand vertically
        
        # Trading panel - make it more compact
        self.trading_panel = TradingPanel(right_frame)
        self.trading_panel.get_frame().pack(fill=tk.X)  # Don't expand vertically
        # 添加交易后更新UI的回调
        self.trading_panel.set_trade_callback(self.update_ui)
        
        # News feed section - give it more space
        news_section = ttk.LabelFrame(main_container, text="Market News")
        main_container.add(news_section, weight=1)  # Give news section significant weight
        
        # News feed with more height
        self.news_feed = NewsFeed(news_section)  # Removed height parameter
        self.news_feed.get_frame().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    def setup_portfolio_tab(self):
        # Left side - portfolio view
        left_frame = ttk.Frame(self.portfolio_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        
        self.portfolio_view = PortfolioView(left_frame)
        self.portfolio_view.get_frame().pack(fill=tk.BOTH, expand=True)
        
        # Right side - portfolio chart
        right_frame = ttk.Frame(self.portfolio_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.portfolio_chart = PortfolioChart(right_frame)
        self.portfolio_chart.get_frame().pack(fill=tk.BOTH, expand=True)
        
    def setup_charts_tab(self):
        # Create a notebook for different chart types
        self.charts_notebook = ttk.Notebook(self.charts_tab)
        self.charts_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Comparison chart tab
        comparison_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(comparison_frame, text="Performance Comparison")
        
        self.comparison_chart = ComparisonChart(comparison_frame)
        self.comparison_chart.get_frame().pack(fill=tk.BOTH, expand=True)
        
        # Sector chart tab
        sector_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(sector_frame, text="Sector Analysis")
        
        self.sector_chart = SectorChart(sector_frame)
        self.sector_chart.get_frame().pack(fill=tk.BOTH, expand=True)

    def set_controller(self, controller):
        self.controller = controller
        print(f"[DEBUG] 设置控制器到主窗口")
        
        # Set up callback functions
        self.stock_list.set_on_select_callback(self.on_stock_selected)
        self.portfolio_view.set_on_select_callback(self.on_portfolio_stock_selected)
        self.price_chart.set_update_callback(self.update_price_chart)
        self.comparison_chart.set_update_callback(self.update_comparison_chart)
        self.sector_chart.set_update_callback(self.update_sector_chart)
        
        # Set up button commands
        self.next_day_button.config(command=self.on_next_day)
        self.next_week_button.config(command=self.on_next_week)
        self.next_month_button.config(command=self.on_next_month)
        
        # Set market reference for trading panel
        self.trading_panel.set_market(controller.market)
        
    def update_ui(self):
        """Update all UI components"""
        market = self.controller.market
        print(f"[DEBUG] 更新UI: 当前天数={market.current_day}, 现金=${market.portfolio.cash:.2f}")
        
        # Update status bar
        self.day_var.set(f"Day: {market.current_day}")
        self.cash_var.set(f"Cash: ${market.portfolio.cash:.2f}")
        
        # Update stock list
        self.stock_list.set_sectors(market.sectors)
        self.stock_list.update_stocks(market.stocks)
        
        # 更新交易面板中当前选中股票的价格
        self.trading_panel.update_current_stock_price()
        
        # Update price chart
        selected_symbols = self.stock_list.get_selected_symbols()
        self.update_price_chart()
        
        # Update portfolio view
        self.portfolio_view.update(market.portfolio, market.stocks)
        
        # Update portfolio chart
        self.portfolio_chart.update(market.portfolio, market.portfolio.net_worth_history)
        
        # Update comparison chart
        self.update_comparison_chart()
        
        # Update sector chart
        self.update_sector_chart()
        
        # Update news feed
        self.news_feed.update(market.news_feed)
        
    def on_stock_selected(self, symbols):
        """Handle stock selection from the main stock list"""
        if symbols and len(symbols) > 0:
            # Get the first selected stock
            stock = next((s for s in self.controller.market.stocks if s.symbol == symbols[0]), None)
            if stock:
                # Update trading panel with selected stock
                self.trading_panel.select_stock(stock)
                
        # Update price chart with selected stocks
        self.update_price_chart()
        self.update_comparison_chart()
        
    def on_portfolio_stock_selected(self, symbol):
        """Handle stock selection from portfolio view"""
        if symbol:
            # Find the stock
            stock = next((s for s in self.controller.market.stocks if s.symbol == symbol), None)
            if stock:
                # Select in the main stock list and switch to main tab
                self.stock_list.tree.selection_set("")  # Clear current selection
                
                # Find and select the item in the tree
                for item in self.stock_list.tree.get_children():
                    if self.stock_list.tree.item(item)["values"][0] == symbol:
                        self.stock_list.tree.selection_set(item)
                        self.stock_list.tree.see(item)
                        break
                        
                # Update trading panel and switch to main tab
                self.trading_panel.select_stock(stock)
                self.notebook.select(0)  # Switch to main tab
                
    def update_price_chart(self):
        """Update the price chart with current selection"""
        selected_symbols = self.stock_list.get_selected_symbols()
        self.price_chart.update(self.controller.market.stocks, selected_symbols)
        
    def update_comparison_chart(self):
        """Update the comparison chart"""
        selected_symbols = self.stock_list.get_selected_symbols()
        self.comparison_chart.update(
            self.controller.market.stocks, 
            selected_symbols, 
            self.controller.market.portfolio.net_worth_history
        )
        
    def update_sector_chart(self):
        """Update the sector chart"""
        self.sector_chart.update(
            self.controller.market.stocks,
            self.controller.market.sectors,
            self.controller.market.portfolio
        )
        
    def on_next_day(self):
        """Advance the market by one day"""
        print(f"[DEBUG] 点击下一天按钮")
        if self.controller.next_day():
            self.update_ui()
        else:
            self.game_over()
            
    def on_next_week(self):
        """Advance the market by one week (5 days)"""
        print(f"[DEBUG] 点击下一周按钮 (5天)")
        for _ in range(5):
            if not self.controller.next_day():
                self.game_over()
                return
        self.update_ui()
        
    def on_next_month(self):
        """Advance the market by one month (21 days)"""
        print(f"[DEBUG] 点击下一月按钮 (21天)")
        for _ in range(21):
            if not self.controller.next_day():
                self.game_over()
                return
        self.update_ui()
        
    def game_over(self):
        """Handle game over"""
        result = self.controller.market.portfolio.get_final_evaluation()
        messagebox.showinfo("Game Over", result)
        
        # Disable trading buttons
        self.next_day_button.config(state=tk.DISABLED)
        self.next_week_button.config(state=tk.DISABLED)
        self.next_month_button.config(state=tk.DISABLED)

