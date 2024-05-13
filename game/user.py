from datetime import datetime
from functools import wraps


class User:
    def __init__(self, name, cash, permission):
        # User's identity and financial status
        # Single value attributes.
        self.name = name
        self.cash = cash
        self.permission = permission

        # Additional properties relevant to the game
        # Multi-value attributes.
        self.stocks = {}  # Stock holdings dictionary
        self.lottery_tickets = []  # List of lottery tickets
        self.trades = []  # List of trades made by the user

    # 修饰器函数，用于检查用户权限
    def require_admin_permission(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.permission != 1:
                print("You do not have admin permission to perform this action.")
                return
            return func(self, *args, **kwargs)

        return wrapper

    def buy_market_price_stock(self, stock, quantity):
        """市价买入股票"""
        if self.cash >= stock.get_current_price() * quantity:
            self.cash -= stock.get_current_price() * quantity
            if stock.code not in self.stocks:
                self.stocks[stock.code] = 0
            self.stocks[stock.code] += quantity
            trade = (datetime.now(), 'BUY', stock.code, quantity, stock.get_current_price())
            self.trades.append(trade)
            print(f"Bought {quantity} shares of {stock.name} at market price.")
        else:
            print("Insufficient funds to complete the purchase.")

    def sell_market_price_stock(self, stock, quantity):
        """市价卖出股票"""
        if stock.code in self.stocks and self.stocks[stock.code] >= quantity:
            self.cash += stock.get_current_price() * quantity
            self.stocks[stock.code] -= quantity
            trade = (datetime.now(), 'SELL', stock.code, quantity, stock.get_current_price())
            self.trades.append(trade)
            print(f"Sold {quantity} shares of {stock.name} at market price.")
        else:
            print("Insufficient shares to sell.")

    def view_holdings(self):
        """展示持仓"""
        print("Your current stock holdings:")
        for code, quantity in self.stocks.items():
            print(f"{code}: {quantity} shares")

    def show_history(self):
        """展示交易历史记录"""
        print("Your trade history:")
        for trade in self.trades:
            trade_time, action, code, quantity, price = trade
            print(f"{trade_time} - {action} {quantity} shares of code {code} at {price}")

    def get_current_cash(self):
        """获取当前可用资金"""
        return self.cash