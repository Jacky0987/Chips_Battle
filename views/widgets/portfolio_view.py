import tkinter as tk
from tkinter import ttk


class PortfolioView:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Create portfolio summary section
        self.summary_frame = ttk.LabelFrame(self.frame, text="Portfolio Summary")
        self.summary_frame.pack(fill=tk.X, padx=5, pady=5)

        self.summary_text = tk.Text(self.summary_frame, height=8, width=40)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.summary_text.config(state=tk.DISABLED)

        # Create holdings table
        self.holdings_frame = ttk.LabelFrame(self.frame, text="Holdings")
        self.holdings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("Symbol", "Type", "Shares", "Price", "Value", "Gain/Loss", "%")
        self.tree = ttk.Treeview(self.holdings_frame, columns=columns, show="headings", selectmode="browse")

        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80
            self.tree.column(col, width=width, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.holdings_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind("<Double-1>", self.on_holding_double_click)

        # Store callback function
        self.on_select_callback = lambda symbol: None

    def set_on_select_callback(self, callback):
        self.on_select_callback = callback

    def update(self, portfolio, stocks):
        # Create lookup from symbol to stock
        stock_dict = {stock.symbol: stock for stock in stocks}
        print(f"[DEBUG] 更新投资组合视图: 现金=${portfolio.cash:.2f}, 持股数量={len(portfolio.stocks)}")

        # Update summary text
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)

        total_value = portfolio.cash
        for symbol, shares in portfolio.stocks.items():
            if symbol in stock_dict:
                stock = stock_dict[symbol]
                total_value += stock.price * shares

        self.summary_text.insert(tk.END, f"Cash: ${portfolio.cash:.2f}\n")
        self.summary_text.insert(tk.END, f"Stocks: ${total_value - portfolio.cash:.2f}\n")
        self.summary_text.insert(tk.END, f"Total Value: ${total_value:.2f}\n\n")

        profit_loss = total_value - portfolio.starting_cash
        profit_loss_percent = (profit_loss / portfolio.starting_cash) * 100

        if profit_loss >= 0:
            self.summary_text.insert(tk.END, f"Profit: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)\n")
        else:
            self.summary_text.insert(tk.END, f"Loss: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)\n")

        self.summary_text.config(state=tk.DISABLED)

        # Update holdings table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Check if portfolio has any stocks
        if not portfolio.stocks:
            # Add a message row when portfolio is empty
            self.tree.insert("", tk.END, values=("No holdings", "", "", "", "", "", ""))
            return

        for symbol, shares in portfolio.stocks.items():
            if symbol in stock_dict:
                stock = stock_dict[symbol]
                position_type = "LONG" if shares > 0 else "SHORT"
                shares_display = abs(shares)
                value = stock.price * shares_display

                # Calculate gain/loss (simplified - in a real app we'd track cost basis)
                # For demonstration only
                if len(stock.price_history) > 5:
                    prev_price = stock.price_history[-5]
                    gain_loss = (stock.price - prev_price) * shares_display
                    gain_loss_pct = (stock.price - prev_price) / prev_price * 100 if prev_price > 0 else 0
                    gain_loss_pct = gain_loss_pct if shares > 0 else -gain_loss_pct
                else:
                    gain_loss = 0
                    gain_loss_pct = 0

                formatted_price = f"${stock.price:.2f}"
                formatted_value = f"${value:.2f}"
                formatted_gain_loss = f"${gain_loss:+.2f}" if gain_loss != 0 else "$0.00"
                formatted_pct = f"{gain_loss_pct:+.2f}%" if gain_loss_pct != 0 else "0.00%"

                item_id = self.tree.insert("", tk.END, values=(symbol, position_type, shares_display,
                                                               formatted_price, formatted_value,
                                                               formatted_gain_loss, formatted_pct))

                # Color based on gain/loss
                if gain_loss > 0:
                    self.tree.item(item_id, tags=("gain",))
                elif gain_loss < 0:
                    self.tree.item(item_id, tags=("loss",))

        # Configure tag colors
        self.tree.tag_configure("gain", foreground="green")
        self.tree.tag_configure("loss", foreground="red")

    def on_holding_double_click(self, event):
        item = self.tree.selection()[0]
        symbol = self.tree.item(item)["values"][0]
        self.on_select_callback(symbol)

    def get_frame(self):
        return self.frame
