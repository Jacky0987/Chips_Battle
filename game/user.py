# This file contains the User class which represents a user in the game.

from datetime import datetime

class User:
    def __init__(self, name, password, cash, permission):
        self.name = name
        self.password = password
        self.cash = cash
        self.permission = permission
        self.stocks = {}  # Stock holdings dictionary
        self.lottery_tickets = []  # List of lottery tickets
        self.trades = []  # List of trades made by the user

    # 修饰器函数，用于检查用户权限

    def buy_market_price_stock(self, stock, quantity):
        if self.cash >= stock.get_current_price() * quantity:
            self.cash -= stock.get_current_price() * quantity
            if stock.code not in self.stocks:
                self.stocks[stock.code] = 0
            self.stocks[stock.code] += quantity
            stock.purchasable_shares -= quantity
            stock.trading_volume += quantity * stock.get_current_price()
            trade = (datetime.now(), 'BUY', stock.code, quantity, stock.get_current_price())
            self.trades.append(trade)
            print(f"Bought {quantity} shares of {stock.name} at market price for J$ {stock.get_current_price() * quantity:,.2f}.")
        else:
            print("Insufficient funds to complete the purchase.")

    def sell_market_price_stock(self, stock, quantity):
        if stock.code in self.stocks and self.stocks[stock.code] >= quantity:
            self.cash += stock.get_current_price() * quantity
            self.stocks[stock.code] -= quantity
            stock.purchasable_shares += quantity
            stock.trading_volume += quantity * stock.get_current_price()
            trade = (datetime.now(), 'SELL', stock.code, quantity, stock.get_current_price())
            self.trades.append(trade)
            print(f"Sold {quantity} shares of {stock.name} at market price for J${stock.get_current_price():,.2f}.")
            print(f"You earned J$ {stock.get_current_price() * quantity:,.2f}. from the selling.")
            print(f"You now have J$ {self.cash:,.2f}.")
        else:
            print("Insufficient shares to sell.")

    def view_holdings(self):
        print("Your current stock holdings:")
        for code, quantity in self.stocks.items():
            print(f"{code}: {quantity} shares")
        print(f"You have J$ {self.cash:,.2f}.")

    def show_history(self):
        print("Your trade history:")
        for trade in self.trades:
            trade_time, action, code, quantity, price = trade
            print(f"{trade_time} - {action} {quantity} shares of code {code} at {price}")

    def get_current_cash(self):
        return self.cash

    def add_cash(self, amount):
        self.cash += amount

    def deduce_cash(self, amount):
        if self.cash >= amount:
            self.cash -= amount
