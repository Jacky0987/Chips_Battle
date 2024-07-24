from game import menu
from game.market import Market
from game.user import User
from game.menu import *
from game.config import *

# Defined in config.py
market = market_init()
EXCHANGE_RATE, default_cash, default_permission, user_file_path = game_init()

# Initialize User File
auth.file_initialize(user_file_path)

# ===================================================================================================
# Local Game Main Menu
# User & Password only saved in account.txt, no other data is saved
# There is no Password attribute in User class which means the password is not stored in class User
# ===================================================================================================
user_name, login_status = menu.auth_menu()
if login_status:
    current_user = User(user_name,  default_cash, default_permission)
    current_user.save_userdata(f"data/user/{user_name}.json")
    current_user = current_user.load_userdata_from_name(f"data/user/{user_name}.json", user_name)
    menu.game_menu(market, current_user)

# Multiplayer Game Main Menu
# not implemented yet
