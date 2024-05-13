from datetime import datetime
import matplotlib.pyplot as plt
import random


class Stock:
    def __init__(self, code, name, current_price):
        self.code = code
        self.name = name
        self.current_price = current_price
        # 初始化价格历史记录为一个空列表
        self.price_history = []

    def update_price(self, new_price):
        self.current_price = new_price
        # 在价格历史中添加这个新价格和时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.price_history.append((timestamp, new_price))

    def get_current_price(self):
        return self.current_price

    def get_price_history(self):
        return self.price_history

    def draw_price_history(self):
        timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts, _ in self.price_history]
        prices = [price for _, price in self.price_history]

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, prices, marker='o')
        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.title(f'Price History for {self.name} (Code: {self.code})')
        plt.grid(True)
        plt.show()

    def update_rw_price(self, step_size=1.0, volatility=0.05):
        """使用随机游走模型来更新股票价格...? 小心负数！"""
        price_change = step_size * (random.random() * 2 - 1) * self.current_price * volatility
        self.current_price += price_change
        # 确保价格不会变成负数（如果需要）
        self.current_price = max(self.current_price, 0.01)
        self.update_price(self.current_price)
