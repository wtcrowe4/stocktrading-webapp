from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import sqlite3
import os
import dotenv
from fastapi import APIRouter

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

router = APIRouter(tags=['favorites'])
templates = Jinja2Templates(directory="templates")

# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()


#Page for Favorite Stocks
@router.get("/favorites")
async def favorite_stocks(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get Favorite Stocks
    user_favorite_stocks = []
    user_favorite_symbols = []
    user_favorite_stock_ids = []

    cursor.execute("""SELECT stock_id FROM favorite_stock""")
    rows = cursor.fetchall()
    for row in rows:
        user_favorite_stock_ids.append(row['stock_id'])

    cursor.execute('SELECT * from favorite_stock')
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute("""SELECT symbol from stock where id=?""", (row['stock_id'],))
        symbol = cursor.fetchone()
        user_favorite_symbols.append(symbol['symbol'])
        
        # cursor.execute("""SELECT stock_id from favorite_stock""")
        # stock_id = cursor.fetchone()
        # user_favorite_stock_ids.append(stock_id['stock_id'])

        cursor.execute("""SELECT * FROM stock WHERE id=?""", (row['stock_id'],))
        stock = cursor.fetchone()  
        user_favorite_stocks.append(dict(stock))


    
    
    stock_data = []
    for stock_id in user_favorite_stock_ids:
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

    
    user_favorite_symbols.pop()
    print(user_favorite_symbols)
    
    return templates.TemplateResponse("favorites.html", {"request": request, "stock_data": stock_data, "stocks": user_favorite_stocks, "favorite_symbols": user_favorite_symbols})
