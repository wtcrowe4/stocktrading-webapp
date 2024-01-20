import os 
import dotenv
import sqlite3

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

conn = sqlite3.connect(db_url)

cursor = conn.cursor()

cursor.execute('''
    DROP TABLE stock_price
''')    

cursor.execute('''
    DROP TABLE stock
''')

conn.commit()

