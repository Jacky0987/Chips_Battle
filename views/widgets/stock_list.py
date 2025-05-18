import tkinter as tk
from tkinter import ttk


class StockList:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # Stock selection frame
        self.selection_frame = ttk.LabelFrame(self.frame, text="Stock Selection")
        self.selection_frame.pack(fill=tk.X, padx=5, pady=5)

        # Filter by sector
        self.sector_frame = ttk.Frame(self.selection_frame)
        self.sector_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(self.sector_frame, text="Filter by Sector:").pack(side=tk.LEFT, padx=5)
        self.sector_var = tk.StringVar(value="All")
        self.sector_combo = ttk.Combobox(self.sector_frame, textvariable=self.sector_var, width=15)
        self.sector_combo.pack(side=tk.LEFT, padx=5)

        # Search bar
        self.search_frame = ttk.Frame(self.selection_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(self.search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(self.search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.search_frame, text="Clear", command=self.clear_search).pack(side=tk.RIGHT, padx=5)

        # Stock table
        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("Symbol", "Name", "Price", "Change", "Change %", "Sector", "Dividend Yield")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="extended")

        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            width = 80 if col != "Name" else 150
            self.tree.column(col, width=width, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind("<Double-1>", self.on_stock_double_click)

        # Store callback function
        self.on_select_callback = lambda symbols: None

        # Set up variables for sort state
        self.sort_column = "Symbol"
        self.sort_reverse = False

    def set_on_select_callback(self, callback):
        self.on_select_callback = callback

    def set_sectors(self, sectors):
        self.sector_combo["values"] = ["All"] + sectors

    def clear_search(self):
        self.search_var.set("")
        self.update_stocks(self.stocks)

    def update_stocks(self, stocks):
        self.stocks = stocks

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter values
        search_text = self.search_var.get().lower()
        selected_sector = self.sector_var.get()

        # Filter stocks
        filtered_stocks = stocks
        if selected_sector != "All":
            filtered_stocks = [s for s in filtered_stocks if s.sector == selected_sector]
        if search_text:
            filtered_stocks = [s for s in filtered_stocks if
                               search_text in s.name.lower() or search_text in s.symbol.lower()]

        # Populate with stock data
        for stock in filtered_stocks:
            # Calculate price change and percentage
            if len(stock.price_history) >= 2:
                price_change = stock.price - stock.price_history[-2]
                change_pct = (price_change / stock.price_history[-2]) * 100 if stock.price_history[-2] > 0 else 0
            else:
                price_change = 0
                change_pct = 0

            # Format values
            formatted_price = f"${stock.price:.2f}"
            formatted_change = f"{price_change:+.2f}" if price_change != 0 else "0.00"
            formatted_pct = f"{change_pct:+.2f}%" if change_pct != 0 else "0.00%"
            dividend_yield = f"{stock.dividend_yield:.2f}%" if stock.pays_dividend else "N/A"

            # Insert into table
            item_id = self.tree.insert("", tk.END, values=(stock.symbol, stock.name, formatted_price,
                                                           formatted_change, formatted_pct, stock.sector,
                                                           dividend_yield))

            # Color red/green based on change
            if price_change > 0:
                self.tree.item(item_id, tags=("gain",))
            elif price_change < 0:
                self.tree.item(item_id, tags=("loss",))

        # Configure tag colors
        self.tree.tag_configure("gain", foreground="green")
        self.tree.tag_configure("loss", foreground="red")

        # Sort by the current sort column
        self.sort_by_column(self.sort_column, override=True)

    def on_stock_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            selected_symbols = [self.tree.item(item)["values"][0] for item in selection]
            self.on_select_callback(selected_symbols)

    def get_selected_symbols(self):
        selection = self.tree.selection()
        if selection:
            return [self.tree.item(item)["values"][0] for item in selection]
        return []

    def sort_by_column(self, column, override=False):
        if self.sort_column != column or override:
            self.sort_column = column
            self.sort_reverse = False
        else:
            self.sort_reverse = not self.sort_reverse

        # Get all items
        item_list = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]

        # Sort based on column type
        if column in ["Symbol", "Name", "Sector"]:
            item_list.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        elif column == "Price":
            item_list.sort(key=lambda x: float(x[0].replace("$", "")), reverse=self.sort_reverse)
        elif column in ["Change", "Change %"]:
            item_list.sort(key=lambda x: float(x[0].replace("+", "").replace("%", "")), reverse=self.sort_reverse)

        # Rearrange items
        for idx, (_, item) in enumerate(item_list):
            self.tree.move(item, "", idx)

    def get_frame(self):
        return self.frame
