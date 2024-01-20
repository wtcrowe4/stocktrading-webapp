import os
from dotenv import load_dotenv
import sqlite3
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
import datetime

load_dotenv()
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_api_secret = os.getenv('ALPACA_API_SECRET')
alpaca_paper_url = os.getenv('ALPACA_PAPER_URL')
alpaca_data_url = os.getenv('ALPACA_DATA_URL')
alpaca_base_url = os.getenv('ALPACA_BASE_URL')
db_url = os.getenv('DATABASE_URL')

conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

#getting current stocks in db to check for new stocks when we call the api
cursor.execute('SELECT symbol FROM stock')
symbols = cursor.fetchall()
symbols = [symbol['symbol'] for symbol in symbols]


#api
api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_paper_url)
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
#command line to put out to a log file
#>> /logs/populate_log.txt 2>&1
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(timestamp)                


#populating db with stock price data
bars_db = api.get_bars(['AAPL', 'MSFT'], TimeFrame.Day, '2023-01-01', '2023-01-20')
bars_df = api.get_bars(['AAPL', 'MSFT'], TimeFrame.Day, '2023-01-01', '2023-01-20', adjustment='raw').df
print(bars_db)

for bar in bars_db:
    print(f'Processing symbol {bar.S}')
    cursor.execute('SELECT id FROM stock WHERE symbol=?', (bar.S,))
    stock_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO stock_price (stock_id, date, open, high, low, close, adjusted_close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
    (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.c, bar.v))


conn.commit()