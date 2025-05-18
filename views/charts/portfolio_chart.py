import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class PortfolioChart:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Create chart
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()

    def update(self, portfolio, portfolio_history):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        days = list(range(len(portfolio_history)))

        # Plot net worth line
        ax.plot(days, portfolio_history, label="Total Value", color="green", linewidth=2)

        # Plot starting cash horizontal line
        ax.axhline(y=portfolio.starting_cash, color='r', linestyle='-', alpha=0.3, label="Starting Cash")

        # Add markers for transactions if available
        for trans in portfolio.transaction_history:
            day = trans["day"]
            if day < len(portfolio_history):
                value = portfolio_history[day]

                marker = '^' if trans["type"] in ["BUY", "COVER"] else 'v'
                color = 'g' if trans["type"] in ["BUY", "SELL"] else 'r'

                ax.scatter(day, value, marker=marker, color=color, s=30, alpha=0.7)

        ax.set_title("Portfolio Value History")
        ax.set_xlabel("Day")
        ax.set_ylabel("Value ($)")
        ax.legend(loc="upper left")
        ax.grid(True)

        self.canvas.draw()

    def get_frame(self):
        return self.frame
