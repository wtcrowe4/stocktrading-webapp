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
                SELECT id from strategy where name = 'bollinger_band_breakout'
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

for stock in stocks:
    symbol = stock[0]
    name = stock[1]

    bars = api.get_barset(symbol, 'day', limit=20).df[symbol]
    last_close = bars['close'].iloc[-1]
    last_high = bars['high'].iloc[-1]
    last_low = bars['low'].iloc[-1]

    # Calculate Bollinger Bands
    sma = bars['close'].rolling(window=20).mean()
    std = bars['close'].rolling(window=20).std()
    upper_band = sma + 2 * std
    lower_band = sma - 2 * std

    if last_close > upper_band.iloc[-1] or last_close < lower_band.iloc[-1]:
        print(f"{symbol} is breaking outside of its Bollinger Bands")
        if symbol not in ordered_symbols:
            if last_close > upper_band.iloc[-1]:
                paper_api.submit_order(
                    symbol=symbol,
                    qty='1',
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Ordering 1 share of {symbol} at {last_close}")
            elif last_close < lower_band.iloc[-1]:
                paper_api.submit_order(
                    symbol=symbol,
                    qty='1',
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Selling 1 share of {symbol} at {last_close}")
    else:
        print(f"{symbol} is not breaking outside of its Bollinger Bands")
        