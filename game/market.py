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
        for stock in self.stocks:
            print(stock.code)
            print(stock.name)
            print(f"Current Price: J$ {stock.current_price:,.2f}")