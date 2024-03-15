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
current_date_str = "2024-03-14"
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
        if stock[0] not in ordered_symbols:
            limit_price = after_opening_range_breakout.iloc[0]['close']
            print(f"Placing order for {stock} at ${limit_price} at {after_opening_range_breakout.iloc[0].name}, with a stop-loss of +-{opening_range}.")


        #submit paper order for testing
            paper_api.submit_order(
                symbol=stock[0],
                side='buy',
                type='limit',
                qty='1',
                time_in_force='day',
                limit_price=limit_price,
                order_class='bracket',
                stop_loss={'stop_price': limit_price - opening_range},
                take_profit={'limit_price': limit_price + opening_range}
            )
        
        else:
            print(f"Already an order for {stock}.")



    