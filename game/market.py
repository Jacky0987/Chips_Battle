class Market:
    def __init__(self):
        self.stocks = []
        self.world_environment = 50  # Default to neutral environment

    def add_stock(self, stock):
        if stock not in self.stocks:
            self.stocks.append(stock)
            print(f"Stock {stock.name} (Code: {stock.code}) has been added to the market.")
        else:
            print("This stock is already in the market.")

    def remove_stock(self, stock):
        if stock in self.stocks:
            self.stocks.remove(stock)
            print(f"Stock {stock.name} (Code: {stock.code}) has been removed from the market.")
        else:
            print("This stock is not in the market.")

    def update_all_stocks(self):
        for stock in self.stocks:
            stock.update_rw_price(self.world_environment)

    def print_all_stocks(self):
        print("========================================================")
        print(f"World Environment: {self.world_environment}")
        for stock in self.stocks:
            print("========================================================")
            print(f"{stock.name} (Code: {stock.code})")
            print(f"Current Market Capitalization: J$ {stock.current_price*stock.initial_issued_shares:.2f}")
            print(f"Initial Price: J$ {stock.initial_price:,.2f}")
            print(f"Current Price: J$ {stock.current_price:,.2f}")
            print(f"Changing Rate: {(stock.current_price - stock.initial_price)/stock.initial_price*100:.2f}%")
            print(f"Trading Volume: J$ {stock.trading_volume:,.2f}")
            print(f"Initial Issued Shares: {stock.initial_issued_shares:,}")
            print(f"Purchasable Shares: {stock.purchasable_shares:,}")
            print("========================================================")