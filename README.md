# 《Stock Trading Simulator Development Technical Documentation》

1、Overview
This project is a stock trading simulator, mainly including modules such as Stock, Market, User, menu, and config. Through the collaboration of these modules, the simulation of stock trading, the management of user operations, and the storage and display of data are realized.

 二、Module Description

# 1. `Stock` Module
 - **Function**: Represents a single stock, responsible for storing relevant information about the stock, such as code, name, initial price, current price, initial issued shares, purchasable shares, trading volume, price history, etc. It also provides methods for updating the price, drawing the price history graph and animation history graph, and updating the random walk price according to the market environment.
 - **Key Methods**:
     - `update_price(new_price)`: Updates the current price of the stock and records the price history.
     - `draw_price_history()`: Draws the stock price history graph, including the percentage change in price and the horizontal line of the initial price.
     - `draw_price_anime_history()`: Draws the stock price animation history graph.
     - `update_rw_price(world_environment)`: Updates the stock price based on the world environment and random factors.
     - `get_current_price()`: Gets the current price of the stock.
     - `get_price_history()`: Gets the price history of the stock.

# 2. `Market` Module
 - **Function**: Represents the market, responsible for managing the list of stocks and the world environment. Provides methods for adding stocks, removing stocks, updating the prices of all stocks, printing information about all stocks, and saving stock data.
 - **Key Methods**:
     - `add_stock(stock)`: Adds a stock to the market.
     - `remove_stock(stock)`: Removes a stock from the market.
     - `update_all_stocks()`: Updates the prices of all stocks in the market.
     - `print_all_stocks()`: Prints detailed information about all stocks in the market.
     - `save_stock_data()`: Saves the stock data to a file.

# 3. `User` Module
 - **Function**: Represents the user, responsible for storing relevant information about the user, such as name, cash, permission, stock holdings, transaction records, and chips. Provides methods for buying stocks, selling stocks, viewing holdings, showing transaction history, saving user data, and loading user data from a file.
 - **Key Methods**:
     - `buy_market_price_stock(stock, quantity)`: Buys stocks at the market price.
     - `sell_market_price_stock(stock, quantity)`: Sells stocks at the market price.
     - `view_holdings()`: Views the user's stock holdings.
     - `show_history()`: Shows the user's transaction history.
     - `to_dict()`: Converts the user data into a dictionary format for easy storage as JSON.
     - `save_userdata(filename)`: Saves the user data to a file.
     - `load_userdata_from_name(filename, name)`: Loads the user data from a file.
     - `get_current_cash()`: Gets the user's current cash.
     - `add_cash(amount)`: Adds cash to the user (requires permission).
     - `deduce_cash(amount)`: Deducts cash from the user (requires permission).
     - `get_admin()`: Gets administrator privileges (requires password input).

# 4. `menu` Module
 - **Function**: Provides the game's menu interface and interaction logic, including user authentication, the main game menu, multiplayer game menu, and mini-game menu. It also starts a thread to update the stock price in real time.
 - **Key Methods**:
     - `game_menu(market, user)`: The main game menu, handles various user choices, such as trading operations, information management, data modification, special operations, and mini-games.
     - `auth_menu()`: The user authentication menu, handles user registration and login.
     - `multiplayer_menu()`: The multiplayer game menu, handles the user's choice to start a new game or join an existing game.
     - `minigame_menu(current_user)`: The mini-game menu, handles the user's choices in the mini-game, such as starting the game, buying or selling chips.
     - `gui_game_menu(market, user)`: The graphical user interface of the main game menu, created using the `tkinter` library.

# 5. `config` Module
 - **Function**: Responsible for the initialization configuration of the game, including market initialization, game initialization (setting the exchange rate, default cash, default permission, and user file path), and obtaining the user file path.
 - **Key Methods**:
     - `market_init()`: Initializes the market and adds default stocks.
     - `game_init()`: Initializes the game configuration, reads or creates the `config.json` file.
     - `get_user_file_path()`: Gets the user file path.

 三、Development Key Technology Stack
 - **Python Programming Language**: Used to implement the logic of the entire stock trading simulator.
 - **matplotlib Library**: Used to draw the stock price history graph and animation history graph.
 - **numpy Library**: Used to generate random numbers to simulate the random fluctuation of stock prices.
 - **tkinter Library**: Used to create the graphical user interface of the main game menu.
 - **json Library**: Used for data storage and reading, saving stock and user data in JSON format to files.
 - **threading Library**: Used to create threads to achieve real-time updates of stock prices.

 四、Development Progress
 - At present, the basic functions of the Stock, Market, User, menu, and config modules have been completed.
 - Users can register, log in, and perform operations such as stock trading, information query, data modification in the main game menu.
 - Stock prices can be updated in real time according to the market environment and saved to files.
 - The graphical user interface of the main game menu has been initially created, but some functions are still being perfected.
 - The multiplayer game function and mini-game expansion have not yet started development.

 五、Development Direction
 - **Multiplayer Game Function**: Further implement the logic of multiplayer games, including player interaction and data synchronization.
 - **Mini-game Expansion**: Add more mini-games to enrich the game experience.
 - **Data Analysis and Visualization**: Analyze and visualize the stock trading data to provide users with more decision support.
 - **Intelligent Trading Strategies**: Introduce some simple intelligent trading strategies for users to choose to use.
 - **User Interface Optimization**: Continue to optimize the graphical user interface to improve the user experience.

 六、Improvement Direction
 - **Performance Optimization**: Optimize the algorithm for updating stock prices to improve the running efficiency of the program.
 - **Data Validation and Error Handling**: Strengthen data validation and error handling to improve the stability of the program.
 - **User Permission Management**: Further refine the user permission management to ensure that users can only perform operations within their permission scope.
 - **Code Refactoring and Optimization**: Refactor and optimize the code to improve the readability and maintainability of the code.
 - **Add Market Events and News**: Simulate the impact of market events and news on stock prices to increase the authenticity of the game.
 - **Connection with Actual Market Data**: Consider connecting with actual market data to make the simulation closer to the real situation.

The above content is for reference only, and you can adjust and improve it according to the actual needs and project situation.