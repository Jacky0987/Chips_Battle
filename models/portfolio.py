class Portfolio:
    def __init__(self, starting_cash=10000):
        self.cash = starting_cash
        self.stocks = {}  # Symbol -> shares
        self.transaction_history = []
        self.net_worth_history = [starting_cash]
        self.starting_cash = starting_cash

    def buy_stock(self, symbol, shares, price, day):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        cost = price * shares
        if cost > self.cash:
            return "Not enough cash for this purchase"

        # Execute the trade
        self.cash -= cost

        if symbol in self.stocks:
            self.stocks[symbol] += shares
        else:
            self.stocks[symbol] = shares

        # Record transaction
        self.transaction_history.append({
            "day": day,
            "type": "BUY",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": cost
        })

        return f"Bought {shares} shares of {symbol} at ${price:.2f} for ${cost:.2f}"

    def sell_stock(self, symbol, shares, price, day):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        if symbol not in self.stocks or self.stocks[symbol] < shares:
            return "Not enough shares to sell"

        proceeds = price * shares

        # Execute the trade

        #cash update
        self.cash += proceeds
        self.stocks[symbol] -= shares

        # Remove stock from portfolio if no shares left
        if self.stocks[symbol] == 0:
            del self.stocks[symbol]

        # Record transaction
        self.transaction_history.append({
            "day": day,
            "type": "SELL",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": proceeds
        })

        return f"Sold {shares} shares of {symbol} at ${price:.2f} for ${proceeds:.2f}"

    def short_sell(self, symbol, shares, price, day):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        # In a short sale, you borrow shares and sell them
        proceeds = price * shares
        self.cash += proceeds

        # Track the short position (negative shares)
        if symbol in self.stocks:
            self.stocks[symbol] -= shares
        else:
            self.stocks[symbol] = -shares

        # Record transaction
        self.transaction_history.append({
            "day": day,
            "type": "SHORT",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": proceeds
        })

        return f"Short sold {shares} shares of {symbol} at ${price:.2f} for ${proceeds:.2f}"

    def cover_short(self, symbol, shares, price, day):
        shares = int(shares)
        if shares <= 0:
            return "Invalid number of shares"

        if symbol not in self.stocks or self.stocks[symbol] >= 0 or abs(
                self.stocks[symbol]) < shares:
            return "Not enough shares to cover"

        cost = price * shares

        if cost > self.cash:
            return "Not enough cash to cover this short position"

        # Execute the cover
        self.cash -= cost
        self.stocks[symbol] += shares

        # Remove stock from portfolio if no shares left
        if self.stocks[symbol] == 0:
            del self.stocks[symbol]

        # Record transaction
        self.transaction_history.append({
            "day": day,
            "type": "COVER",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": cost
        })

        return f"Covered {shares} short shares of {symbol} at ${price:.2f} for ${cost:.2f}"

    def update_net_worth(self, stock_prices):
        """Calculate current net worth based on cash and stock prices"""
        net_worth = self.cash
        for symbol, shares in self.stocks.items():
            if symbol in stock_prices:
                # For long positions (positive shares), add value
                # For short positions (negative shares), subtract value
                if shares > 0:
                    net_worth += stock_prices[symbol] * shares
                else:
                    # For short positions, we owe these shares, so their value reduces our net worth
                    net_worth += stock_prices[symbol] * shares  # shares is negative, so this subtracts

        self.net_worth_history.append(net_worth)
        return net_worth
        
    # 添加新方法来记录股息交易
    def add_dividend_transaction(self, day, symbol, amount):
        """Record a dividend payment as a transaction"""
        self.transaction_history.append({
            "day": day,
            "type": "DIVIDEND",
            "symbol": symbol,
            "shares": 0,
            "price": 0,
            "total": amount
        })

    def get_summary(self, stock_dict):
        """Get a text summary of the portfolio"""
        summary = []
        total_value = self.cash

        summary.append(f"Cash: ${self.cash:.2f}")

        if self.stocks:
            summary.append("\nHoldings:")
            for symbol, shares in self.stocks.items():
                stock = stock_dict[symbol]
                value = stock.price * abs(shares)
                position_type = "LONG" if shares > 0 else "SHORT"
                total_value += value if shares > 0 else -value
                summary.append(f"{symbol} ({position_type}): {abs(shares)} shares at ${stock.price:.2f} = ${value:.2f}")

        summary.append(f"\nTotal Portfolio Value: ${total_value:.2f}")

        profit_loss = total_value - self.starting_cash
        profit_loss_percent = (profit_loss / self.starting_cash) * 100

        summary.append(f"Profit/Loss: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)")

        return "\n".join(summary)

    def get_final_evaluation(self):
        """Generate a final evaluation of portfolio performance"""
        final_value = self.net_worth_history[-1]
        profit_loss = final_value - self.starting_cash
        profit_loss_percent = (profit_loss / self.starting_cash) * 100

        if profit_loss_percent >= 50:
            rating = "Exceptional Investor"
        elif profit_loss_percent >= 25:
            rating = "Skilled Investor"
        elif profit_loss_percent >= 10:
            rating = "Good Investor"
        elif profit_loss_percent >= 0:
            rating = "Average Investor"
        elif profit_loss_percent >= -10:
            rating = "Novice Investor"
        else:
            rating = "Needs Improvement"

        evaluation = [
            "=== FINAL PERFORMANCE EVALUATION ===",
            f"Starting Capital: ${self.starting_cash:.2f}",
            f"Final Portfolio Value: ${final_value:.2f}",
            f"Profit/Loss: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)",
            f"Rating: {rating}",
            "\nTrading Statistics:",
            f"Total Transactions: {len(self.transaction_history)}",
        ]

        if self.transaction_history:
            buys = sum(1 for t in self.transaction_history if t["type"] == "BUY")
            sells = sum(1 for t in self.transaction_history if t["type"] == "SELL")
            shorts = sum(1 for t in self.transaction_history if t["type"] == "SHORT")
            covers = sum(1 for t in self.transaction_history if t["type"] == "COVER")

            evaluation.extend([
                f"Buy Transactions: {buys}",
                f"Sell Transactions: {sells}",
                f"Short Transactions: {shorts}",
                f"Cover Transactions: {covers}"
            ])

        return "\n".join(evaluation)
