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
          
    #pagination
    
    

    # Calculate the offset for the database query
    offset = page * 50


    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    offset = page * 50
    searchInput = request.query_params.get('search')
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
    
    
#Page for individual stock data
# If visited, add this stock to a list of recently visited stocks
# If the stock is already in the list, move it to the top
# If the list is longer than 20, remove the oldest stock
user_recent_stocks = []
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
    
    #recently visited stocks
    user_recent_stocks.insert(0, row['id'])
    if len(user_recent_stocks) > 20:
        user_recent_stocks.pop()
    print(user_recent_stocks)

    return templates.TemplateResponse("stock_data.html", {"request": request, "prices": prices, "stock": row})

    
#Page for Popular Stocks
@app.get("/popular")
async def popular_stocks(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, volume
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        GROUP BY volume
        ORDER BY volume DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    
    return templates.TemplateResponse("popular.html", {"request": request, "stocks": rows, })

#Page for Recent Stocks
@app.get("/recent")
async def recent_stocks(request: Request):
    #for user recent stocks array get the stock information and the latest stock prices
    print(user_recent_stocks)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stocks=[]
    for stock_id in user_recent_stocks:
        cursor.execute("SELECT * FROM stock WHERE id=?", (stock_id,))
        row = cursor.fetchone()
        stocks.append(row)
    recent_prices = []
    for stock_id in user_recent_stocks:
        cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC LIMIT 1", (stock_id,))
        row = cursor.fetchone()
        recent_prices.append(row)

    
    return templates.TemplateResponse("recent.html", {"request": request, "stocks": stocks, "prices": recent_prices})


#Page for Intraday Highs
@app.get("/intraday_highs")
async def intraday_highs(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, high
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        WHERE date = (SELECT MAX(date) FROM stock_price)
        ORDER BY high DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    return templates.TemplateResponse("intraday.html", {"request": request, "stocks": rows})


#Page for Intraday Lows
@app.get("/intraday_lows")
async def intraday_lows(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, low
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        WHERE date = (SELECT MAX(date) FROM stock_price)
        ORDER BY low ASC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    
    return templates.TemplateResponse("intraday.html", {"request": request, "stocks": rows})


