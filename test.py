import os
import dotenv
import sqlite3
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
import datetime

dotenv.load_dotenv()

alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_api_secret = os.getenv('ALPACA_API_SECRET')
alpaca_data_url = os.getenv('ALPACA_DATA_URL')
alpaca_base_url = os.getenv('ALPACA_BASE_URL')
db_url = os.getenv('DATABASE_URL')

conn = sqlite3.connect(db_url)

cursor = conn.cursor()

# api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_base_url)
# #testing
# #problem with symbol 'AAVE/USD'
# start_date = '2024-01-01'
# end_date = '2024-02-14'

# slash_assets = cursor.execute('SELECT symbol FROM stock WHERE symbol LIKE "%/%"').fetchall()
# print(slash_assets)

# for asset in slash_assets:
#     symbol = asset[0]
#     symbol = symbol.replace('/', '')
#     print(symbol)
#     bars = api.get_bars([symbol], TimeFrame.Day, start_date, end_date).df
#     print(bars)
    


# asset = api.get_asset('BATUSD')
# testbars = api.get_bars(['BATUSD'], TimeFrame.Day, start_date, end_date).df
# print(asset)
# print(testbars)

# Crytpo data
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

# Get all crypto stocks from database
crypto_assets = cursor.execute('SELECT symbol FROM stock WHERE exchange = "CRYPTO"').fetchall()
crypto_symbols = [asset[0] for asset in crypto_assets]
print(crypto_symbols)


client = CryptoHistoricalDataClient()
request_params = CryptoBarsRequest(
                        symbol_or_symbols=crypto_symbols,
                        timeframe=TimeFrame.Day,
                        start="2024-03-01T00:00:00Z",
                        end="2024-03-02T00:00:00Z"
                        )

bitcoin_bars = client.get_crypto_bars(request_params).df
print(bitcoin_bars)

#Convert data to store in database table stock_price
for symbol in crypto_symbols:
    bars = bitcoin_bars.loc[symbol]
    for index, row in bars.iterrows():
        print(index, row)
        day_timestamp_str = index.strftime('%Y-%m-%d')
        cursor.execute('''
                        INSERT INTO stock_price (stock_id, date, timestamp, open, high, low, close, volume)
                        VALUES ((SELECT id FROM stock WHERE symbol = ?), ?, ?, ?, ?, ?, ?, ?)
                        ''', (symbol, day_timestamp_str, str(index), row['open'], row['high'], row['low'], row['close'], row['volume']))
        







conn.commit()