from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from fastapi_pagination import Page, add_pagination, paginate
import sqlite3
import os
import dotenv
from fastapi import APIRouter
# from fastapi.responses import RedirectResponse
# from models.Stock import Stock
# from models.Stock_Price import Stock_Price
# from urllib.parse import quote, unquote

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

router = APIRouter(tags=['recent'])
templates = Jinja2Templates(directory="templates")

# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()


# Get Recent/Favorites
user_recent_stocks = []
user_favorite_stocks = []
user_recent_symbols = []
user_favorite_symbols = []
recents_dict = []
favorites_dict = []


# Get Recent Stock IDs
user_recent_stock_ids = [stock['stock_id'] for stock in user_recent_stocks]
user_favorite_stock_ids = [stock['stock_id'] for stock in user_favorite_stocks]




@router.get("/recent")
async def recent_stocks(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get Recent/Favorites
    user_recent_stocks = []
    user_favorite_stocks = []
    recents_dict = {}
    favorites_dict = {}

    cursor.execute("SELECT * FROM favorite_stock;")
    rows = cursor.fetchall()
    for row in rows:
        favorites_dict = dict(row)
        user_favorite_stocks.append(row)

    cursor.execute("SELECT * FROM recent_stock;")
    rows = cursor.fetchall()
    for row in rows:
        recents_dict = dict(row)
        user_recent_stocks.append(row)

    # Get Recent Stock IDs
    user_recent_stock_ids = [stock['stock_id'] for stock in user_recent_stocks]
    user_favorite_stock_ids = [stock['stock_id'] for stock in user_favorite_stocks]

    stocks = []
    symbols = []
    for id in user_recent_stock_ids:
        cursor.execute('SELECT * FROM stock WHERE id = ?', (id,))
        stocks.extend([dict(row) for row in cursor.fetchall()])
        cursor.execute('SELECT symbol FROM stock WHERE id = ?', (id,))
        symbols.extend([row['symbol'] for row in cursor.fetchall()])


    stock_data = []
    for stock_id in user_recent_stock_ids:
        cursor.execute("""
        SELECT * FROM stock 
        JOIN stock_price ON stock.id = stock_price.stock_id
        WHERE stock.id = ?
        ORDER BY stock_price.date DESC
        LIMIT 1;
        """, (stock_id,))
        row = cursor.fetchone()
        
        if row:
            stock_dict = dict(row)
            stock_data.append(stock_dict)
         
        

    return templates.TemplateResponse("recent.html", {"request": request, "stocks": stocks, "stock_data": stock_data, "recent_symbols": symbols})
