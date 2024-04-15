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

router = APIRouter(tags=['recent'])
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


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

# cursor.execute("SELECT * FROM favorite_stock;")
# rows = cursor.fetchall()
# for row in rows:
#     recents_dict = dict(row)
#     print(recents_dict)
#     #user_favorite_stocks.append(recents_dict)
#     #user_favorite_symbols.append(recents_dict['symbol'])


cursor.execute("SELECT * FROM recent_stock;")
rows = cursor.fetchall()
for row in rows:
    # user_recent_stocks.append(row)
    stock_dict = dict(row)

    favorites_dict.append(stock_dict)
    print(favorites_dict)
    #user_recent_stocks.append(favorites_dict)
    #user_recent_symbols.append(favorites_dict['symbol'])

    



# Get Recent Stock IDs
user_recent_stock_ids = [stock['stock_id'] for stock in user_recent_stocks]
user_favorite_stock_ids = [stock['stock_id'] for stock in user_favorite_stocks]



#Page for Recent Stocks
# @router.get("/recent")
# async def recent_stocks(request: Request, user_recent_stocks=user_recent_stocks):
#     #for user recent stocks array get the stock information and the latest stock prices
#     #user_recent_stocks = list(dict.fromkeys(user_recent_stocks))    
#     print(user_recent_stocks)
#     conn = sqlite3.connect(db_url)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     stock_data=[]
    
#     for stock in user_recent_stock_ids:
#         cursor.execute("""
#         SELECT * FROM stock WHERE id = ?
#         JOIN stock_price ON stock.id = stock_price.stock_id
#         ORDER BY stock_price.date DESC
#         LIMIT 1;
            
#         """, (stock,))
#         row = cursor.fetchone()
#         if row:
#             stock_dict = dict(row)
#             stock_data.append(stock_dict)
        
#         rows = cursor.fetchall()

#         stock_data = []
#         for row in rows:
#             stock_dict = dict(row)
#             stock_data.append(stock_dict)

        
        
    
    
#     user_recent_symbols = []
#     for stock in user_recent_stocks:
#         cursor.execute("SELECT symbol FROM stock WHERE id = ?", (stock,))
#         rows = cursor.fetchall()
#         for row in rows:
#             user_recent_symbols.append(row['symbol'])
    
#     print(user_recent_symbols)
    
#     return templates.TemplateResponse("recent.html", {"request": request, "stocks": user_recent_stocks, "stock_data": stock_data, "recent_symbols": user_recent_symbols})

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

    return templates.TemplateResponse("recent.html", {"request": request, "stocks": user_recent_stocks, "stock_data": stock_data})
