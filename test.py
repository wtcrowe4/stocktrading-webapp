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

api = tradeapi.REST(alpaca_api_key, alpaca_api_secret, base_url=alpaca_data_url)
#testing
#problem with symbol 'AAVE/USD'

testbars = api.get_bars(['AAVE/USD'], TimeFrame.Day, '2024-01-15', '2024-01-20', adjustment='raw').df
print(testbars)