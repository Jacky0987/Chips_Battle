from game.stock import Stock
from game.market import Market
from utils import auth
import json
import os


# Initialize Market
def market_init():
    # Market Setup
    market = Market()
    # System Default Stock Setup (can be customized)
    apple = Stock("AAPL", "Apple Inc.", 150, 20000)
    market.add_stock(apple)

    FYRX = Stock("FYRX", "YR & FYX Entertainment", 280, 20000)
    market.add_stock(FYRX)

    bank = Stock("BANK", "Bank of FYX Inc.", 1, 2000000)
    market.add_stock(bank)

    # Save Stock Data to File
    market.save_stock_data()

    return market


def game_init():
    # Default Initialization (Do not modify)
    user_file_path = "data\\config\\account.txt"

    # Minigame Chips to J$ Exchange rate
    # is set to {EXCHANGE_RATE} J$ per 1 chip
    EXCHANGE_RATE = 10000

    # User Setup (can be customized)
    default_cash = 10000000
    default_permission = 0

    # 尝试读取 config.json 中的配置
    if os.path.exists("data\\config\\config.json"):
        with open("data\\config\\config.json", "r") as json_file:
            config_data = json.load(json_file)
            EXCHANGE_RATE = config_data["EXCHANGE_RATE"]
            default_cash = config_data["default_cash"]
            default_permission = config_data["default_permission"]
            user_file_path = config_data["user_file_path"]
            return EXCHANGE_RATE, default_cash, default_permission, user_file_path
    else:
        # 如果文件不存在，使用默认配置
        config_data = {
            "EXCHANGE_RATE": EXCHANGE_RATE,
            "default_cash": default_cash,
            "default_permission": default_permission,
            "user_file_path": user_file_path
        }
        with open("config.json", "w") as json_file:
            json.dump(config_data, json_file, indent=4)

        return EXCHANGE_RATE, default_cash, default_permission, user_file_path


def get_user_file_path():
    _, _, _, user_file_path = game_init()
    return user_file_path