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

router = APIRouter(tags=['portfolio'])
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

# Page for Portfolio/currently active strategies
@router.get("/portfolio")
async def portfolio(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock_strategy")
    active_strategies = cursor.fetchall()
    portfolio_list = []
    for strategy in active_strategies:
        stock = cursor.execute("SELECT * FROM stock WHERE id=?", (strategy['stock_id'],)).fetchone()
        stock_price = cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC LIMIT 1", (stock['id'],)).fetchone()
        strategy_info = cursor.execute("SELECT * FROM strategy WHERE id=?", (strategy['strategy_id'],)).fetchone()

        portfolio_dict = {
            'stock': stock,
            'stock_price': stock_price,
            'name': stock['name'],
            'symbol': stock['symbol'],
            'exchange': stock['exchange'],
            'strategy': strategy_info,
            'viewable_name': strategy_info['viewable_name']
        }
        portfolio_list.append(portfolio_dict)

    print(portfolio_list)


    return templates.TemplateResponse("portfolio.html", {"request": request, "portfolio": portfolio_list})