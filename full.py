import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
from datetime import datetime, timedelta
import pandas as pd


class Stock:
    def __init__(self, name, symbol, initial_price, volatility, sector, pays_dividend=False, dividend_yield=0):
        self.name = name
        self.symbol = symbol
        self.price = initial_price
        self.volatility = volatility  # Percentage volatility per day
        self.sector = sector
        self.price_history = [initial_price]
        self.pays_dividend = pays_dividend
        self.dividend_yield = dividend_yield
        self.next_dividend_day = random.randint(5, 10) if pays_dividend else -1

    def update_price(self, sector_influence=0):
        # Base random movement based on volatility
        change_percent = random.normalvariate(0, self.volatility)

        # Add sector influence (stocks in same sector move similarly)
        change_percent += sector_influence

        # Calculate new price
        new_price = self.price * (1 + change_percent / 100)

        # Ensure price doesn't go below 0.1
        self.price = max(0.1, new_price)
        self.price_history.append(self.price)

    def check_dividend(self, current_day):
        if self.pays_dividend and current_day == self.next_dividend_day:
            dividend_amount = self.price * (self.dividend_yield / 100)
            self.next_dividend_day = current_day + random.randint(5, 10)
            return dividend_amount
        return 0


class MarketSimulator:
    def __init__(self):
        # Define sectors
        self.sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer"]

        # Create stocks with different characteristics
        self.stocks = [
            Stock("TechGiant", "TGT", 150.0, 2.5, "Technology", True, 0.5),
            Stock("MediHealth", "MHC", 85.0, 1.8, "Healthcare", True, 1.2),
            Stock("BankCorp", "BNK", 65.0, 1.5, "Finance", True, 2.5),
            Stock("EnergyOne", "ENO", 40.0, 2.2, "Energy", False, 0),
            Stock("RetailShop", "RSP", 55.0, 1.7, "Consumer", True, 1.0),
            Stock("StartupTech", "STU", 25.0, 3.5, "Technology", False, 0),
            Stock("PharmaCure", "PHC", 120.0, 2.0, "Healthcare", True, 0.8),
            Stock("InvestFund", "INF", 95.0, 1.6, "Finance", True, 1.8),
            Stock("OilDrill", "ODL", 70.0, 2.3, "Energy", True, 3.0),
            Stock("FoodMarket", "FMT", 45.0, 1.5, "Consumer", True, 1.5)
        ]

        # Dictionary to track stocks by symbol
        self.stock_dict = {stock.symbol: stock for stock in self.stocks}

        # News events that can occur
        self.news_events = [
            {"headline": "Economic Boom: Markets Rally", "impact": {"sector": "all", "change": 3.0}},
            {"headline": "Market Crash: Investors Panic", "impact": {"sector": "all", "change": -4.0}},
            {"headline": "Tech Innovation Breakthrough", "impact": {"sector": "Technology", "change": 5.0}},
            {"headline": "Healthcare Reform Announced", "impact": {"sector": "Healthcare", "change": 4.0}},
            {"headline": "Banking Scandal Erupts", "impact": {"sector": "Finance", "change": -5.0}},
            {"headline": "Oil Price Surge", "impact": {"sector": "Energy", "change": 6.0}},
            {"headline": "Consumer Spending Drops", "impact": {"sector": "Consumer", "change": -3.0}},
            {"headline": "New Tech Regulations", "impact": {"sector": "Technology", "change": -4.0}},
            {"headline": "Medical Breakthrough", "impact": {"sector": "Healthcare", "change": 7.0}},
            {"headline": "Interest Rates Cut", "impact": {"sector": "Finance", "change": 4.0}},
            {"headline": "Renewable Energy Push", "impact": {"sector": "Energy", "change": -3.0}},
            {"headline": "Retail Sales Boom", "impact": {"sector": "Consumer", "change": 5.0}}
        ]

        # Stock-specific news events
        self.stock_news_events = [
            {"headline": "TechGiant Launches New Product", "impact": {"stock": "TGT", "change": 8.0}},
            {"headline": "MediHealth Recalls Drug", "impact": {"stock": "MHC", "change": -7.0}},
            {"headline": "BankCorp Announces Expansion", "impact": {"stock": "BNK", "change": 6.0}},
            {"headline": "Oil Spill at EnergyOne Facility", "impact": {"stock": "ENO", "change": -9.0}},
            {"headline": "RetailShop Beats Earnings Estimates", "impact": {"stock": "RSP", "change": 7.0}},
        ]

        # Game settings
        self.current_day = 0
        self.max_days = 300
        self.starting_cash = 10000

        # Player portfolio
        self.portfolio = {"cash": self.starting_cash, "stocks": {}}
        self.transaction_history = []
        self.net_worth_history = [self.starting_cash]

        # News feed
        self.news_feed = ["Welcome to Stock Market Simulator! You have $10,000 to invest."]

    def simulate_day(self):
        if self.current_day >= self.max_days:
            return False

        self.current_day += 1

        # Initialize sector movements
        sector_movements = {sector: random.normalvariate(0, 1.0) for sector in self.sectors}

        # Chance for a market-wide or sector news event
        if random.random() < 0.3:  # 30% chance of news event each day
            news_event = random.choice(self.news_events)
            self.news_feed.insert(0, f"Day {self.current_day}: {news_event['headline']}")

            if news_event["impact"]["sector"] == "all":
                for sector in self.sectors:
                    sector_movements[sector] += news_event["impact"]["change"]
            else:
                sector_movements[news_event["impact"]["sector"]] += news_event["impact"]["change"]

        # Chance for stock-specific news
        if random.random() < 0.2:  # 20% chance of stock-specific news
            stock_news = random.choice(self.stock_news_events)
            self.news_feed.insert(0, f"Day {self.current_day}: {stock_news['headline']}")
            affected_stock = stock_news["impact"]["stock"]

            # Apply direct impact to stock
            stock = self.stock_dict.get(affected_stock)
            if stock:
                change_percent = stock_news["impact"]["change"]
                current_price = stock.price
                stock.price = max(0.1, current_price * (1 + change_percent / 100))

        # Update each stock price
        for stock in self.stocks:
            if stock.symbol != affected_stock if 'affected_stock' in locals() else True:
                stock.update_price(sector_movements[stock.sector])

            # Check for dividends
            dividend = stock.check_dividend(self.current_day)
            if dividend > 0 and stock.symbol in self.portfolio["stocks"]:
                shares_owned = self.portfolio["stocks"][stock.symbol]
                dividend_total = dividend * shares_owned
                self.portfolio["cash"] += dividend_total
                self.news_feed.insert(0,
                                      f"Day {self.current_day}: Received ${dividend_total:.2f} in dividends from {stock.name}")

        # Update portfolio value history
        self.update_net_worth()

        return True

    def update_net_worth(self):
        net_worth = self.portfolio["cash"]
        for symbol, shares in self.portfolio["stocks"].items():
            stock = self.stock_dict[symbol]
            net_worth += stock.price * shares

        self.net_worth_history.append(net_worth)
        return net_worth

    def buy_stock(self, symbol, shares):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        stock = self.stock_dict.get(symbol)
        if not stock:
            return "Invalid stock symbol"

        cost = stock.price * shares

        if cost > self.portfolio["cash"]:
            return "Not enough cash for this purchase"

        # Execute the trade
        self.portfolio["cash"] -= cost

        if symbol in self.portfolio["stocks"]:
            self.portfolio["stocks"][symbol] += shares
        else:
            self.portfolio["stocks"][symbol] = shares

        # Record transaction
        self.transaction_history.append({
            "day": self.current_day,
            "type": "BUY",
            "symbol": symbol,
            "shares": shares,
            "price": stock.price,
            "total": cost
        })

        return f"Bought {shares} shares of {symbol} at ${stock.price:.2f} for ${cost:.2f}"

    def sell_stock(self, symbol, shares):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        if symbol not in self.portfolio["stocks"] or self.portfolio["stocks"][symbol] < shares:
            return "Not enough shares to sell"

        stock = self.stock_dict[symbol]
        proceeds = stock.price * shares

        # Execute the trade
        self.portfolio["cash"] += proceeds
        self.portfolio["stocks"][symbol] -= shares

        # Remove stock from portfolio if no shares left
        if self.portfolio["stocks"][symbol] == 0:
            del self.portfolio["stocks"][symbol]

        # Record transaction
        self.transaction_history.append({
            "day": self.current_day,
            "type": "SELL",
            "symbol": symbol,
            "shares": shares,
            "price": stock.price,
            "total": proceeds
        })

        return f"Sold {shares} shares of {symbol} at ${stock.price:.2f} for ${proceeds:.2f}"

    def short_sell(self, symbol, shares):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        stock = self.stock_dict.get(symbol)
        if not stock:
            return "Invalid stock symbol"

        # In a short sale, you borrow shares and sell them
        proceeds = stock.price * shares
        self.portfolio["cash"] += proceeds

        # Track the short position (negative shares)
        if symbol in self.portfolio["stocks"]:
            self.portfolio["stocks"][symbol] -= shares
        else:
            self.portfolio["stocks"][symbol] = -shares

        # Record transaction
        self.transaction_history.append({
            "day": self.current_day,
            "type": "SHORT",
            "symbol": symbol,
            "shares": shares,
            "price": stock.price,
            "total": proceeds
        })

        return f"Short sold {shares} shares of {symbol} at ${stock.price:.2f} for ${proceeds:.2f}"

    def cover_short(self, symbol, shares):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        if symbol not in self.portfolio["stocks"] or self.portfolio["stocks"][symbol] >= 0 or abs(
                self.portfolio["stocks"][symbol]) < shares:
            return "Not enough shares to cover"

        stock = self.stock_dict[symbol]
        cost = stock.price * shares

        if cost > self.portfolio["cash"]:
            return "Not enough cash to cover this short position"

        # Execute the cover
        self.portfolio["cash"] -= cost
        self.portfolio["stocks"][symbol] += shares

        # Remove stock from portfolio if no shares left
        if self.portfolio["stocks"][symbol] == 0:
            del self.portfolio["stocks"][symbol]

        # Record transaction
        self.transaction_history.append({
            "day": self.current_day,
            "type": "COVER",
            "symbol": symbol,
            "shares": shares,
            "price": stock.price,
            "total": cost
        })

        return f"Covered {shares} short shares of {symbol} at ${stock.price:.2f} for ${cost:.2f}"

    def get_portfolio_summary(self):
        summary = []
        total_value = self.portfolio["cash"]

        summary.append(f"Cash: ${self.portfolio['cash']:.2f}")

        if self.portfolio["stocks"]:
            summary.append("\nHoldings:")
            for symbol, shares in self.portfolio["stocks"].items():
                stock = self.stock_dict[symbol]
                value = stock.price * abs(shares)
                position_type = "LONG" if shares > 0 else "SHORT"
                total_value += value if shares > 0 else -value
                summary.append(f"{symbol} ({position_type}): {abs(shares)} shares at ${stock.price:.2f} = ${value:.2f}")

        summary.append(f"\nTotal Portfolio Value: ${total_value:.2f}")

        initial_value = self.starting_cash
        profit_loss = total_value - initial_value
        profit_loss_percent = (profit_loss / initial_value) * 100

        summary.append(f"Profit/Loss: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)")

        return "\n".join(summary)

    def get_final_evaluation(self):
        final_value = self.update_net_worth()
        profit_loss = final_value - self.starting_cash
        profit_loss_percent = (profit_loss / self.starting_cash) * 100

        if profit_loss_percent >= 50:
            rating = "Exceptional Investor"
        elif profit_loss_percent >= 25:
            rating = "Skilled Investor"
        elif profit_loss_percent >= 10:
            rating = "Good Investor"
        elif profit_loss_percent >= 0:
            rating = "Average Investor"
        elif profit_loss_percent >= -10:
            rating = "Novice Investor"
        else:
            rating = "Needs Improvement"

        evaluation = [
            "=== FINAL PERFORMANCE EVALUATION ===",
            f"Starting Capital: ${self.starting_cash:.2f}",
            f"Final Portfolio Value: ${final_value:.2f}",
            f"Profit/Loss: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)",
            f"Rating: {rating}",
            "\nTrading Statistics:",
            f"Total Days Traded: {self.current_day}",
            f"Total Transactions: {len(self.transaction_history)}",
        ]

        if self.transaction_history:
            buys = sum(1 for t in self.transaction_history if t["type"] == "BUY")
            sells = sum(1 for t in self.transaction_history if t["type"] == "SELL")
            shorts = sum(1 for t in self.transaction_history if t["type"] == "SHORT")
            covers = sum(1 for t in self.transaction_history if t["type"] == "COVER")

            evaluation.extend([
                f"Buy Transactions: {buys}",
                f"Sell Transactions: {sells}",
                f"Short Transactions: {shorts}",
                f"Cover Transactions: {covers}"
            ])

        return "\n".join(evaluation)


class StockMarketGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Market Simulator")
        self.root.geometry("1600x800")
        self.root.resizable(True, True)

        self.simulator = MarketSimulator()

        self.create_widgets()
        # Setup charts AFTER creating widgets
        self.setup_charts()
        self.update_displays()

    def create_widgets(self):
        # Create main frames
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for game controls
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))

        self.next_day_btn = ttk.Button(self.top_frame, text="Next Day", command=self.advance_day)
        self.next_day_btn.pack(side=tk.LEFT)

        self.day_label = ttk.Label(self.top_frame, text="Day: 0/30")
        self.day_label.pack(side=tk.LEFT, padx=20)

        self.cash_label = ttk.Label(self.top_frame, text=f"Cash: ${self.simulator.portfolio['cash']:.2f}")
        self.cash_label.pack(side=tk.LEFT, padx=20)

        self.net_worth_label = ttk.Label(self.top_frame, text=f"Net Worth: ${self.simulator.portfolio['cash']:.2f}")
        self.net_worth_label.pack(side=tk.LEFT, padx=20)

        # Split the main area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Charts and Stock Table
        self.left_frame = ttk.Frame(self.content_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Charts area - enhanced with more options
        self.charts_frame = ttk.LabelFrame(self.left_frame, text="Market Charts")
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Chart control panel
        self.chart_controls = ttk.Frame(self.charts_frame)
        self.chart_controls.pack(fill=tk.X, padx=5, pady=5)

        # Chart type selection
        ttk.Label(self.chart_controls, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        self.chart_type_var = tk.StringVar(value="Line")
        chart_type_combo = ttk.Combobox(self.chart_controls, textvariable=self.chart_type_var,
                                        values=["Line", "Candlestick", "Area"], width=12)
        chart_type_combo.pack(side=tk.LEFT, padx=5)
        chart_type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stock_price_chart())

        # Time range selection
        ttk.Label(self.chart_controls, text="Time Range:").pack(side=tk.LEFT, padx=5)
        self.time_range_var = tk.StringVar(value="All")
        time_range_combo = ttk.Combobox(self.chart_controls, textvariable=self.time_range_var,
                                        values=["All", "5 Days", "10 Days", "15 Days"], width=10)
        time_range_combo.pack(side=tk.LEFT, padx=5)
        time_range_combo.bind("<<ComboboxSelected>>", lambda e: self.update_stock_price_chart())

        # Technical indicators
        ttk.Label(self.chart_controls, text="Indicators:").pack(side=tk.LEFT, padx=5)
        self.show_ma_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.chart_controls, text="Moving Avg", variable=self.show_ma_var,
                        command=self.update_stock_price_chart).pack(side=tk.LEFT)

        # Button to toggle between single/multi stock view
        self.multi_stock_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.chart_controls, text="Multi-Stock View", variable=self.multi_stock_var,
                        command=self.update_stock_price_chart).pack(side=tk.LEFT, padx=10)

        # Export button
        ttk.Button(self.chart_controls, text="Export Chart", command=self.export_chart).pack(side=tk.RIGHT, padx=5)

        # Create tabs for different charts
        self.chart_notebook = ttk.Notebook(self.charts_frame)
        self.chart_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Stock price chart
        self.price_chart_frame = ttk.Frame(self.chart_notebook)
        self.chart_notebook.add(self.price_chart_frame, text="Stock Prices")

        # Portfolio value chart
        self.portfolio_chart_frame = ttk.Frame(self.chart_notebook)
        self.chart_notebook.add(self.portfolio_chart_frame, text="Portfolio Value")

        # Performance comparison tab
        self.comparison_chart_frame = ttk.Frame(self.chart_notebook)
        self.chart_notebook.add(self.comparison_chart_frame, text="Performance Comparison")

        # Sector performance tab
        self.sector_chart_frame = ttk.Frame(self.chart_notebook)
        self.chart_notebook.add(self.sector_chart_frame, text="Sector Performance")

        # Stock table
        self.stocks_frame = ttk.LabelFrame(self.left_frame, text="Stocks")
        self.stocks_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        # Create the treeview for stocks
        columns = ("Symbol", "Name", "Price", "Change", "Sector")
        self.stocks_tree = ttk.Treeview(self.stocks_frame, columns=columns, show="headings", height=10)

        # Configure columns
        self.stocks_tree.heading("Symbol", text="Symbol")
        self.stocks_tree.heading("Name", text="Name")
        self.stocks_tree.heading("Price", text="Price")
        self.stocks_tree.heading("Change", text="Change")
        self.stocks_tree.heading("Sector", text="Sector")

        self.stocks_tree.column("Symbol", width=80)
        self.stocks_tree.column("Name", width=150)
        self.stocks_tree.column("Price", width=100)
        self.stocks_tree.column("Change", width=100)
        self.stocks_tree.column("Sector", width=120)

        # Add scrollbar
        stocks_scrollbar = ttk.Scrollbar(self.stocks_frame, orient=tk.VERTICAL, command=self.stocks_tree.yview)
        self.stocks_tree.configure(yscrollcommand=stocks_scrollbar.set)

        self.stocks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stocks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right side - Trading, Portfolio, News
        self.right_frame = ttk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Trading interface
        self.trading_frame = ttk.LabelFrame(self.right_frame, text="Trading")
        self.trading_frame.pack(fill=tk.X, padx=5, pady=5)

        # Stock selection
        ttk.Label(self.trading_frame, text="Stock:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.stock_var = tk.StringVar()
        self.stock_combo = ttk.Combobox(self.trading_frame, textvariable=self.stock_var, width=15)
        self.stock_combo['values'] = [stock.symbol for stock in self.simulator.stocks]
        self.stock_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Shares input
        ttk.Label(self.trading_frame, text="Shares:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.shares_var = tk.StringVar()
        self.shares_entry = ttk.Entry(self.trading_frame, textvariable=self.shares_var, width=10)
        self.shares_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # Trading buttons
        self.buy_btn = ttk.Button(self.trading_frame, text="Buy", command=self.buy_stock)
        self.buy_btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.sell_btn = ttk.Button(self.trading_frame, text="Sell", command=self.sell_stock)
        self.sell_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.short_btn = ttk.Button(self.trading_frame, text="Short", command=self.short_stock)
        self.short_btn.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        self.cover_btn = ttk.Button(self.trading_frame, text="Cover", command=self.cover_stock)
        self.cover_btn.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # Portfolio display
        self.portfolio_frame = ttk.LabelFrame(self.right_frame, text="Portfolio")
        self.portfolio_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.portfolio_text = scrolledtext.ScrolledText(self.portfolio_frame, wrap=tk.WORD, height=10)
        self.portfolio_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # News feed
        self.news_frame = ttk.LabelFrame(self.right_frame, text="Market News")
        self.news_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.news_text = scrolledtext.ScrolledText(self.news_frame, wrap=tk.WORD, height=10)
        self.news_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_charts(self):
        # Stock price chart
        self.price_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.price_canvas = FigureCanvasTkAgg(self.price_fig, self.price_chart_frame)
        self.price_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar for zooming/panning
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.price_toolbar = NavigationToolbar2Tk(self.price_canvas, self.price_chart_frame)
        self.price_toolbar.update()

        # Portfolio value chart
        self.portfolio_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.portfolio_canvas = FigureCanvasTkAgg(self.portfolio_fig, self.portfolio_chart_frame)
        self.portfolio_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.portfolio_toolbar = NavigationToolbar2Tk(self.portfolio_canvas, self.portfolio_chart_frame)
        self.portfolio_toolbar.update()

        # Performance comparison chart
        self.comparison_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, self.comparison_chart_frame)
        self.comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add comparison controls
        comparison_controls = ttk.Frame(self.comparison_chart_frame)
        comparison_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(comparison_controls, text="Base Value:").pack(side=tk.LEFT, padx=5)
        self.comparison_base_var = tk.StringVar(value="First Day")
        ttk.Combobox(comparison_controls, textvariable=self.comparison_base_var,
                     values=["First Day", "100%"], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(comparison_controls, text="Update",
                   command=self.update_comparison_chart).pack(side=tk.LEFT, padx=5)

        # Sector performance chart
        self.sector_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.sector_canvas = FigureCanvasTkAgg(self.sector_fig, self.sector_chart_frame)
        self.sector_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add sector controls
        sector_controls = ttk.Frame(self.sector_chart_frame)
        sector_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(sector_controls, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        self.sector_chart_type_var = tk.StringVar(value="Line")
        ttk.Combobox(sector_controls, textvariable=self.sector_chart_type_var,
                     values=["Line", "Bar", "Pie"], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(sector_controls, text="Update",
                   command=self.update_sector_chart).pack(side=tk.LEFT, padx=5)

    def update_stock_price_chart(self):
        self.price_fig.clear()
        ax = self.price_fig.add_subplot(111)

        # Get selected time range
        time_range = self.time_range_var.get()
        days_to_show = None
        if time_range == "5 Days":
            days_to_show = 5
        elif time_range == "10 Days":
            days_to_show = 10
        elif time_range == "15 Days":
            days_to_show = 15

        # Get the selected stocks (or all if none selected)
        selected_items = self.stocks_tree.selection()
        if selected_items and not self.multi_stock_var.get():
            # Single stock view
            selected_symbols = [self.stocks_tree.item(selected_items[0], "values")[0]]
            selected_stocks = [stock for stock in self.simulator.stocks if stock.symbol in selected_symbols]
        else:
            # Multi-stock view - show top 5 or selected
            if selected_items:
                selected_symbols = [self.stocks_tree.item(item, "values")[0] for item in selected_items]
                selected_stocks = [stock for stock in self.simulator.stocks if stock.symbol in selected_symbols]
            else:
                selected_stocks = self.simulator.stocks[:5]

        chart_type = self.chart_type_var.get()

        # Initialize affected_stock to None to avoid reference errors
        affected_stock = None

        for stock in selected_stocks:
            price_history = stock.price_history

            # Apply time range filter if needed
            if days_to_show and len(price_history) > days_to_show:
                price_history = price_history[-days_to_show:]
                days = list(range(len(price_history)))
                start_day = len(stock.price_history) - days_to_show
                days = [d + start_day for d in days]
            else:
                days = list(range(len(price_history)))

            # Draw based on chart type
            if chart_type == "Line":
                ax.plot(days, price_history, label=stock.symbol)

            elif chart_type == "Area":
                ax.fill_between(days, price_history, alpha=0.3, label=stock.symbol)
                ax.plot(days, price_history, alpha=0.6)

            elif chart_type == "Candlestick":
                # For demonstration, create simple OHLC data
                # In a real app, you'd track actual OHLC data
                if len(price_history) > 1:
                    from matplotlib.patches import Rectangle

                    width = 0.8
                    for i in range(1, len(price_history)):
                        open_price = price_history[i - 1]
                        close_price = price_history[i]

                        # Simulate high/low with some random variation
                        high = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
                        low = min(open_price, close_price) * (1 - random.uniform(0, 0.02))

                        # Draw candlestick
                        color = 'green' if close_price >= open_price else 'red'
                        rect = Rectangle((i - width / 2, min(open_price, close_price)),
                                         width, abs(close_price - open_price),
                                         facecolor=color, edgecolor='black', alpha=0.6)
                        ax.add_patch(rect)

                        # Draw wicks
                        ax.plot([i, i], [low, min(open_price, close_price)], color='black', linewidth=1)
                        ax.plot([i, i], [max(open_price, close_price), high], color='black', linewidth=1)

            # Add moving average if selected
            if self.show_ma_var.get() and len(price_history) > 5:
                window_size = 5  # 5-day moving average
                ma = [sum(price_history[max(0, i - window_size + 1):i + 1]) / min(i + 1, window_size)
                      for i in range(len(price_history))]
                ax.plot(days, ma, '--', alpha=0.7, label=f"{stock.symbol} MA-{window_size}")

        ax.set_title("Stock Price History")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price ($)")
        ax.legend(loc="upper left")
        ax.grid(True)

        # Add annotations for key events if in single stock view
        if len(selected_stocks) == 1 and not self.multi_stock_var.get():
            stock = selected_stocks[0]
            symbol = stock.symbol

            # Find news events for this stock
            for news in self.simulator.stock_news_events:
                if news["impact"]["stock"] == symbol:
                    # Find days when this news might have happened
                    for i in range(1, len(stock.price_history)):
                        # Look for large price changes that might correspond to news
                        change_pct = ((stock.price_history[i] - stock.price_history[i - 1]) /
                                      stock.price_history[i - 1]) * 100
                        if abs(change_pct) > 3:  # Significant change
                            ax.annotate('News Event', xy=(i, stock.price_history[i]),
                                        xytext=(i, stock.price_history[i] * 1.1),
                                        arrowprops=dict(facecolor='red', shrink=0.05),
                                        fontsize=8)
                            break

        self.price_canvas.draw()

    def update_portfolio_chart(self):
        self.portfolio_fig.clear()
        ax = self.portfolio_fig.add_subplot(111)

        days = list(range(len(self.simulator.net_worth_history)))
        ax.plot(days, self.simulator.net_worth_history, label="Net Worth", color="green")

        ax.set_title("Portfolio Value History")
        ax.set_xlabel("Day")
        ax.set_ylabel("Value ($)")
        ax.axhline(y=self.simulator.starting_cash, color='r', linestyle='-', alpha=0.3, label="Starting Cash")
        ax.legend(loc="upper left")
        ax.grid(True)

        self.portfolio_canvas.draw()

    def update_stock_table(self):
        # Clear existing items
        for item in self.stocks_tree.get_children():
            self.stocks_tree.delete(item)

        # Add current stock data
        for stock in self.simulator.stocks:
            price_change = 0
            if len(stock.price_history) >= 2:
                prev_price = stock.price_history[-2]
                price_change = ((stock.price - prev_price) / prev_price) * 100

            # Format price change with color indicator
            change_text = f"{price_change:.2f}%"
            if price_change > 0:
                change_text = "↑ " + change_text
                change_color = "green"
            elif price_change < 0:
                change_text = "↓ " + change_text
                change_color = "red"
            else:
                change_text = "- " + change_text
                change_color = "black"

            values = (stock.symbol, stock.name, f"${stock.price:.2f}", change_text, stock.sector)
            item_id = self.stocks_tree.insert("", tk.END, values=values)

            # Apply color to the change column
            self.stocks_tree.tag_configure(change_color, foreground=change_color)
            if price_change != 0:
                self.stocks_tree.item(item_id, tags=(change_color,))

    def update_portfolio_display(self):
        self.portfolio_text.delete(1.0, tk.END)
        self.portfolio_text.insert(tk.END, self.simulator.get_portfolio_summary())

    def update_news_feed(self):
        self.news_text.delete(1.0, tk.END)
        for news in self.simulator.news_feed[:10]:  # Show latest 10 news items
            self.news_text.insert(tk.END, news + "\n\n")

    def update_displays(self):
        self.day_label.config(text=f"Day: {self.simulator.current_day}/{self.simulator.max_days}")
        self.cash_label.config(text=f"Cash: ${self.simulator.portfolio['cash']:.2f}")

        # Calculate and update net worth
        net_worth = self.simulator.update_net_worth()
        self.net_worth_label.config(text=f"Net Worth: ${net_worth:.2f}")

        self.update_stock_table()
        self.update_portfolio_display()
        self.update_news_feed()
        self.update_stock_price_chart()
        self.update_portfolio_chart()
        self.update_comparison_chart()
        self.update_sector_chart()

    def advance_day(self):
        if self.simulator.simulate_day():
            self.update_displays()
        else:
            self.show_final_results()

    def show_final_results(self):
        # Disable game buttons
        self.next_day_btn.config(state=tk.DISABLED)
        self.buy_btn.config(state=tk.DISABLED)
        self.sell_btn.config(state=tk.DISABLED)
        self.short_btn.config(state=tk.DISABLED)
        self.cover_btn.config(state=tk.DISABLED)

        # Show final evaluation in a new window
        eval_window = tk.Toplevel(self.root)
        eval_window.title("Game Over - Final Evaluation")
        eval_window.geometry("500x400")

        eval_text = scrolledtext.ScrolledText(eval_window, wrap=tk.WORD)
        eval_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        eval_text.insert(tk.END, self.simulator.get_final_evaluation())

    def buy_stock(self):
        symbol = self.stock_var.get()
        shares_str = self.shares_var.get()

        if not symbol or not shares_str:
            messagebox.showerror("Error", "Please select a stock and enter number of shares")
            return

        try:
            shares = int(shares_str)
            result = self.simulator.buy_stock(symbol, shares)
            if result.startswith("Bought"):
                messagebox.showinfo("Trade Executed", result)
                self.shares_var.set("")  # Clear shares entry
                self.update_displays()
            else:
                messagebox.showerror("Trade Failed", result)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shares")

    def sell_stock(self):
        symbol = self.stock_var.get()
        shares_str = self.shares_var.get()

        if not symbol or not shares_str:
            messagebox.showerror("Error", "Please select a stock and enter number of shares")
            return

        try:
            shares = int(shares_str)
            result = self.simulator.sell_stock(symbol, shares)
            if result.startswith("Sold"):
                messagebox.showinfo("Trade Executed", result)
                self.shares_var.set("")  # Clear shares entry
                self.update_displays()
            else:
                messagebox.showerror("Trade Failed", result)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shares")

    def short_stock(self):
        symbol = self.stock_var.get()
        shares_str = self.shares_var.get()

        if not symbol or not shares_str:
            messagebox.showerror("Error", "Please select a stock and enter number of shares")
            return

        try:
            shares = int(shares_str)
            result = self.simulator.short_sell(symbol, shares)
            if result.startswith("Short"):
                messagebox.showinfo("Trade Executed", result)
                self.shares_var.set("")  # Clear shares entry
                self.update_displays()
            else:
                messagebox.showerror("Trade Failed", result)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shares")

    def cover_stock(self):
        symbol = self.stock_var.get()
        shares_str = self.shares_var.get()

        if not symbol or not shares_str:
            messagebox.showerror("Error", "Please select a stock and enter number of shares")
            return

        try:
            shares = int(shares_str)
            result = self.simulator.cover_short(symbol, shares)
            if result.startswith("Covered"):
                messagebox.showinfo("Trade Executed", result)
                self.shares_var.set("")  # Clear shares entry
                self.update_displays()
            else:
                messagebox.showerror("Trade Failed", result)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shares")

    def setup_charts(self):
        # Stock price chart
        self.price_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.price_canvas = FigureCanvasTkAgg(self.price_fig, self.price_chart_frame)
        self.price_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar for zooming/panning
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.price_toolbar = NavigationToolbar2Tk(self.price_canvas, self.price_chart_frame)
        self.price_toolbar.update()

        # Portfolio value chart
        self.portfolio_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.portfolio_canvas = FigureCanvasTkAgg(self.portfolio_fig, self.portfolio_chart_frame)
        self.portfolio_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.portfolio_toolbar = NavigationToolbar2Tk(self.portfolio_canvas, self.portfolio_chart_frame)
        self.portfolio_toolbar.update()

        # Performance comparison chart
        self.comparison_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, self.comparison_chart_frame)
        self.comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add comparison controls
        comparison_controls = ttk.Frame(self.comparison_chart_frame)
        comparison_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(comparison_controls, text="Base Value:").pack(side=tk.LEFT, padx=5)
        self.comparison_base_var = tk.StringVar(value="First Day")
        ttk.Combobox(comparison_controls, textvariable=self.comparison_base_var,
                     values=["First Day", "100%"], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(comparison_controls, text="Update",
                   command=self.update_comparison_chart).pack(side=tk.LEFT, padx=5)

        # Sector performance chart
        self.sector_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.sector_canvas = FigureCanvasTkAgg(self.sector_fig, self.sector_chart_frame)
        self.sector_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add sector controls
        sector_controls = ttk.Frame(self.sector_chart_frame)
        sector_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(sector_controls, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        self.sector_chart_type_var = tk.StringVar(value="Line")
        ttk.Combobox(sector_controls, textvariable=self.sector_chart_type_var,
                     values=["Line", "Bar", "Pie"], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(sector_controls, text="Update",
                   command=self.update_sector_chart).pack(side=tk.LEFT, padx=5)

    def update_stock_price_chart(self):
        self.price_fig.clear()
        ax = self.price_fig.add_subplot(111)

        # Get selected time range
        time_range = self.time_range_var.get()
        days_to_show = None
        if time_range == "5 Days":
            days_to_show = 5
        elif time_range == "10 Days":
            days_to_show = 10
        elif time_range == "15 Days":
            days_to_show = 15

        # Get the selected stocks (or all if none selected)
        selected_items = self.stocks_tree.selection()
        if selected_items and not self.multi_stock_var.get():
            # Single stock view
            selected_symbols = [self.stocks_tree.item(selected_items[0], "values")[0]]
            selected_stocks = [stock for stock in self.simulator.stocks if stock.symbol in selected_symbols]
        else:
            # Multi-stock view - show top 5 or selected
            if selected_items:
                selected_symbols = [self.stocks_tree.item(item, "values")[0] for item in selected_items]
                selected_stocks = [stock for stock in self.simulator.stocks if stock.symbol in selected_symbols]
            else:
                selected_stocks = self.simulator.stocks[:5]

        chart_type = self.chart_type_var.get()

        for stock in selected_stocks:
            price_history = stock.price_history

            # Apply time range filter if needed
            if days_to_show and len(price_history) > days_to_show:
                price_history = price_history[-days_to_show:]
                days = list(range(len(price_history)))
                start_day = len(stock.price_history) - days_to_show
                days = [d + start_day for d in days]
            else:
                days = list(range(len(price_history)))

            # Draw based on chart type
            if chart_type == "Line":
                ax.plot(days, price_history, label=stock.symbol)

            elif chart_type == "Area":
                ax.fill_between(days, price_history, alpha=0.3, label=stock.symbol)
                ax.plot(days, price_history, alpha=0.6)

            elif chart_type == "Candlestick":
                # For demonstration, create simple OHLC data
                # In a real app, you'd track actual OHLC data
                if len(price_history) > 1:
                    from matplotlib.patches import Rectangle

                    width = 0.8
                    for i in range(1, len(price_history)):
                        open_price = price_history[i - 1]
                        close_price = price_history[i]

                        # Simulate high/low with some random variation
                        high = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
                        low = min(open_price, close_price) * (1 - random.uniform(0, 0.02))

                        # Draw candlestick
                        color = 'green' if close_price >= open_price else 'red'
                        rect = Rectangle((i - width / 2, min(open_price, close_price)),
                                         width, abs(close_price - open_price),
                                         facecolor=color, edgecolor='black', alpha=0.6)
                        ax.add_patch(rect)

                        # Draw wicks
                        ax.plot([i, i], [low, min(open_price, close_price)], color='black', linewidth=1)
                        ax.plot([i, i], [max(open_price, close_price), high], color='black', linewidth=1)

            # Add moving average if selected
            if self.show_ma_var.get() and len(price_history) > 5:
                window_size = 5  # 5-day moving average
                ma = [sum(price_history[max(0, i - window_size + 1):i + 1]) / min(i + 1, window_size)
                      for i in range(len(price_history))]
                ax.plot(days, ma, '--', alpha=0.7, label=f"{stock.symbol} MA-{window_size}")

        ax.set_title("Stock Price History")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price ($)")
        ax.legend(loc="upper left")
        ax.grid(True)

        # Add annotations for key events if in single stock view
        if len(selected_stocks) == 1 and not self.multi_stock_var.get():
            stock = selected_stocks[0]
            symbol = stock.symbol

            # Find news events for this stock
            for news in self.simulator.stock_news_events:
                if news["impact"]["stock"] == symbol:
                    # Find days when this news might have happened
                    for i in range(1, len(stock.price_history)):
                        # Look for large price changes that might correspond to news
                        change_pct = ((stock.price_history[i] - stock.price_history[i - 1]) /
                                      stock.price_history[i - 1]) * 100
                        if abs(change_pct) > 3:  # Significant change
                            ax.annotate('News Event', xy=(i, stock.price_history[i]),
                                        xytext=(i, stock.price_history[i] * 1.1),
                                        arrowprops=dict(facecolor='red', shrink=0.05),
                                        fontsize=8)
                            break

        self.price_canvas.draw()

    def update_portfolio_chart(self):
        self.portfolio_fig.clear()
        ax = self.portfolio_fig.add_subplot(111)

        days = list(range(len(self.simulator.net_worth_history)))

        # Plot net worth line
        ax.plot(days, self.simulator.net_worth_history, label="Total Value", color="green", linewidth=2)

        # Plot cash component as filled area
        cash_history = [self.simulator.starting_cash]  # Start with initial cash
        for trans in self.simulator.transaction_history:
            day = trans["day"]
            while len(cash_history) <= day:
                cash_history.append(cash_history[-1])  # Extend with previous value

            if trans["type"] == "BUY" or trans["type"] == "COVER":
                cash_history[day] -= trans["total"]
            elif trans["type"] == "SELL" or trans["type"] == "SHORT":
                cash_history[day] += trans["total"]

        # Extend cash history to match net worth history length
        while len(cash_history) < len(self.simulator.net_worth_history):
            cash_history.append(cash_history[-1])

        ax.fill_between(days, cash_history, alpha=0.3, color="blue", label="Cash Component")

        # Calculate and plot stock component as the difference
        stock_values = [n - c for n, c in zip(self.simulator.net_worth_history, cash_history)]
        ax.fill_between(days, cash_history, self.simulator.net_worth_history, alpha=0.3, color="orange",
                        label="Stock Value")

        ax.set_title("Portfolio Value History")
        ax.set_xlabel("Day")
        ax.set_ylabel("Value ($)")
        ax.axhline(y=self.simulator.starting_cash, color='r', linestyle='-', alpha=0.3, label="Starting Cash")
        ax.legend(loc="upper left")
        ax.grid(True)

        # Add markers for significant trades
        for trans in self.simulator.transaction_history:
            day = trans["day"]
            value = self.simulator.net_worth_history[day]

            marker = '^' if trans["type"] in ["BUY", "COVER"] else 'v'
            color = 'g' if trans["type"] in ["BUY", "SELL"] else 'r'

            ax.scatter(day, value, marker=marker, color=color, s=30, alpha=0.7)

        self.portfolio_canvas.draw()

    def update_comparison_chart(self):
        self.comparison_fig.clear()
        ax = self.comparison_fig.add_subplot(111)

        # Get selected stocks
        selected_items = self.stocks_tree.selection()
        if not selected_items:
            # If no selection, compare the first 3 stocks
            selected_stocks = self.simulator.stocks[:3]
        else:
            selected_symbols = [self.stocks_tree.item(item, "values")[0] for item in selected_items]
            selected_stocks = [stock for stock in self.simulator.stocks if stock.symbol in selected_symbols]

        # Determine base value for normalization
        base_type = self.comparison_base_var.get()

        for stock in selected_stocks:
            price_history = stock.price_history
            days = list(range(len(price_history)))

            if base_type == "First Day":
                # Normalize to first day value (percentage change)
                base_value = price_history[0]
                normalized_prices = [(p / base_value) * 100 for p in price_history]
                ax.plot(days, normalized_prices, label=f"{stock.symbol}")

                ax.set_ylabel("Percent of Initial Value (%)")
                ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)

            else:  # Raw prices
                ax.plot(days, price_history, label=f"{stock.symbol}")
                ax.set_ylabel("Price ($)")

        # Add portfolio performance if we have history
        if len(self.simulator.net_worth_history) > 1:
            days = list(range(len(self.simulator.net_worth_history)))
            if base_type == "First Day":
                base_value = self.simulator.net_worth_history[0]
                norm_net_worth = [(v / base_value) * 100 for v in self.simulator.net_worth_history]
                ax.plot(days, norm_net_worth, 'k--', label="Portfolio", linewidth=2)
            else:
                ax.plot(days, self.simulator.net_worth_history, 'k--', label="Portfolio", linewidth=2)

        ax.set_title("Performance Comparison")
        ax.set_xlabel("Day")
        ax.grid(True)
        ax.legend(loc="upper left")

        self.comparison_canvas.draw()

    def update_sector_chart(self):
        self.sector_fig.clear()

        # Group stocks by sector
        sector_data = {}
        for stock in self.simulator.stocks:
            if stock.sector not in sector_data:
                sector_data[stock.sector] = []
            sector_data[stock.sector].append(stock)

        chart_type = self.sector_chart_type_var.get()

        if chart_type == "Pie":
            # Pie chart of current sector allocation in portfolio
            ax = self.sector_fig.add_subplot(111)

            sector_values = {}
            total_value = 0

            # Calculate value by sector
            for symbol, shares in self.simulator.portfolio["stocks"].items():
                stock = self.simulator.stock_dict[symbol]
                value = stock.price * abs(shares)

                if stock.sector not in sector_values:
                    sector_values[stock.sector] = 0

                sector_values[stock.sector] += value
                total_value += value

            # Add cash to sector allocation
            sector_values["Cash"] = self.simulator.portfolio["cash"]
            total_value += self.simulator.portfolio["cash"]

            # Create pie chart
            labels = []
            sizes = []
            for sector, value in sector_values.items():
                labels.append(f"{sector}: ${value:.2f}")
                sizes.append(value)

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title("Portfolio Allocation by Sector")

        elif chart_type == "Bar":
            # Bar chart of sector performance
            ax = self.sector_fig.add_subplot(111)

            # Calculate average performance by sector
            sector_performance = {}
            for sector, stocks in sector_data.items():
                perf_sum = 0
                for stock in stocks:
                    if len(stock.price_history) > 1:
                        perf = ((stock.price_history[-1] / stock.price_history[0]) - 1) * 100
                        perf_sum += perf

                sector_performance[sector] = perf_sum / len(stocks)

            # Create bar chart
            sectors = list(sector_performance.keys())
            performances = list(sector_performance.values())

            bars = ax.bar(sectors, performances)

            # Color bars based on performance
            for i, perf in enumerate(performances):
                color = 'green' if perf >= 0 else 'red'
                bars[i].set_color(color)

            ax.set_xlabel('Sector')
            ax.set_ylabel('Average Performance (%)')
            ax.set_title('Sector Performance')
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Add performance values on top of bars
            for i, perf in enumerate(performances):
                ax.text(i, perf + (1 if perf >= 0 else -2),
                        f"{perf:.1f}%", ha='center')

        else:  # Line chart
            ax = self.sector_fig.add_subplot(111)

            # For each sector, calculate average daily price
            max_days = max([len(stock.price_history) for stock in self.simulator.stocks])
            days = list(range(max_days))

            for sector, stocks in sector_data.items():
                # Calculate average daily price for all stocks in this sector
                sector_daily_avg = []

                for day in range(max_days):
                    day_sum = 0
                    day_count = 0

                    for stock in stocks:
                        if day < len(stock.price_history):
                            # Get price relative to the first day
                            rel_price = stock.price_history[day] / stock.price_history[0] * 100
                            day_sum += rel_price
                            day_count += 1

                    if day_count > 0:
                        sector_daily_avg.append(day_sum / day_count)
                    else:
                        # If no data for this day, use previous day or 100
                        if sector_daily_avg:
                            sector_daily_avg.append(sector_daily_avg[-1])
                        else:
                            sector_daily_avg.append(100)

                ax.plot(days[:len(sector_daily_avg)], sector_daily_avg, label=sector)

            ax.set_title("Sector Performance Over Time")
            ax.set_xlabel("Day")
            ax.set_ylabel("Average Price (% of Initial)")
            ax.legend(loc="upper left")
            ax.grid(True)

        self.sector_canvas.draw()

    def export_chart(self):
        # Create a file dialog to save the chart
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Chart As"
        )

        if file_path:
            # Determine which chart to save based on current tab
            current_tab = self.chart_notebook.index(self.chart_notebook.select())

            if current_tab == 0:  # Stock prices tab
                self.price_fig.savefig(file_path, dpi=300, bbox_inches='tight')
            elif current_tab == 1:  # Portfolio tab
                self.portfolio_fig.savefig(file_path, dpi=300, bbox_inches='tight')
            elif current_tab == 2:  # Comparison tab
                self.comparison_fig.savefig(file_path, dpi=300, bbox_inches='tight')
            elif current_tab == 3:  # Sector performance tab
                self.sector_fig.savefig(file_path, dpi=300, bbox_inches='tight')

            messagebox.showinfo("Export Successful", f"Chart saved to {file_path}")


def main():
    root = tk.Tk()
    app = StockMarketGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
