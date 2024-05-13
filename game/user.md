## User Class
The user.py defines the User class, which represents a user in the game.

The user class has the following attributes:

1. `name`: The name of the user.
2. `cash`: The current cash balance of the user.
3. `permission`: The permission level of the user.
4. `stocks` : A dictionary containing the stocks owned by the user.
5. `lottery_tickets` : A list containing the lottery tickets owned by the user.
6. `trades` : A list containing the game history of the user.
7. `inventory` : A dictionary containing the items owned by the user.

The user class has the following methods:

### For `permission == 0` :
which means the normal user permission:

1. `buy_stock(stock_name, quantity)`: This method allows the user to buy a stock at the current price.
2. `sell_stock(stock_name, quantity)`: This method allows the user to sell a stock at the current price.
3. 



