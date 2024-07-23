import menu
import utils.auth as auth
from game.market import Market
from game.user import User
from game.stock import Stock

# Initialization
user_file_path = "account.txt"
auth.file_validation(user_file_path)

# Market Setup
market = Market()

apple = Stock("AAPL", "Apple Inc.", 150, 20000)
FYRX = Stock("FYRX", "YR & FYX Entertainment", 280, 20000)
market.add_stock(apple)
market.add_stock(FYRX)

# User Setup
default_cash = 10000000

# Main Menu
user_name, login_status = menu.auth_menu()
if login_status:
    user = User(user_name, "", default_cash, 1)
    menu.game_menu(market, user)