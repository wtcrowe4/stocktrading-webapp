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
current_date_str = "2024-03-11"
opening_min_bar = f"{str(current_date_str)} 08:00:00+00:00"
fifteen_min_bar = f"{str(current_date_str)} 08:15:00+00:00"

for stock in stocks:
    minute_bars = api.get_bars(stock[0], '1Min', start=current_date_str, end=current_date_str).df
    print(stock)
    
    opening_range_mask = (minute_bars.index >= opening_min_bar) & (minute_bars.index <= fifteen_min_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    print(opening_range_bars)
    
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low
    print(opening_range_high, opening_range_low, opening_range)

    after_opening_range_mask = minute_bars.index > fifteen_min_bar
    after_opening_bars = minute_bars.loc[after_opening_range_mask]
    #print(after_opening_bars)
    after_opening_range_breakout = after_opening_bars[after_opening_bars['close'] > opening_range_high]
    if not after_opening_range_breakout.empty:
        print(after_opening_range_breakout)
        limit_price = after_opening_range_breakout.iloc[0]['close']
        print(limit_price)
        print(f"Placed order for {stock} at ${limit_price} at {after_opening_range_breakout.iloc[0].name}, with a range of +-{opening_range}.")



    