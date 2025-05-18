import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class ComparisonChart:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Chart controls
        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.controls_frame, text="Base Value:").pack(side=tk.LEFT, padx=5)
        self.base_var = tk.StringVar(value="First Day")
        ttk.Combobox(self.controls_frame, textvariable=self.base_var,
                     values=["First Day", "100%"], width=10).pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(self.controls_frame, text="Update")
        self.update_button.pack(side=tk.LEFT, padx=5)

        # Create chart
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def set_update_callback(self, callback):
        self.update_button.config(command=callback)

    def update(self, stocks, selected_symbols, portfolio_history):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Determine base value for normalization
        base_type = self.base_var.get()

        # Filter selected stocks
        if selected_symbols:
            selected_stocks = [stock for stock in stocks if stock.symbol in selected_symbols]
        else:
            selected_stocks = stocks[:3]  # Default to first 3 stocks

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
        if portfolio_history and len(portfolio_history) > 1:
            days = list(range(len(portfolio_history)))
            if base_type == "First Day":
                base_value = portfolio_history[0]
                norm_net_worth = [(v / base_value) * 100 for v in portfolio_history]
                ax.plot(days, norm_net_worth, 'k--', label="Portfolio", linewidth=2)
            else:
                ax.plot(days, portfolio_history, 'k--', label="Portfolio", linewidth=2)

        ax.set_title("Performance Comparison")
        ax.set_xlabel("Day")
        ax.grid(True)
        ax.legend(loc="upper left")

        self.canvas.draw()

    def get_frame(self):
        return self.frame
