import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random
from matplotlib.patches import Rectangle


class PriceChart:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Initialize update_callback before create_controls uses it
        self.update_callback = lambda: None

        # Chart controls
        self.create_controls()

        # Create chart
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()

    def create_controls(self):
        # Chart control panel
        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)

        # Chart type selection
        ttk.Label(self.controls_frame, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        self.chart_type_var = tk.StringVar(value="Line")
        chart_type_combo = ttk.Combobox(self.controls_frame, textvariable=self.chart_type_var,
                                        values=["Line", "Candlestick", "Area"], width=12)
        chart_type_combo.pack(side=tk.LEFT, padx=5)
        chart_type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_callback())

        # Time range selection
        ttk.Label(self.controls_frame, text="Time Range:").pack(side=tk.LEFT, padx=5)
        self.time_range_var = tk.StringVar(value="All")
        time_range_combo = ttk.Combobox(self.controls_frame, textvariable=self.time_range_var,
                                        values=["All", "5 Days", "10 Days", "15 Days"], width=10)
        time_range_combo.pack(side=tk.LEFT, padx=5)
        time_range_combo.bind("<<ComboboxSelected>>", lambda e: self.update_callback())

        # Technical indicators
        ttk.Label(self.controls_frame, text="Indicators:").pack(side=tk.LEFT, padx=5)
        self.show_ma_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.controls_frame, text="Moving Avg", variable=self.show_ma_var,
                        command=self.update_callback).pack(side=tk.LEFT)
    
        # Add more technical indicators
        self.show_rsi_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.controls_frame, text="RSI", variable=self.show_rsi_var,
                        command=self.update_callback).pack(side=tk.LEFT)
                        
        self.show_macd_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.controls_frame, text="MACD", variable=self.show_macd_var,
                        command=self.update_callback).pack(side=tk.LEFT)

        # Button to toggle between single/multi stock view
        self.multi_stock_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.controls_frame, text="Multi-Stock View", variable=self.multi_stock_var,
                        command=self.update_callback).pack(side=tk.LEFT, padx=10)

        # Export button
        ttk.Button(self.controls_frame, text="Export Chart", command=self.export_chart).pack(side=tk.RIGHT, padx=5)

    def set_update_callback(self, callback):
        self.update_callback = callback


    def update(self, stocks, selected_symbols=None):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Get selected time range
        time_range = self.time_range_var.get()
        days_to_show = None
        if time_range == "5 Days":
            days_to_show = 5
        elif time_range == "10 Days":
            days_to_show = 10
        elif time_range == "15 Days":
            days_to_show = 15

        # Get the selected stocks
        if selected_symbols and not self.multi_stock_var.get():
            # Single stock view - just use the first selected stock
            selected_stocks = [stock for stock in stocks if stock.symbol == selected_symbols[0]]
        else:
            # Multi-stock view - show all selected or top 5
            if selected_symbols:
                selected_stocks = [stock for stock in stocks if stock.symbol in selected_symbols]
            else:
                selected_stocks = stocks[:5]

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
            # We would add annotations here for news events if available
            pass

        self.canvas.draw()

    def get_frame(self):
        return self.frame

    def export_chart(self):
        # Create a file dialog to save the chart
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Chart As"
        )

        if file_path:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
