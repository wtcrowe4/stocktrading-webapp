#Route for individual stock data
# from .stock import *

# Path: routes/__init__.py
# Compare this snippet from routes/stock_data.py:

import sqlite3
from urllib.parse import unquote
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
router = APIRouter()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")

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


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_data(request: Request, symbol):
    print("url_symbol", symbol)
    symbol = unquote(symbol)
    print(symbol)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    return templates.TemplateResponse("stock.html", {"request": request, "stock": row})


app.include_router(router)
