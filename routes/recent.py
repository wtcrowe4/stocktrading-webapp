from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# from fastapi_pagination import Page, add_pagination, paginate
import sqlite3
import os
import dotenv
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
# from models.Stock import Stock
# from models.Stock_Price import Stock_Price
from urllib.parse import quote, unquote

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()


#Page for Recent Stocks
@app.get("/recent")
async def recent_stocks(request: Request, user_recent_stocks=user_recent_stocks):
    #for user recent stocks array get the stock information and the latest stock prices
    #user_recent_stocks = list(dict.fromkeys(user_recent_stocks))    
    print(user_recent_stocks)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stock_data=[]
    
    for stock in user_recent_stocks:
        print(stock)
        
        cursor.execute("""
            SELECT stock.*, stock_price.close, stock_price.date, stock_price.volume, stock_price.high, stock_price.low
            FROM stock
            JOIN stock_price ON stock.id = stock_price.stock_id
            WHERE stock.id IN (?, ?, ?, ?, ?, ?, ?, ?)
            ORDER BY stock_price.date DESC
        """, user_recent_stock_ids)
        rows = cursor.fetchall()

        stock_data = []
        for row in rows:
            stock_dict = dict(row)
            stock_data.append(stock_dict)
    
    user_recent_symbols = [stock['symbol'] for stock in user_recent_stocks]
    print(user_recent_symbols)
    
    return templates.TemplateResponse("recent.html", {"request": request, "stocks": user_recent_stocks, "stock_data": stock_data, "recent_symbols": user_recent_symbols})
