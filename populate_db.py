import os
from dotenv import load_dotenv
import sqlite3
import alpaca_trade_api as tradeapi

load_dotenv()
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_api_secret = os.getenv('ALPACA_API_SECRET')

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url='https://paper-api.alpaca.markets')
assets = api.list_assets()

for asset in assets:
    #print(asset.name)
    try:
        if asset.status == 'active' and asset.tradable:
            cursor.execute('INSERT INTO stock (symbol, company) VALUES (?, ?)', (asset.symbol, asset.name))
    except Exception as e:
        print(asset.symbol)
        print(e)

conn.commit()