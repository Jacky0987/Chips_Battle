import threading
import time
import os
from game.market import Market
from game.user import User
from game.stock import Stock

# Initialize the market and stocks
market = Market()
apple = Stock("AAPL", "Apple Inc.", 150)
FYRX = Stock("FYRX", "YR & FYX Entertainment", 280)
market.add_stock(apple)
market.add_stock(FYRX)


# User setup with default admin permission
user = User("Guest", "", 10000, 1)

# Price update function
def update_prices():
    while True:
        for stock in market.stocks:
            stock.update_rw_price(market.world_environment)
        time.sleep(1)  # Update every second

# Start the price update thread
price_update_thread = threading.Thread(target=update_prices, daemon=True)
price_update_thread.start()

options = {
    'a': "Purchase stock",
    'b': "Sell stock",
    'c': "View your stocks",
    'd': "View market",
    'e': "Show certain stock graph",
    'f': "Modify market stocks",
    'g': "Show operation history",
    'h': "Modify world environment",
    'i': "Exit"
}



while True:
    print("\nChoose an option:")
    for key, value in options.items():
        print(f"{key}: {value}")
    print(f"\nCurrent cash: J$ {user.get_current_cash():,.2f}")
    choice = input("Your choice (a/b/c/d/e/f/g/h/i): ").lower()

    if choice == 'i':
        print("Exiting the simulator.")
        break
    elif choice == 'a':
        stock_code = input("Enter stock code to purchase: ")
        quantity = int(input("Enter quantity to purchase: "))
        stock = next((s for s in market.stocks if s.code == stock_code), None)
        if stock:
            user.buy_market_price_stock(stock, quantity)
        else:
            print("Stock not found.")
    elif choice == 'b':
        stock_code = input("Enter stock code to sell: ")
        quantity = int(input("Enter quantity to sell: "))
        stock = next((s for s in market.stocks if s.code == stock_code), None)
        if stock:
            user.sell_market_price_stock(stock, quantity)
        else:
            print("Stock not found.")
    elif choice == 'c':
        user.view_holdings()
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
            new_stock = Stock(code, name, price)
            market.add_stock(new_stock)
        elif modification == 'remove':
            code = input("Enter stock code to remove: ")
            stock = next((s for s in market.stocks if s.code == code), None)
            if stock:
                market.remove_stock(stock)
            else:
                print("Stock not found.")
    elif choice == 'g':
        user.show_history()
    elif choice == 'h':
        new_environment = int(input("Enter new world environment value (1-100): "))
        market.world_environment = new_environment
        print(f"World environment set to {new_environment}.")
    else:
        print("Invalid choice. Please select a valid option.")

    # Check if the user's cash is below zero after the operation
    if user.get_current_cash() < 0:
        print("Your cash balance is below zero. Exiting the simulator.")
        break

    input("Press Enter to return to the menu...")

