from typing import List
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import Page, add_pagination, paginate
import sqlite3
import os
import dotenv
from models.Stock import Stock
from models.Stock_Price import Stock_Price

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
add_pagination(app)

# Page = Page.with_custom_options(size=50)

# Stock data class with stock and stock price data
class StockData:
    def __init__(self, stock: Stock, stock_price: List[Stock_Price]):
        self.stock = stock
        self.stock_price = stock_price





@app.get("/", response_model=Page[StockData])
async def root(request: Request, page: str = '1', searchInput: str = None) -> Page[StockData]:
    
    # Pagination
    if page == 'prev_page':
        if int(page) > 1:
            page = int(page) - 1
            offset = (page - 1) * 50
    elif page == 'next_page':
        page = int(page) + 1
        offset = (page - 1) * 50
    else:
        page = int(page)
        offset = (page - 1) * 50
    
   

    

    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    
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

    return templates.TemplateResponse("home.html", {"request": request, "stocks": stocks, "searchInput": searchInput})
    #return paginate(templates.TemplateResponse("home.html", {"request": request, "stocks": stocks, "searchInput": searchInput}))


# Pagination
# @app.get("/{<int:page>}", response_model=Page[StockData])
# async def root(request: Request, page: int, searchInput: str = None) -> Page[StockData]:
#     page = int(page)
#     offset = (page - 1) * 50
   

    

#     conn = sqlite3.connect(db_url)
#     conn.row_factory = sqlite3.Row  
#     cursor = conn.cursor()
    
#     searchInput = request.query_params.get('search')
#     if searchInput:
        
#         cursor.execute("SELECT * FROM stock WHERE symbol LIKE ? ORDER BY symbol LIMIT 50", (f'%{searchInput}%',))
    
    
#     cursor.execute("SELECT * FROM stock ORDER BY symbol LIMIT 50 OFFSET ?", (offset,))
#     rows = cursor.fetchall()
    
#     #Get the most recent closing price for each stock to display on home page
#     cursor.execute("""
#         SELECT stock_id, close
#         FROM stock_price
#         WHERE (stock_id, date) IN (
#             SELECT stock_id, MAX(date)
#             FROM stock_price
#             GROUP BY stock_id
#         )
#     """)
#     recent_prices = cursor.fetchall()
#     recent_prices_dict = {row['stock_id']: row['close'] for row in recent_prices}
#     stocks = []
#     for stock in rows:
#         stock_dict = dict(stock)
#         stock_dict['recent_price'] = recent_prices_dict.get(stock_dict['id'], None)
#         if stock_dict['recent_price'] is not None:
#             stock_dict['recent_price'] = round(stock_dict['recent_price'], 2)
#         stock = stock_dict
#         stocks.append(stock)

#     return templates.TemplateResponse("home.html", {"request": request, "stocks": stocks, "searchInput": searchInput})




    
    
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
    user_recent_stocks = list(dict.fromkeys(user_recent_stocks))    
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


#Page for Closing Highs
@app.get("/closing_highs")
async def closing_highs(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, MAX(close) 
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY close DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    
    return templates.TemplateResponse("closing.html", {"request": request, "stocks": rows})


#Page for Closing Lows
@app.get("/closing_lows")
async def closing_lows(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, MIN(close) 
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY close ASC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    
    return templates.TemplateResponse("closing.html", {"request": request, "stocks": rows})













# Page for 404 not found errors
@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

