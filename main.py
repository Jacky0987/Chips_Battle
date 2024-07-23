from game import menu
from game.market import Market
from game.user import User
from game.menu import *

import utils.auth as auth

# Initialization (Do not modify)
user_file_path = "account.txt"
auth.file_initialize(user_file_path)

# Market Setup
market = Market()

# System Default Stock Setup (can be customized)
apple = Stock("AAPL", "Apple Inc.", 150, 20000)
FYRX = Stock("FYRX", "YR & FYX Entertainment", 280, 20000)
market.add_stock(apple)
market.add_stock(FYRX)
market.save_stock_data()

# User Setup (can be customized)
default_cash = 10000000
default_permission = 0

# Main Menu
# User & Password only saved in account.txt, no other data is saved
# There is no Password attribute in User class which means the password is not stored in class User
user_name, login_status = menu.auth_menu()
if login_status:
    current_user = User(user_name,  default_cash, default_permission)
    current_user.save_userdata(f"data/user/{user_name}.json")
    current_user = current_user.load_userdata_from_name(f"data/user/{user_name}.json", user_name)
    menu.game_menu(market, current_user)