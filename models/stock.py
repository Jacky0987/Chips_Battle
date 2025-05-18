import random

class Stock:
    def __init__(self, name, symbol, initial_price, volatility, sector, pays_dividend=False, dividend_yield=0):
        self.name = name
        self.symbol = symbol
        self.price = initial_price
        self.volatility = volatility  # Percentage volatility per day
        self.sector = sector
        self.price_history = [initial_price]
        self.pays_dividend = pays_dividend
        self.dividend_yield = dividend_yield
        self.next_dividend_day = random.randint(5, 10) if pays_dividend else -1

    def update_price(self, sector_influence=0):
        # Base random movement based on volatility
        change_percent = random.normalvariate(0, self.volatility)

        # Add sector influence (stocks in same sector move similarly)
        change_percent += sector_influence

        # Calculate new price
        new_price = self.price * (1 + change_percent / 100)

        # Ensure price doesn't go below 0.1
        self.price = max(0.1, new_price)
        self.price_history.append(self.price)

    def check_dividend(self, current_day):
        if self.pays_dividend and current_day == self.next_dividend_day:
            dividend_amount = self.price * (self.dividend_yield / 100)
            self.next_dividend_day = current_day + random.randint(5, 10)
            return dividend_amount
        return 0
