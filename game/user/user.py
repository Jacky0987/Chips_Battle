# This file contains the User class which is used to represent a user in the game.
# Also defines the basic methods of the User class.

class User:
    def __init__(self, name, cash, permission):
        # User's identity and financial status
        self.name = name
        self.cash = cash
        self.permission = permission
        # Additional properties relevant to the game
        self.stocks = {}
        self.lottery_tickets = []
        self.trades = []
        self.inventory = {}

    def buy_stock(self, stock_name, quantity, current_price):
        if self.permission >= 0:
            total_cost = current_price * quantity
            if self.cash >= total_cost:
                if stock_name not in self.stocks:
                    self.stocks[stock_name] = 0
                self.stocks[stock_name] += quantity
                self.cash -= total_cost
                # self.trades.append(f"Bought {quantity} of {stock_name} at {current_price} each.")
            else:
                print("Insufficient funds to complete this purchase.")
        else:
            print("Permission denied. This user does not have the rights to buy stocks.")

    def sell_stock(self, stock_name, quantity, current_price):
        if self.permission >= 0:
            if stock_name in self.stocks and self.stocks[stock_name] >= quantity:
                self.stocks[stock_name] -= quantity
                if self.stocks[stock_name] == 0:
                    del self.stocks[stock_name]
                total_revenue = current_price * quantity
                self.cash += total_revenue
                self.trades.append(f"Sold {quantity} of {stock_name} at {current_price} each.")
            else:
                print(f"You do not have enough of {stock_name} to sell.")
        else:
            print("Permission denied. This user does not have the rights to sell stocks.")
