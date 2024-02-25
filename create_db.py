import sqlite3
import os
import dotenv

dotenv.load_dotenv()
db_url = os.getenv('DATABASE_URL')

conn = sqlite3.connect(db_url)

cursor = conn.cursor()

# Create the stock and stock_price tables for data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY, 
        symbol TEXT NOT NULL UNIQUE, 
        name TEXT NOT NULL,
        exchange TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY, 
        stock_id INTEGER,
        date NOT NULL,
        timestamp NOT NULL,
        open NOT NULL,
        high NOT NULL,
        low NOT NULL,
        close NOT NULL,
        volume NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
''')


# Create the user table for authentication

# Create tables for strategies
cursor.execute('''
    CREATE TABLE IF NOT EXISTS strategy (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_strategy (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        strategy_id INTEGER,
        FOREIGN KEY (stock_id) REFERENCES stock (id),
        FOREIGN KEY (strategy_id) REFERENCES strategy (id)
    )
''')

conn.commit()