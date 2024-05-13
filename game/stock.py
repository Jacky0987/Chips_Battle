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

        # 计算价格变化的百分比
        percent_changes = []
        for i in range(1, len(prices)):
            change = (prices[i] - prices[i - 1]) / prices[i - 1] * 100
            percent_changes.append(f'{change:.2f}%')
        percent_changes.insert(0, 'N/A')  # 第一个数据点设置为'N/A'

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, prices, marker='o')

        # 在每个数据点上添加带有颜色的百分比变化的文本
        for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
            if i == 0:
                # 第一个数据点设置为默认颜色（黑色）
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8)
            elif prices[i] > prices[i - 1]:
                # 价格上升，设置为红色
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8, color='red')
            else:
                # 价格下降，设置为绿色
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8, color='green')

        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.title(f'Price History for {self.name} (Code: {self.code})')
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate()
        plt.show()

    def update_rw_price(self, step_size=1.0, volatility=0.05):
        """使用随机游走模型来更新股票价格...? 小心负数！"""
        price_change = step_size * (random.random() * 2 - 1) * self.current_price * volatility
        self.current_price += price_change
        # 确保价格不会变成负数（如果需要）
        self.current_price = max(self.current_price, 0.01)
        self.update_price(self.current_price)
