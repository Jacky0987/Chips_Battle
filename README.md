
# Technical Documentation for Stock Trading Simulation Program

## I. Introduction
This technical documentation provides a detailed description of the architecture, design, and implementation details of the stock trading simulation program. The program aims to simulate the trading environment of the stock market, including user operations, stock trading logic, market status updates, and other functions.

## II. Program Architecture

### 1. Module Structure
The program mainly consists of the following modules:
- `market.py`: Responsible for market-related operations, such as adding and removing stocks, updating stock prices, and printing market information.
- `menu.py`: Contains the logic of the game menu and authentication menu, handling user input choices and corresponding operations.
- `stock.py`: Defines the stock class, including attributes of stocks and methods for price update, price history record, chart drawing, etc.
- `user.py`: Implements the user class, covering basic user information, stock trading operations, viewing holdings, showing trading history, and data saving functions.

### 2. Data Storage and Interaction
- User data: Stored in a file in JSON format and saved and read through the `save_userdata` method of the `User` class.
- Stock data: Stored in the relevant class objects in memory during program runtime.

## III. Module Details

### 1. `Market` Module (`market.py`)
- `__init__` method: Initializes the market object, creates a list of stocks, and sets the default world environment value.
    - `self.stocks`: Used to store stock objects in the market.
    - `self.world_environment`: Represents the world environment factor that affects stock prices.
- `add_stock` method: Adds a new stock to the market, ensuring it is added only if it doesn't already exist in the market, and prints the corresponding prompt message.
- `remove_stock` method: Removes the specified stock from the market, and performs the removal operation only if the stock exists in the market, and prints a prompt.
- `update_all_stocks` method: Iterates through all stocks in the market and calls the price update method of each stock.
- `print_all_stocks` method: Prints detailed information of all stocks in the market, including the world environment value and various attributes of the stocks.

### 2. `Menu` Module (`menu.py`)
- `options` dictionary: Defines the operation options available to the user in the menu and their descriptions.
- `game_menu` function: Logic of the game main menu.
    - Starts a thread `update_prices` for real-time stock price updates.
    - Continuously waits for user input choices and performs corresponding operations based on the choices, such as buying and selling stocks, viewing holdings, market information, etc.
    - Checks if the user's cash is below zero after the operation. If so, exits the simulation.
- `auth_menu` function: Logic of the authentication menu.
    - Provides options for registration, login, and exit.
    - Performs corresponding authentication operations based on user input, provides prompts, and recursively calls to maintain menu availability.

### 3. `Stock` Module (`stock.py`)
- `__init__` method: Initializes the attributes of the stock object, including code, name, initial price, initial issued shares, etc., and initializes the price history record.
    - `self.code`: Stock code.
    - `self.name`: Stock name.
    - `self.initial_price`: Initial price.
    - `self.current_price`: Current price.
    - `self.initial_issued_shares`: Initial issued shares.
    - `self.purchasable_shares`: Purchasable shares.
    - `self.trading_volume`: Trading volume.
    - `self.price_history`: Price history record.
    - `self.historical_mean`: Historical average price.
    - `self.volatility`: Volatility.
- `update_price` method: Updates the current price of the stock and adds the timestamp and new price to the price history record.
- `draw_price_history` method: Draws the stock price history line chart using the `matplotlib.pyplot` library and adds annotations such as percentage changes and initial price.
- `update_rw_price` method: Calculates and updates the random walk price of the stock based on factors such as the world environment and trading volume.
- `get_current_price` method: Returns the current price of the stock.
- `get_price_history` method: Returns the price history record of the stock.

### 4. `User` Module (`user.py`)
- `__init__` method: Initializes the attributes of the user object, including username, cash, stock holdings, and trading records.
    - `self.name`: Username.
    - `self.cash`: Cash balance.
    - `self.stocks`: Stock holdings dictionary with the stock code as the key and the holding quantity as the value.
    - `self.trades`: Trading record list.
- `buy_market_price_stock` method: User's stock purchase operation, including checks for stock validity, purchase quantity, and sufficient funds. Updates user's cash, stock holdings, and trading records upon successful purchase.
- `sell_market_price_stock` method: User's stock selling operation, checks if the holding quantity is sufficient. Updates relevant data upon successful sale.
- `view_holdings` method: Prints the user's current stock holdings and cash balance.
- `show_history` method: Prints the user's trading history record.
- `to_dict` method: Converts the relevant data of the user object into a dictionary format for JSON serialization.
- `save_userdata` method: Saves the user data in JSON format to the specified file.
- `get_current_cash` method: Returns the user's current cash balance.
- `add_cash` method: Increases the user's cash balance.
- `deduce_cash` method: Deducts the user's cash balance.

## IV. Key Technical Implementation Points

### 1. Random Price Update
The stock price update adopts a random walk model, considering factors such as the world environment, historical mean, and trading volume to simulate price fluctuations in the real market.

### 2. Concurrent Processing
In `game_menu`, a thread is used to update stock prices in real-time to simulate the dynamic changes in the market without blocking user input and processing.

### 3. Data Serialization
User data is serialized and saved using JSON to maintain the user's state and trading records between multiple program runs.

## V. Runtime Environment
- Python version: [Specific version]
- Dependent libraries: `matplotlib`, `numpy`, `datetime`, `json`

## VI. Future Improvement Directions
- Add more market influence factors and trading strategies.
- Optimize the price update algorithm to improve the authenticity of the simulation.
- Provide more rich user interaction and interface display.
