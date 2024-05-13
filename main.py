from game.user import User
from game.stock import Stock
from game.market import Market

# 创建市场和股票
market = Market()
stock1 = Stock('000001', 'Example Stock', 100.0)

# 将股票添加到市场中
market.add_stock(stock1)

# 创建用户
user1 = User('Alice', 10000, 0)  # 0 表示普通用户权限

# 用户购买股票
user1.buy_market_price_stock(stock1, 10)

# 打印用户持仓
user1.view_holdings()

# 更新股票价格（模拟市场变动）
market.update_all_stocks()

# 用户卖出股票
user1.sell_market_price_stock(stock1, 5)

# 打印交易历史
user1.show_history()

# 展示股票价格历史
stock1.draw_price_history()

# 打印市场中的所有股票信息
market.print_all_stocks()