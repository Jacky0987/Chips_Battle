
class Market:
    def __init__(self):
        self.stocks = []

    def add_stock(self, stocks):
        if stocks not in self.stocks:
            self.stocks.append(stocks)
            print(f"Stock {stocks.name} (Code: {stocks.code}) has been added to the market.")
        else:
            print("This stock is already in the market.")

    def remove_stock(self, stock):
        if stock in self.stocks:
            self.stocks.remove(stock)
            print(f"Stock {stock.name} (Code: {stock.code}) has been removed from the market.")
        else:
            print("This stock is not in the market.")

    def update_all_stocks(self):
        for stocks in self.stocks:
            stocks.update_rw_price()

    def print_all_stocks(self):
        for stocks in self.stocks:
            print(stocks)
