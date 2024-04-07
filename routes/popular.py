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

router = APIRouter(tags=['popular'])
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()





@router.get("/popular")
async def popular_stocks(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, volume, url_symbol
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        GROUP BY volume
        ORDER BY volume DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()

    # Add a url_symbol key to each stock dictionary
    stocks=[]
    for stock in rows:
        stock = dict(stock)
        #stock['url_symbol'] = quote(stock['symbol'], safe='')
        stocks.append(stock)
        

    
    return templates.TemplateResponse("popular.html", {"request": request, "stocks": stocks})