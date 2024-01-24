from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock")
    rows = cursor.fetchall()
    

    
    
    
    
    
    
    
    
    
    # Get the most recent closing price for each stock to display on home page
    # cursor.execute("""
    #     SELECT stock_id, close
    #     FROM stock_price
    #     WHERE (stock_id, date) IN (
    #         SELECT stock_id, MAX(date)
    #         FROM stock_price
    #         GROUP BY stock_id
    #     )
    # """)
    # recent_prices = cursor.fetchall()



    # recent_prices_dict = {row['stock_id']: row['close'] for row in recent_prices}

    # for stock in rows:
    #     stock_dict = dict(stock)
    #     stock_dict['recent_price'] = recent_prices_dict.get(stock_dict['id'], None)
    
    #     if stock_dict['recent_price'] is not None:
    #         stock_dict['recent_price'] = round(stock_dict['recent_price'], 2)
    
        
    
    #     stock = stock_dict
        
        #print(stock['recent_price'])
   

        
            
        

    
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows})
    
    

@app.get("/stock/{symbol}")
async def stock_data(request: Request, symbol):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    
    cursor.execute("SELECT * FROM stock_price WHERE stock_id=?", (row['id'],))
    prices = cursor.fetchall()
    
    return templates.TemplateResponse("stock_data.html", {"request": request, "prices": prices, "stock": row})

    


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



