from game.user import User
from game.stock import Stock
from game.market import Market

import time

# Initiate the market and add a stock to it.
market = Market()

stock1 = Stock('000001', 'Example Stock', 100.0)
market.add_stock(stock1)

# 创建用户
user1 = User('Alice', 10000, 0)  # 0 表示普通用户权限

# 用户购买股票
user1.buy_market_price_stock(stock1, 10)

# 打印用户持仓
user1.view_holdings()

# 更新股票价格（模拟市场变动）
end_time = time.time() + 2

while time.time() < end_time:
    market.update_all_stocks()
    time.sleep(1)  # 暂停1秒
    print(f"Current price of {stock1.code}: {stock1.current_price}")


# 用户卖出股票
user1.sell_market_price_stock(stock1, 5)
print(user1.get_current_cash())

# 打印交易历史
user1.show_history()

# 展示股票价格历史
stock1.draw_price_history()

# 打印市场中的所有股票信息
market.print_all_stocks()