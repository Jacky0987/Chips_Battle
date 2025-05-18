import tkinter as tk
from tkinter import ttk, messagebox


class TradingPanel:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Stock info section
        self.info_frame = ttk.LabelFrame(self.frame, text="Stock Info")
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.stock_var = tk.StringVar()
        self.stock_name_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.sector_var = tk.StringVar()

        # Create grid for stock info
        info_grid = ttk.Frame(self.info_frame)
        info_grid.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(info_grid, text="Symbol:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(info_grid, textvariable=self.stock_var, font=("", 10, "bold")).grid(row=0, column=1, sticky="w",
                                                                                      padx=5)

        ttk.Label(info_grid, text="Name:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(info_grid, textvariable=self.stock_name_var).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(info_grid, text="Price:").grid(row=2, column=0, sticky="w", padx=5)
        ttk.Label(info_grid, textvariable=self.price_var).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(info_grid, text="Sector:").grid(row=3, column=0, sticky="w", padx=5)
        ttk.Label(info_grid, textvariable=self.sector_var).grid(row=3, column=1, sticky="w", padx=5)

        # Trading actions section
        self.trade_frame = ttk.LabelFrame(self.frame, text="Trade")
        self.trade_frame.pack(fill=tk.X, padx=5, pady=5)

        # Trade type selection
        trade_type_frame = ttk.Frame(self.trade_frame)
        trade_type_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(trade_type_frame, text="Position:").pack(side=tk.LEFT, padx=5)
        self.position_var = tk.StringVar(value="LONG")
        ttk.Radiobutton(trade_type_frame, text="Long", variable=self.position_var, value="LONG").pack(side=tk.LEFT,
                                                                                                      padx=5)
        ttk.Radiobutton(trade_type_frame, text="Short", variable=self.position_var, value="SHORT").pack(side=tk.LEFT,
                                                                                                        padx=5)

        # Shares entry and buttons
        shares_frame = ttk.Frame(self.trade_frame)
        shares_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(shares_frame, text="Shares:").pack(side=tk.LEFT, padx=5)
        self.shares_var = tk.StringVar(value="0")
        self.shares_entry = ttk.Entry(shares_frame, textvariable=self.shares_var, width=10)
        self.shares_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(shares_frame, text="+10", command=lambda: self.adjust_shares(10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(shares_frame, text="+50", command=lambda: self.adjust_shares(50)).pack(side=tk.LEFT, padx=2)
        ttk.Button(shares_frame, text="+100", command=lambda: self.adjust_shares(100)).pack(side=tk.LEFT, padx=2)
        ttk.Button(shares_frame, text="Max", command=self.max_shares).pack(side=tk.LEFT, padx=2)

        # Trade button
        trade_button_frame = ttk.Frame(self.trade_frame)
        trade_button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.total_cost_var = tk.StringVar(value="$0.00")
        ttk.Label(trade_button_frame, text="Total:").pack(side=tk.LEFT, padx=5)
        ttk.Label(trade_button_frame, textvariable=self.total_cost_var).pack(side=tk.LEFT, padx=5)

        self.buy_button = ttk.Button(trade_button_frame, text="Buy", command=self.buy)
        self.buy_button.pack(side=tk.RIGHT, padx=5)

        self.sell_button = ttk.Button(trade_button_frame, text="Sell", command=self.sell)
        self.sell_button.pack(side=tk.RIGHT, padx=5)

        # Disable buttons initially
        self.enable_trading(False)

        # Store references
        self.current_stock = None
        self.current_price = 0
        self.market = None

        # Bind events
        self.shares_var.trace("w", self.update_total_cost)
        self.position_var.trace("w", self.update_button_text)
        
        # 添加交易完成后的回调函数
        self.trade_callback = lambda: None

    def set_market(self, market):
        self.market = market

    def enable_trading(self, enable=True):
        state = "normal" if enable else "disabled"
        self.shares_entry.config(state=state)
        self.buy_button.config(state=state)
        self.sell_button.config(state=state)

    def select_stock(self, stock):
        self.current_stock = stock
        self.current_price = stock.price

        # Update display
        self.stock_var.set(stock.symbol)
        self.stock_name_var.set(stock.name)
        self.price_var.set(f"${stock.price:.2f}")
        self.sector_var.set(stock.sector)

        # Enable trading
        self.enable_trading(True)
        self.shares_var.set("0")
        self.update_button_text()
        
    # 添加一个新方法来更新当前股票价格
    def update_current_stock_price(self):
        """更新当前选中股票的价格"""
        if self.current_stock:
            self.current_price = self.current_stock.price
            self.price_var.set(f"${self.current_stock.price:.2f}")
            self.update_total_cost()

    def adjust_shares(self, amount):
        try:
            current = int(self.shares_var.get() or "0")
            self.shares_var.set(str(current + amount))
        except ValueError:
            self.shares_var.set(str(amount))

    def max_shares(self):
        if self.current_stock and self.market:
            if self.position_var.get() == "LONG":
                max_shares = int(self.market.portfolio.cash / self.current_price)
            else:
                # For short selling, use a margin requirement of 150% (simplified)
                max_shares = int(self.market.portfolio.cash / (self.current_price * 1.5))

            self.shares_var.set(str(max_shares))

    def update_total_cost(self, *args):
        try:
            shares = int(self.shares_var.get() or "0")
            total = shares * self.current_price
            self.total_cost_var.set(f"${total:.2f}")
        except ValueError:
            self.total_cost_var.set("$0.00")

    def update_button_text(self, *args):
        position = self.position_var.get()
        if position == "LONG":
            self.buy_button.config(text="Buy")
            self.sell_button.config(text="Sell")
        else:
            self.buy_button.config(text="Short")
            self.sell_button.config(text="Cover")
    
    def set_trade_callback(self, callback):
        """设置交易完成后的回调函数"""
        self.trade_callback = callback

    def buy(self):
        if not self.current_stock or not self.market:
            return

        try:
            shares = int(self.shares_var.get())
            if shares <= 0:
                messagebox.showwarning("Invalid Shares", "Please enter a positive number of shares.")
                return

            position = self.position_var.get()
            print(f"[DEBUG] 尝试交易: 类型={'买入' if position == 'LONG' else '做空'}, 股票={self.current_stock.symbol}, 数量={shares}, 价格=${self.current_price:.2f}")

            if position == "LONG":
                result = self.market.portfolio.buy_stock(
                    self.current_stock.symbol,
                    shares,
                    self.current_price,
                    self.market.current_day
                )
            else:
                result = self.market.portfolio.short_sell(
                    self.current_stock.symbol,
                    shares,
                    self.current_price,
                    self.market.current_day
                )

            print(f"[DEBUG] 交易结果: {result}")
            messagebox.showinfo("Trade Result", result)
            
            # 在交易完成后调用回调函数
            self.trade_callback()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of shares.")

    def sell(self):
        if not self.current_stock or not self.market:
            return

        try:
            shares = int(self.shares_var.get())
            if shares <= 0:
                messagebox.showwarning("Invalid Shares", "Please enter a positive number of shares.")
                return

            position = self.position_var.get()
            print(f"[DEBUG] 尝试交易: 类型={'卖出' if position == 'LONG' else '回补'}, 股票={self.current_stock.symbol}, 数量={shares}, 价格=${self.current_price:.2f}")

            if position == "LONG":
                result = self.market.portfolio.sell_stock(
                    self.current_stock.symbol,
                    shares,
                    self.current_price,
                    self.market.current_day
                )
            else:
                result = self.market.portfolio.cover_short(
                    self.current_stock.symbol,
                    shares,
                    self.current_price,
                    self.market.current_day
                )

            print(f"[DEBUG] 交易结果: {result}")
            messagebox.showinfo("Trade Result", result)
            
            # 在交易完成后调用回调函数
            self.trade_callback()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of shares.")

    def get_frame(self):
        return self.frame
