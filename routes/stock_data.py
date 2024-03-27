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
router = APIRouter()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()

# Get Recent/Favorites
user_recent_stocks = []
user_favorite_stocks = []


cursor.execute("SELECT * FROM favorite_stock;")
rows = cursor.fetchall()
for row in rows:
    cursor.execute("SELECT * FROM stock WHERE id=?", (row['stock_id'],))
    stock = cursor.fetchone()
    user_favorite_stocks.append(stock)

cursor.execute("SELECT * FROM recent_stock;")
rows = cursor.fetchall()
for row in rows:
    cursor.execute("SELECT * FROM stock WHERE id=?", (row['stock_id'],))
    stock = cursor.fetchone()
    user_recent_stocks.append(stock)



@router.get("/stock/{symbol}")
async def stock_data(request: Request, symbol):
    print("url_symbol", symbol)
    symbol = unquote(symbol)
    print(symbol)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    print(row['id'])
    cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC", (row['id'],))
    prices = cursor.fetchall()
    
   
    #recently visited stocks
    if row['id'] not in user_recent_stocks:
        user_recent_stocks.insert(0, row['id'])
    if len(user_recent_stocks) > 40:
        user_recent_stocks.pop()
    print("recent",user_recent_stocks)

    #favorite stocks
    print("favorites", user_favorite_stocks)

    #strategies
    cursor.execute("SELECT * FROM strategy")
    strategies = cursor.fetchall()

    return templates.TemplateResponse("stock_data.html", {"request": request, 
                                                          "prices": prices, 
                                                          "stock": row,
                                                          "recent_stocks": user_recent_stocks,
                                                          "favorite_stocks": user_favorite_stocks,
                                                          "strategies": strategies})


# @app.get("/stock/{url_symbol}")
# async def stock_data(request: Request, url_symbol):
#     print("url_symbol", url_symbol)
#     symbol = unquote(url_symbol)
#     print(symbol)
#     conn = sqlite3.connect(db_url)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM stock WHERE symbol=?", (symbol,))
#     row = cursor.fetchone()
#     if row is None:
#         return templates.TemplateResponse("404.html", {"request": request})
#     cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC", (row['id'],))
#     prices = cursor.fetchall()
    
#     #recently visited stocks
#     if row['id'] not in user_recent_stocks:
#         user_recent_stocks.insert(0, row['id'])
#     if len(user_recent_stocks) > 40:
#         user_recent_stocks.pop()
#     print("recent",user_recent_stocks)

#     #favorite stocks
#     print("favorites", user_favorite_stocks)

#     #strategies
#     cursor.execute("SELECT * FROM strategy")
#     strategies = cursor.fetchall()

#     return templates.TemplateResponse("stock_data.html", {"request": request, 
#                                                           "prices": prices, 
#                                                           "stock": row,
#                                                           "recent_stocks": user_recent_stocks,
#                                                           "favorite_stocks": user_favorite_stocks,
#                                                           "strategies": strategies})


# Pages for bitcoin assets with a slash in the symbol
@router.get("/stock/{symbol1}/{symbol2}")
async def stock_data(request: Request, symbol1, symbol2):
    
    symbol = symbol1 + '/' + symbol2
    print(symbol)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    print(row['id'])
    cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC", (row['id'],))
    prices = cursor.fetchall()
    
    #recently visited stocks
    if row['id'] not in user_recent_stocks:
        user_recent_stocks.insert(0, row['id'])
    if len(user_recent_stocks) > 40:
        user_recent_stocks.pop()
    print("recent",user_recent_stocks)

    #favorite stocks
    print("favorites", user_favorite_stocks)

    #strategies
    cursor.execute("SELECT * FROM strategy")
    strategies = cursor.fetchall()

    return templates.TemplateResponse("stock_data.html", {"request": request, 
                                                          "prices": prices, 
                                                          "stock": row,
                                                          "recent_stocks": user_recent_stocks,
                                                          "favorite_stocks": user_favorite_stocks,
                                                          "strategies": strategies})

app.include_router(router, tags=['stock_data'])