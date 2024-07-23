from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class Stock:
    def __init__(self, code, name, current_price, initial_issued_shares, historical_mean=None, volatility=0.05):
        self.code = code
        self.name = name
        self.initial_price = current_price
        self.current_price = current_price
        self.initial_issued_shares = initial_issued_shares  # Normally it doesn't change. It is more like a constant.
        self.purchasable_shares = initial_issued_shares  # This is changing as shares are bought and sold.
        self.trading_volume = 0
        self.price_history = [(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), current_price)]
        self.historical_mean = historical_mean if historical_mean is not None else current_price
        self.volatility = volatility
        self.pause_updates = 0  # DEPRECATED
        self.last_four_prices = [current_price] * 4

    def update_price(self, new_price):
        from datetime import datetime
        self.current_price = new_price
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.price_history.append((timestamp, new_price))

    def draw_price_history(self):
        timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts, _ in self.price_history]
        prices = [price for _, price in self.price_history]
        percent_changes = []

        for i in range(1, len(prices)):
            change = (prices[i] - prices[i - 1]) / prices[i - 1] * 100
            percent_changes.append(f'{change:.2f}%')
        percent_changes.insert(0, '')

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, prices, marker='o')

        # Add text for percent changes with color indication for rise or fall 
        for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
            if i == 0:
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8)
            elif prices[i] > prices[i - 1]:
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8, color='red')
            else:
                plt.text(timestamp, price, percent_changes[i], ha='center', va='bottom', fontsize=8, color='green')

        # Add a horizontal line showing the initial stock price
        plt.axhline(y=self.initial_price, color='blue', linestyle='--', label=f'Initial Price: {self.initial_price}')
        plt.legend()

        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.title(f' {self.name} (Code: {self.code}) for {self.initial_issued_shares} shares issued')
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate()
        plt.show()

    def update_rw_price(self, world_environment):

        environment_effect = (world_environment - 50) / 100 + (
                self.trading_volume / self.initial_issued_shares / self.initial_price)
        mean_reversion_factor = 0.005 + 0.002 * environment_effect
        deviation_from_mean = self.historical_mean - self.current_price
        random_noise = np.random.normal(0, self.current_price * self.volatility * (1 - 0.5 * abs(environment_effect)))

        new_price = self.current_price + \
                    (mean_reversion_factor * deviation_from_mean) + \
                    (random_noise)

        new_price = max(new_price, 0.1 * self.historical_mean)
        self.update_price(new_price)

    def get_current_price(self):
        return self.current_price

    def get_price_history(self):
        return self.price_history
