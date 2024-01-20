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
api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_base_url)
assets = api.list_assets()

for asset in assets:
    #print(asset.name)
    try:
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            cursor.execute('INSERT INTO stock (symbol, name) VALUES (?, ?)', (asset.symbol, asset.name))
            print(f'Added a new stock {asset.symbol} {asset.name} to the database')
    except Exception as e:
        print(asset.symbol)
        print(e)

#scheduled task to keep up to date
#command line to put out to a log file
#>> /logs/populate_log.txt 2>&1
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(timestamp)                


#populating db with stock price daily historical data
bars_db = api.get_bars(['AAPL', 'MSFT'], TimeFrame.Day, '2023-01-01', '2023-01-20')
bars_df = api.get_bars(['AAPL', 'MSFT'], TimeFrame.Day, '2023-01-01', '2023-01-20', adjustment='raw').df
print(bars_df)

for bar in bars_db:
    print(f'Processing symbol {bar.S} for date {bar.t.date()}')
    cursor.execute('SELECT id FROM stock WHERE symbol=?', (bar.S,))
    stock_id = cursor.fetchone()[0]

    #check if the stock price is already in the db
    timestamp_str = bar.t.strftime('%H:%M:%S')
    cursor.execute('SELECT id FROM stock_price WHERE stock_id=? AND date=?', (stock_id, bar.t.date()))
    stock_price_id = cursor.fetchone()
    if stock_price_id:
        print('Stock price already exists')
    else:
        cursor.execute('INSERT INTO stock_price (stock_id, date, timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
        (stock_id, bar.t.date(), timestamp_str, bar.o, bar.h, bar.l, bar.c, bar.v))


#get minute data
#min_bars = api.get_bars('MSFT', TimeFrame.Minute, '2024-01-18', '2024-01-19', adjustment='raw').df
#print(min_bars)

# data_api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_data_url)
# min_bars = data_api.get_latest_bars('MSFT')
# print(min_bars)


conn.commit()