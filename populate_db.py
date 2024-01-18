import os
from dotenv import load_dotenv
import sqlite3
import alpaca_trade_api as tradeapi

load_dotenv()
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_api_secret = os.getenv('ALPACA_API_SECRET')

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

#getting current stocks in db to check for new stocks when we call the api
cursor.execute('SELECT symbol FROM stock')
symbols = cursor.fetchall()
symbols = [symbol['symbol'] for symbol in symbols]


#populating db with stock symbols and company names
api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url='https://paper-api.alpaca.markets')
assets = api.list_assets()

for asset in assets:
    #print(asset.name)
    try:
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            cursor.execute('INSERT INTO stock (symbol, company) VALUES (?, ?)', (asset.symbol, asset.name))
            print(f'Added a new stock {asset.symbol} {asset.name} to the database')
    except Exception as e:
        print(asset.symbol)
        print(e)

#scheduled task to keep up to date
                

conn.commit()