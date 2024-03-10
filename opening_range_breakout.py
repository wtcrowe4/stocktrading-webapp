import sqlite3
import os
import dotenv
import alpaca_trade_api as tradeapi
import datetime as dt

dotenv.load_dotenv()

alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_api_secret = os.getenv('ALPACA_API_SECRET')
alpaca_base_url = os.getenv('ALPACA_BASE_URL')
alpaca_data_url = os.getenv('ALPACA_DATA_URL')
db_url = os.getenv('DATABASE_URL')

conn = sqlite3.connect(db_url)
cursor = conn.cursor()

api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_base_url)

cursor.execute('''
               SELECT id from strategy where name = 'opening_range_breakout'
               ''')

strategy_id = cursor.fetchone()[0]

cursor.execute('''
                SELECT symbol, name
                FROM stock
                JOIN stock_strategy on stock_strategy.stock_id = stock.id
                WHERE stock_strategy.strategy_id = ?
                ''', (strategy_id,))

stocks = cursor.fetchall()

current_date = dt.date.today().isoformat()

for stock in stocks:
    minute_bars = api.get_bars(stock[0], '1Min', start="2024-03-09", end="2024-03-09").df
    print(minute_bars)
