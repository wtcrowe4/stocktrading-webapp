import sqlite3
import os
import dotenv
import alpaca_trade_api as tradeapi
import datetime as dt

dotenv.load_dotenv()

alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_api_secret = os.getenv('ALPACA_API_SECRET')
alpaca_base_url = os.getenv('ALPACA_BASE_URL')
alpaca_paper_url = os.getenv('ALPACA_PAPER_URL')
alpaca_paper_api_key = os.getenv('ALPACA_PAPER_API_KEY')
alpaca_paper_api_secret = os.getenv('ALPACA_PAPER_API_SECRET')
alpaca_data_url = os.getenv('ALPACA_DATA_URL')
db_url = os.getenv('DATABASE_URL')

conn = sqlite3.connect(db_url)
cursor = conn.cursor()

api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_base_url)
paper_api = tradeapi.REST(alpaca_paper_api_key, alpaca_paper_api_secret, base_url=alpaca_paper_url)

account = paper_api.get_account()
print(account.status)

# check orders to stop duplicates
orders = paper_api.list_orders(status='all', limit=100)
print(f"Orders: {orders}")
ordered_symbols = [order.symbol for order in orders]

cursor.execute('''
                SELECT id from strategy where name = 'simple_moving_average'
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
current_date_str = current_date.tostirng()
opening_min_bar = f"{str(current_date_str)} 08:00:00+00:00"
fifteen_min_bar = f"{str(current_date_str)} 08:15:00+00:00"

for stock in stocks:
    minute_bars = api.get_bars(stock[0], '1Min', start=current_date_str, end=current_date_str).df
    print(stock)
    
    
