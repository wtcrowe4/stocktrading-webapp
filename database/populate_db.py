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


#populating db with stock symbols
api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_base_url)
assets = api.list_assets()

for asset in assets:
    #print(asset.name)
    try:
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            cursor.execute('INSERT INTO stock (symbol, name, exchange) VALUES (?, ?, ?)', (asset.symbol, asset.name, asset.exchange))
            print(f'Added a new stock {asset.symbol} {asset.name} to the database')
    except Exception as e:
        print(asset.symbol)
        print(e)



#scheduled task to keep up to date
#command line to put out to a log file
#>> /logs/populate_log.txt 2>&1
#timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#print(timestamp)                


#chunking and getting all daily data for last week
chunk_size = 100
start_date = '2024-06-01'
end_date = '2024-06-09'


for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]
    try:
        #remove '/' from symbol for api call
        symbol_chunk = [symbol.replace('/', '') if '/' in symbol else symbol for symbol in symbol_chunk]
        print('processing symbols', symbol_chunk)
        barsets = api.get_bars(symbol_chunk, TimeFrame.Day, start=start_date, end=end_date)
        #print(barsets)
        for bar in barsets:
            #print(f'Processing symbol {bar.S} for date {bar.t.date()}')
            cursor.execute('SELECT id FROM stock WHERE symbol=?', (bar.S,))
            stock_id = cursor.fetchone()[0]
            timestamp_str = bar.t.strftime('%H:%M:%S')
            cursor.execute('SELECT id FROM stock_price WHERE stock_id=? AND date=? AND timestamp=?', (stock_id, bar.t.date(), timestamp_str))
            stock_price_id = cursor.fetchone()
            if stock_price_id:
                #print('Stock price already exists')
                pass
            else:
                cursor.execute('INSERT INTO stock_price (stock_id, date, timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                (stock_id, bar.t.date(), timestamp_str, bar.o, bar.h, bar.l, bar.c, bar.v))
    except Exception as e:
        print(f'Error occurred while getting bars: {e}')



conn.commit()