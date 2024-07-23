import threading
import time
from game.stock import Stock
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
game_dir = os.path.join(parent_dir, 'utils')
sys.path.append(game_dir)  # 将 utils 目录添加到系统路径，以便能够导入

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
    'z': "Save and Exit"
}


def game_menu(market, user):
    time.sleep(1)
    def update_prices():
        while True:
            for stock in market.stocks:
                stock.update_rw_price(market.world_environment)
            market.save_stock_data()
            time.sleep(1)  # Update every 1 seconds


    # Start the price update thread
    price_update_thread = threading.Thread(target=update_prices, daemon=True)
    price_update_thread.start()

    # Print the menu
    while True:
        print("\nChoose an option:")
        for key, value in options.items():
            print(f"{key}: {value}")
        print("===========================================================================")
        print(f"Current user: {user.name}")
        print(f"Current cash: J$ {user.get_current_cash(user):,.2f}")
        print(f"Current world environment: {market.world_environment}")
        choice = input("Your choice (a/b/c/d/e/f/g/h/i): ").lower()

        if choice == 'z':
            user.save_userdata("data\\user\\userdata.json")
            """stock.save_stock_data("data\\stock\\stockdata.json")"""
            market.save_stock_data()
            print("Exiting the simulator.")
            break

        elif choice == 'a':
            stock_code = input("Enter stock code to purchase: ")
            quantity = int(input("Enter quantity to purchase: "))
            stock = next((s for s in market.stocks if s.code == stock_code), None)
            if stock:
                user.buy_market_price_stock(user, stock, quantity)
            else:
                print("Stock not found.")

        elif choice == 'b':
            stock_code = input("Enter stock code to sell: ")
            quantity = int(input("Enter quantity to sell: "))
            stock = next((s for s in market.stocks if s.code == stock_code), None)
            if stock:
                user.sell_market_price_stock(user, stock, quantity)
            else:
                print("Stock not found.")

        elif choice == 'c':
            user.view_holdings(user)

        elif choice == 'd':
            market.print_all_stocks()

        elif choice == 'e':
            stock_code = input("Enter stock code to view its graph: ")
            stock = next((s for s in market.stocks if s.code == stock_code), None)
            if stock:
                stock.draw_price_history()
            else:
                print("Stock not found.")

        elif choice == 'f':
            modification = input("Do you want to add or remove a stock? (add/remove): ")
            if modification == 'add':
                code = input("Enter new stock code: ")
                name = input("Enter new stock name: ")
                price = float(input("Enter initial price: "))
                share = int(input("Enter initial share quantity: "))
                new_stock = Stock(code, name, price, share)
                market.add_stock(new_stock)
                market.save_stock_data()
            elif modification == 'remove':
                code = input("Enter stock code to remove: ")
                stock = next((s for s in market.stocks if s.code == code), None)
                if stock:
                    market.remove_stock(stock)
                else:
                    print("Stock not found.")

        elif choice == 'g':
            user.show_history(user)

        elif choice == 'h':
            new_environment = int(input("Enter new world environment value (1-100): "))
            market.world_environment = new_environment
            print(f"World environment set to {new_environment}.")

        elif choice == 'i':
            user.get_admin(user)

        elif choice == 'j':
            operation = input("Do you want to deposit or withdraw money? (deposit/withdraw): ")
            if operation == 'deposit':
                user.add_cash(user, float(input("Enter amount to deposit: ")))
            elif operation == 'withdraw':
                user.withdraw_cash(user, float(input("Enter amount to withdraw: ")))

        else:
            print("Invalid choice. Please select a valid option.")

        # Check if the user's cash is below zero after the operation
        if user.get_current_cash(user) < 0:
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
            auth.register(name, password, "data\\account.txt")
            # print("Registration successful.")
            auth_menu()
            break

        elif choice == '2':
            name = input("Enter your name: ")
            password = input("Enter your password: ")
            if auth.login(name, password, "data\\account.txt"):
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
        return