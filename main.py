from fastapi import FastAPI
import sqlite3
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()

@app.get("/")
async def root():
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    cursor.execute("SELECT symbol FROM stock")
    rows = cursor.fetchall()
    return {"message": rows}
    
    #return {"message": "Home page"}

@app.get("/stocks")
async def stocks():
    return {"message": "Specific stocks"}


# @app.get("/stocks/{symbol}")
# async def stock(symbol):
#     return {"message": "Hello World"}

# @app.get("/stocks/{symbol}/bars")
# async def bars(symbol):
#     return {"message": "Hello World"}

# @app.get("/stocks/{symbol}/bars/{start}/{end}")
# async def bars(symbol, start, end):
#     return {"message": "Hello World"}

# @app.get("/stocks/{symbol}/bars/{start}/{end}/{timeframe}")
# async def bars(symbol, start, end, timeframe):
#     return {"message": "Hello World"}



