import sqlite3


def init_db():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    # Create a table for users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            cash REAL NOT NULL,
            permission INTEGER NOT NULL
        )
    ''')

    # Create a table for stocks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            user_id INTEGER,
            stock_name TEXT,
            quantity INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Commit changes and close the connection
    connection.commit()
    connection.close()


init_db()



# For update
class User:
    def __init__(self, name, cash, permission):
        self.name = name
        self.cash = cash
        self.permission = permission
        self.stocks = {}
        self.save()

    def save(self):
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO users (name, cash, permission) VALUES (?, ?, ?)',
                       (self.name, self.cash, self.permission))
        self.id = cursor.lastrowid  # Save the last inserted id to use for foreign key reference

        connection.commit()
        connection.close()

    def update_cash(self):
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        cursor.execute('UPDATE users SET cash = ? WHERE id = ?', (self.cash, self.id))
        connection.commit()
        connection.close()

    def add_stock(self, stock_name, quantity):
        if stock_name in self.stocks:
            self.stocks[stock_name] += quantity
        else:
            self.stocks[stock_name] = quantity

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO stocks (user_id, stock_name, quantity) VALUES (?, ?, ?)',
                       (self.id, stock_name, quantity))
        connection.commit()
        connection.close()
