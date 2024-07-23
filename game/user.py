import json
from datetime import datetime


class User:
    def __init__(self, name , cash, permission):
        self.name = name
        self.cash = cash
        self.permission = 0
        self.stocks = {}  # Stock holdings dictionary
        self.trades = []  # List of trades made by the user

    def buy_market_price_stock(self, stock, quantity):
        # Check if the stock object is valid
        if stock is None:
            print("Error: Stock not found.")
            return

        # Ensure quantity is a numeric value and positive
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            print("Error: Quantity must be a positive number.")
            return

        # Convert float quantity to integer if necessary
        if isinstance(quantity, float):
            print("Warning: Quantity should be an integer, converting quantity to integer.")
            quantity = int(quantity)

        # Check if the stock is available for purchase
        if stock.purchasable_shares <= 0:
            print(f"Error: No shares of {stock.name} are available for purchase at this time.")
            return

        # Check if sufficient shares are available to purchase
        if quantity > stock.purchasable_shares:
            print(f"Error: Only {stock.purchasable_shares} shares available, cannot purchase {quantity}.")
            return

        # Check if the user has enough cash to purchase the desired quantity of stock
        total_cost = stock.get_current_price() * quantity
        if self.cash < total_cost:
            print(
                f"Insufficient funds to complete the purchase. You need J$ {total_cost:,.2f}, but you have J$ {self.cash:,.2f}.")
            return

        # Proceed with the purchase
        self.cash -= total_cost
        if stock.code not in self.stocks:
            self.stocks[stock.code] = 0
        self.stocks[stock.code] += quantity
        stock.purchasable_shares -= quantity
        stock.trading_volume += quantity * stock.get_current_price()
        trade = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'BUY', stock.code, quantity, stock.get_current_price())
        self.trades.append(trade)
        print(f"Bought {quantity} shares of {stock.name} at market price for J$ {total_cost:,.2f}.")

    def sell_market_price_stock(self, stock, quantity):
        if stock.code in self.stocks and self.stocks[stock.code] >= quantity:
            self.cash += stock.get_current_price() * quantity
            self.stocks[stock.code] -= quantity
            stock.purchasable_shares += quantity
            stock.trading_volume += quantity * stock.get_current_price()
            trade = (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'SELL', stock.code, quantity, stock.get_current_price())
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

    def to_dict(self):
        return {
            "name": self.name,
            "cash": self.cash,
            "permission": self.permission,
            "stocks": self.stocks,
            "trades": [
                [trade_time, action, code, quantity, price]
                for trade_time, action, code, quantity, price in self.trades
            ]
        }

    def save_userdata(self, filename):
        # Save user data to a file using JSON
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f)
        print(f"User data saved to {filename}.")

    def load_userdata_from_name(self, filename, name):
        try:
            # 尝试加载文件
            with open(filename, "r") as f:
                data = json.load(f)
            if data["name"] == name:
                self.name = data["name"]
                self.cash = data["cash"]
                self.permission = data["permission"]
                self.stocks = data["stocks"]
                self.trades = [
                    (trade_time, action, code, quantity, price)
                    for trade_time, action, code, quantity, price in data["trades"]
                ]
                print(f"User data loaded from {filename}.")
                return self
            else:
                print(f"User data not found for {name}.")
                return
        except FileNotFoundError:
            # 如果文件未找到，创建默认用户数据并保存
            default_data = {
                "name": name,
                "cash": 0,  # 您可以根据需要设置默认现金值
                "permission": 0,  # 您可以根据需要设置默认权限值
                "stocks": {},
                "trades": []
            }
            with open(filename, "w") as f:
                json.dump(default_data, f)
            print(f"Created default user data file {filename}.")
            return self


    def get_current_cash(self):
        return self.cash

    def add_cash(self, amount):
        if self.permission == 1:
            self.cash += amount
            print(f"Added J$ {amount:,.2f} to your account.")
        else:
            print("You do not have permission to add cash.")

    def deduce_cash(self, amount):
        if self.permission == 1:
            if self.cash >= amount:
                self.cash -= amount
                print(f"Deduced J$ {amount:,.2f} to your account.")
            else:
                print("Insufficient funds.")
        else:
            print("You do not have permission to deduct cash.")

    def get_admin(self):
        if self.permission == 1:
            print("You are an admin.")
            return False
        else:
            pwd = input("Enter password to get admin privileges: ")
            if pwd == "admin":
                self.permission = 1
                print("You are now an admin.")
                return True
            else:
                print("You are not an admin.")
                return False