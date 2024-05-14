from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import random


class Stock:
    def __init__(self, code, name, current_price, historical_mean=None, volatility=0.05):
        self.code = code
        self.name = name
        self.current_price = current_price
        self.price_history = []
        self.historical_mean = historical_mean if historical_mean is not None else current_price
        self.volatility = volatility
        self.pause_updates = 0
        self.last_four_prices = [current_price] * 4

    def update_price(self, new_price):
        from datetime import datetime
        self.current_price = new_price
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.price_history.append((timestamp, new_price))
    def get_current_price(self):
        return self.current_price

    def get_price_history(self):
        return self.price_history

    def draw_price_history(self):
        timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts, _ in self.price_history]
        prices = [price for _, price in self.price_history]
        percent_changes = []
        for i in range(1, len(prices)):
            change = (prices[i] - prices[i - 1]) / prices[i - 1] * 100
            percent_changes.append(f'{change:.2f}%')
        percent_changes.insert(0, 'N/A')
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, prices, marker='o')
        # 在每个数据点上添加带有颜色的百分比变化的文本 价格上升，设置为红色 价格下降，设置为绿色
        for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
            if i == 0:
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8)
            elif prices[i] > prices[i - 1]:
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8, color='red')
            else:
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8, color='green')

        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.title(f'Price History for {self.name} (Code: {self.code})')
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate()
        plt.show()

    def update_rw_price(self, world_environment):
        if self.pause_updates > 0:
            self.pause_updates -= 1
            return

        environment_effect = (world_environment - 50) / 100
        mean_reversion_factor = 0.005 + 0.005 * environment_effect
        deviation_from_mean = self.historical_mean - self.current_price
        random_noise = np.random.normal(0, self.current_price * self.volatility * (1 - 0.5 * abs(environment_effect)))

        new_price = self.current_price + \
                    (mean_reversion_factor * deviation_from_mean) + \
                    (random_noise)

        new_price = max(new_price, 0.1 * self.historical_mean)
        self.update_price(new_price)