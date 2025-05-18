import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SectorChart:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Chart controls
        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.controls_frame, text="Chart Type:").pack(side=tk.LEFT, padx=5)
        self.chart_type_var = tk.StringVar(value="Line")
        ttk.Combobox(self.controls_frame, textvariable=self.chart_type_var,
                     values=["Line", "Bar", "Pie"], width=10).pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(self.controls_frame, text="Update")
        self.update_button.pack(side=tk.LEFT, padx=5)

        # Create chart
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def set_update_callback(self, callback):
        self.update_button.config(command=callback)

    def update(self, stocks, sectors, portfolio):
        self.fig.clear()
        chart_type = self.chart_type_var.get()

        # Group stocks by sector
        sector_data = {}
        for sector in sectors:
            sector_data[sector] = []

        for stock in stocks:
            if stock.sector in sector_data:
                sector_data[stock.sector].append(stock)

        if chart_type == "Line":
            ax = self.fig.add_subplot(111)

            # Calculate average performance for each sector
            for sector, sector_stocks in sector_data.items():
                if not sector_stocks:
                    continue

                # Calculate average daily price change percentage
                avg_performance = []
                for day in range(max(len(stock.price_history) for stock in sector_stocks)):
                    day_sum = 0
                    day_count = 0
                    for stock in sector_stocks:
                        if day < len(stock.price_history) - 1:
                            if stock.price_history[day] > 0:  # Avoid division by zero
                                perf = (stock.price_history[day + 1] - stock.price_history[day]) / stock.price_history[
                                    day] * 100
                                day_sum += perf
                                day_count += 1

                    if day_count > 0:
                        avg_performance.append(day_sum / day_count)
                    else:
                        avg_performance.append(0)

                days = list(range(len(avg_performance)))
                ax.plot(days, avg_performance, label=sector)

            ax.set_title("Sector Performance")
            ax.set_xlabel("Day")
            ax.set_ylabel("Avg Daily Change (%)")
            ax.legend(loc="upper left")
            ax.grid(True)

        elif chart_type == "Bar":
            ax = self.fig.add_subplot(111)

            # Calculate total growth for each sector
            sector_growth = {}
            for sector, sector_stocks in sector_data.items():
                if not sector_stocks:
                    sector_growth[sector] = 0
                    continue

                total_start = sum(stock.price_history[0] for stock in sector_stocks)
                total_end = sum(stock.price_history[-1] for stock in sector_stocks)

                if total_start > 0:
                    growth = ((total_end - total_start) / total_start) * 100
                    sector_growth[sector] = growth
                else:
                    sector_growth[sector] = 0

            sectors = list(sector_growth.keys())
            growth_values = list(sector_growth.values())

            bars = ax.bar(sectors, growth_values)

            # Color bars based on growth (green for positive, red for negative)
            for i, bar in enumerate(bars):
                if growth_values[i] >= 0:
                    bar.set_color('green')
                else:
                    bar.set_color('red')

            ax.set_title("Sector Total Growth")
            ax.set_ylabel("Growth (%)")
            ax.grid(True, axis='y')

            # Add value labels on top of bars
            for i, v in enumerate(growth_values):
                ax.text(i, v + (1 if v >= 0 else -3), f"{v:.1f}%", ha='center')

        elif chart_type == "Pie":
            ax = self.fig.add_subplot(111)

            # Calculate current portfolio allocation by sector
            sector_values = {sector: 0 for sector in sectors}
            total_value = 0

            for symbol, shares in portfolio.stocks.items():
                for stock in stocks:
                    if stock.symbol == symbol:
                        value = stock.price * shares
                        sector_values[stock.sector] += value
                        total_value += value
                        break

            # Add cash to total
            sector_values["Cash"] = portfolio.cash
            total_value += portfolio.cash

            # Filter out zero values
            non_zero_sectors = {k: v for k, v in sector_values.items() if v > 0}

            if total_value > 0:
                labels = []
                sizes = []
                for sector, value in non_zero_sectors.items():
                    labels.append(f"{sector} (${value:.2f})")
                    sizes.append(value)

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                ax.set_title("Portfolio Allocation by Sector")
            else:
                ax.text(0.5, 0.5, "No portfolio data", ha='center', va='center')

        self.canvas.draw()

    def get_frame(self):
        return self.frame
