import threading
import time
from game.stock import Stock
import sys
import os
import game.config as config
from game.config import get_user_file_path


EXCHANGE_RATE, _, _, _ = config.game_init()

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
game_dir = os.path.join(parent_dir, 'utils')
sys.path.append(game_dir)  # 将 utils 目录添加到系统路径，以便能够导入
sys.path.append('../')  # 将父目录添加到系统路径

import utils.auth as auth  # 或者指定要导入的函数，例如 from user import function_name

options = {
    'a': "Purchase stock",
    'b': "Sell stock",
    'c': "View your stocks",
    'd': "View market",
    'e': "Show certain stock graph",
    'f': "Modify market stocks",
    'g': "Show operation history",
    'h': "Modify world environment",
    'i': "Get Admin Access",
    'j': "Money Deposit or Withdrawal",
    'k': "Minigame Menu",
    'z': "Save and Exit"
}


def game_menu(market, user):
    time.sleep(1)

    # Start a thread to update stock prices every second
    def update_prices():
        while True:
            for stock in market.stocks:
                stock.update_rw_price(market.world_environment)
            market.save_stock_data()
            time.sleep(1)  # Update every 1 seconds

    price_update_thread = threading.Thread(target=update_prices, daemon=True)
    price_update_thread.start()

    while True:
        print("===================================")
        print("LOCAL PLAYER MAIN MENU:")
        print("a. Trading Options")
        print("b. Information Management")
        print("c. Data Modification")
        print("d. Special Operations")
        print("e. Minigame Functions")
        print("z. Others")
        print("===================================")

        choice = input("Your choice (letter): ").lower()

        if choice == 'a':
            print("===================================")
            print("=========Trading Options===========")
            print("a1. Purchase Stock")
            print("a2. Sell Stock")
            print("a3. Money Deposit or Withdrawal")
            print("===================================")
            sub_choice = input("Your sub-choice (letter): ").lower()
            if sub_choice == 'a1':
                stock_code = input("Enter stock code to purchase: ")
                quantity = int(input("Enter quantity to purchase: "))
                stock = next((s for s in market.stocks if s.code == stock_code), None)
                if stock:
                    user.buy_market_price_stock(stock, quantity)
                else:
                    print("Stock not found.")
            elif sub_choice == 'a2':
                stock_code = input("Enter stock code to sell: ")
                quantity = int(input("Enter quantity to sell: "))
                stock = next((s for s in market.stocks if s.code == stock_code), None)
                if stock:
                    user.sell_market_price_stock(stock, quantity)
                else:
                    print("Stock not found.")
            elif sub_choice == 'a3':
                operation = input("Do you want to deposit or withdraw money? (deposit/withdraw): ")
                if operation == 'deposit':
                    user.add_cash(float(input("Enter amount to deposit: ")))
                elif operation == 'withdraw':
                    user.withdraw_cash(float(input("Enter amount to withdraw: ")))

        elif choice == 'b':
            print("===================================")
            print("======Information Management=======")
            print("b1. View your stocks")
            print("b2. View market")
            print("b3. Show certain stock graph")
            print("b4. Show operation history")
            print("===================================")
            sub_choice = input("Your sub-choice (letter): ").lower()
            if sub_choice == 'b1':
                user.view_holdings()
            elif sub_choice == 'b2':
                market.print_all_stocks()
            elif sub_choice == 'b3':
                stock_code = input("Enter stock code to view its graph: ")
                stock = next((s for s in market.stocks if s.code == stock_code), None)
                if stock:
                    stock.draw_price_history()
                else:
                    print("Stock not found.")
            elif sub_choice == 'b4':
                user.show_history()

        elif choice == 'c':
            print("===================================")
            print("=======Data Modification===========")
            print("c1. Modify market stocks")
            print("c2. Modify world environment")
            print("===================================")
            sub_choice = input("Your sub-choice (letter): ").lower()
            if sub_choice == 'c1':
                modification = input("Do you want to add or remove a stock? (add/remove): ")
                if modification == 'add':
                    code = input("Enter new stock code: ")
                    name = input("Enter new stock name: ")
                    price = float(input("Enter initial price: "))
                    share = int(input("Enter initial share quantity: "))
                    new_stock = Stock(code, name, price, share)
                    market.add_stock(new_stock)
                    market.save_stock_data()
                elif modification == 'emove':
                    code = input("Enter stock code to remove: ")
                    stock = next((s for s in market.stocks if s.code == code), None)
                    if stock:
                        market.remove_stock(stock)
                    else:
                        print("Stock not found.")
            elif sub_choice == 'c2':
                if user.permission == 1:
                    new_environment = int(input("Enter new world environment value (1-100): "))
                    market.world_environment = new_environment
                    print(f"World environment set to {new_environment}.")
                else:
                    print("You do not have permission to modify the world environment.")

        elif choice == 'd':
            print("===================================")
            print("========Special Operations=========")
            print("d1. Get Admin Access")
            print("===================================")
            sub_choice = input("Your sub-choice (letter): ").lower()
            if sub_choice == 'd1':
                user.get_admin()

        elif choice == 'e':
            print("===================================")
            print("=========Minigame Functions========")
            print("e1. Blackjacky")
            print("e2. Texas Hold'em")
            print("e3. Lottery Ticket")
            print("===================================")
            sub_choice = input("Your sub-choice (letter): ").lower()
            if sub_choice == 'e1':
                pass
            elif sub_choice == 'e2':
                pass
            elif sub_choice == 'e3':
                pass

        elif choice == 'z':
            user.save_userdata(f"data\\user\\{user.name}.json")
            market.save_stock_data()
            print("Exiting the simulator.")
            break

        # Check if the user's cash is below zero after the operation
        if user.get_current_cash() < 0:
            print("Your cash balance is below zero. Exiting the simulator.")
            break

        input("Press Enter to return to the menu...")

def auth_menu():
    login_success = False  # 新增一个标志，用于判断是否登录成功
    while True:
        print("\nChoose an option:")
        print("1: Sign up")
        print("2: Log in")
        print("3: Exit")
        choice = input("Your choice: ")

        if choice == '1':
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            login_success = auth.register(name, password, get_user_file_path())
            # 注册成功后返回用户名和登录状态
            if not login_success:
                print("Invalid username or password. Please try again.")
                continue  # 继续下一次循环，而不是重新调用函数
            else:
                print("Registration successful. User: "f"{name}")
                return name, True
            break

        elif choice == '2':
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            if auth.login(name, password, get_user_file_path()):
                print("Login successful. User: "f"{name}")
                login_success = True  # 登录成功，设置标志为 True
                return name, True
            else:
                print("Invalid username or password. Please try again.")

        elif choice == '3':
            print("Exiting the simulator.")
            break

        else:
            print("Invalid choice. Please select a valid option.")
    if login_success:  # 如果登录成功，不再执行后续的循环
        return name, login_success


def multiplayer_menu():
    print("\nChoose an option:")
    print("1: Start a new game")
    print("2: Join an existing game")
    print("3: Exit")
    choice = input("Your choice: ")

    if choice == '1':
        print("Starting a new game.")
        return True

    elif choice == '2':
        print("Joining an existing game.")
        return False

    elif choice == '3':
        print("Exiting the simulator.")
        return False

    else:
        print("Invalid choice. Please select a valid option.")
        return False

def minigame_menu(current_user):

    print("\nChoose an Minigame option:")
    print("1: Start a new game")
    print("2. Buy in Chips")
    print("3: Sell in Chips")
    print(f"Current Exchange Rate: 1 Chips = {EXCHANGE_RATE} J$")
    print(f"Current User: {current_user.name}")
    print(f"Current Chips: USD {current_user.chips}")
    print(f"Current Cash: J${current_user.cash}")
    print("z: Exit")

    choice = input("Your choice: ")

    if choice == '1':
        print("Choose a minigame to play.")
        print("1: Blackjack")
        print("2: Texas Hold'em")
        print("3: Lottery")
        print("z: Exit")

        choice = input("Your choice: ")

        if choice == '1':
            print("Starting Blackjack.")
            return True

        elif choice == '2':
            print("Starting Texas Hold'em.")
            return True

        elif choice == '3':
            print("Starting Lottery.")
            return True

        elif choice == 'z':
            print("Exiting the minigame menu.")

        else:
            print("Invalid choice. Please select a valid option.")
            minigame_menu()
        return True

    elif choice == '2':
        print("Buy in Chips.")
        return True

    elif choice == '3':
        print("Sell in Chips.")
        return True

    elif choice == 'z':
        print("Exiting the minigame menu.")

    else:
        print("Invalid choice. Please select a valid option.")
        minigame_menu()