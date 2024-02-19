from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request, page: int = 0, searchInput: str = None):
    #dropdown filter
    stock_filter = request.query_params.get('filter', None)
    if stock_filter == 'new_intraday_highs':
        conn = sqlite3.connect(db_url)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT stock_id, MAX(high) as high
            FROM stock_price
            WHERE date = (SELECT MAX(date) FROM stock_price)
            GROUP BY stock_id
            ORDER BY date DESC
            LIMIT 50
        """)
        recent_highs = cursor.fetchall()
        recent_highs_dict = {row['stock_id']: row['high'] for row in recent_highs}
        cursor.execute("SELECT * FROM stock WHERE id IN ({})".format(','.join(str(row['stock_id']) for row in recent_highs)))
        rows = cursor.fetchall()
        stocks = []
        for stock in rows:
            stock_dict = dict(stock)
            stock_dict['recent_high'] = recent_highs_dict.get(stock_dict['id'], None)
            if stock_dict['recent_high'] is not None:
                stock_dict['recent_high'] = round(stock_dict['recent_high'], 2)
            stock = stock_dict
            stocks.append(stock)
            
        return templates.TemplateResponse("home.html", {"request": request, "stocks": stocks})          
    #pagination
    # Get the 'page' query parameter
    # page = request.query_params.get('page', 0)
    # try:
    #     page = int(page)
    # except ValueError:
    #     page = 0

    # Calculate the offset for the database query
    offset = page * 50


    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    offset = page * 50
    
    if searchInput:
        
        cursor.execute("SELECT * FROM stock WHERE symbol LIKE ? ORDER BY symbol LIMIT 50", (f'%{searchInput}%',))
    
    
    cursor.execute("SELECT * FROM stock ORDER BY symbol LIMIT 50 OFFSET ?", (offset,))
    rows = cursor.fetchall()
    
    #Get the most recent closing price for each stock to display on home page
    cursor.execute("""
        SELECT stock_id, close
        FROM stock_price
        WHERE (stock_id, date) IN (
            SELECT stock_id, MAX(date)
            FROM stock_price
            GROUP BY stock_id
        )
    """)
    recent_prices = cursor.fetchall()
    recent_prices_dict = {row['stock_id']: row['close'] for row in recent_prices}
    stocks = []
    for stock in rows:
        stock_dict = dict(stock)
        stock_dict['recent_price'] = recent_prices_dict.get(stock_dict['id'], None)
        if stock_dict['recent_price'] is not None:
            stock_dict['recent_price'] = round(stock_dict['recent_price'], 2)
        stock = stock_dict
        stocks.append(stock)

    return templates.TemplateResponse("home.html", {"request": request, "stocks": stocks})
    
    

@app.get("/stock/{symbol}")
async def stock_data(request: Request, symbol):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock WHERE symbol=?", (symbol,))
    row = cursor.fetchone()
    print(row['id'])
    cursor.execute("SELECT * FROM stock_price WHERE stock_id=?", (row['id'],))
    prices = cursor.fetchall()
    
    return templates.TemplateResponse("stock_data.html", {"request": request, "prices": prices, "stock": row})

    






