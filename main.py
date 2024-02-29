from typing import List
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# from fastapi_pagination import Page, add_pagination, paginate
import sqlite3
import os
import dotenv
from fastapi import APIRouter
# from models.Stock import Stock
# from models.Stock_Price import Stock_Price

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Stock data class with stock and stock price data
# class StockData:
#     def __init__(self, stock: Stock, stock_price: List[Stock_Price]):
#         self.stock = stock
#         self.stock_price = stock_price

# Home page
@app.get("/")   #, response_model=Page[StockData]
async def root(request: Request, page: str = '1', searchInput: str = None):  # -> Page[StockData]
    
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

    # Connect to the database
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    
    # Input from search bar
    searchInput = request.query_params.get('searchInput')
    if searchInput:
        print(searchInput)
        cursor.execute("SELECT * FROM stock WHERE symbol LIKE ? OR name LIKE ? ORDER BY symbol LIMIT 50", (f'%{searchInput}%', f'%{searchInput}%'))
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
            
        pages = len(stocks) // 50
        return templates.TemplateResponse("home.html", {"request": request, "stocks": stocks, "searchInput": searchInput, "pages": pages})

            
    
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

    pages = cursor.execute("SELECT COUNT(*) FROM stock").fetchone()[0] // 50

    return templates.TemplateResponse("home.html", {"request": request, 
                                                    "stocks": stocks, 
                                                    "searchInput": searchInput, 
                                                    "pages": pages})
    #return paginate(templates.TemplateResponse("home.html", {"request": request, "stocks": stocks, "searchInput": searchInput}))


    
#Page for individual stock data
# If visited, add this stock to a list of recently visited stocks
user_recent_stocks = [377, 5007, 5553, 6380, 105, 9312]
user_favorite_stocks = [377, 5007, 5553, 6380, 105, 9312] #6562,Berkshire Hathaway
@app.get("/stock/{symbol}")
async def stock_data(request: Request, symbol):
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


# Routes for favorite stocks
@app.post("/add_favorite/{stock_id}")
async def add_favorite_stock(stock_id: int):
    global user_favorite_stocks
    if stock_id not in user_favorite_stocks:
        user_favorite_stocks.append(stock_id)
        print("Added to favorites:", stock_id, user_favorite_stocks)    
    return {"message": "Stock added to favorites", "favorite_stocks": user_favorite_stocks}

@app.post("/remove_favorite/{stock_id}")
async def remove_favorite_stock(stock_id: int):
    global user_favorite_stocks
    if stock_id in user_favorite_stocks:
        user_favorite_stocks.remove(stock_id)
    return {"message": "Stock removed from favorites", "favorite_stocks": user_favorite_stocks}


    
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
async def recent_stocks(request: Request, user_recent_stocks=user_recent_stocks):
    #for user recent stocks array get the stock information and the latest stock prices
    user_recent_stocks = list(dict.fromkeys(user_recent_stocks))    
    print(user_recent_stocks)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stocks=[]
    # for stock_id in user_recent_stocks:
    #     cursor.execute("SELECT * FROM stock WHERE id=?", (stock_id,))
    #     row = cursor.fetchone()
    #     stocks.append(row)
    for stock_id in user_recent_stocks:
        cursor.execute("SELECT * FROM stock WHERE id=?", (stock_id,))
        stock = cursor.fetchone()
        stock_dict = dict(stock)
        cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC LIMIT 1", (stock_id,))
        price = cursor.fetchone()
        if price is not None:
            stock_dict['close'] = price['close']
            stock_dict['date'] = price['date']
            stock_dict['volume'] = price['volume']
            stock_dict['high'] = price['high']
            stock_dict['low'] = price['low']

        stocks.append(stock_dict)
    
    user_recent_symbols = [stock['symbol'] for stock in stocks]
    print(user_recent_symbols)
    
    return templates.TemplateResponse("recent.html", {"request": request, "stocks": stocks, "recent_symbols": user_recent_symbols})


#Page for Favorite Stocks
@app.get("/favorites")
async def favorite_stocks(request: Request, user_favorite_stocks=user_favorite_stocks):
    #for user favorite stocks array get the stock information and the latest stock prices
    user_favorite_stocks = list(dict.fromkeys(user_favorite_stocks))
    print(user_favorite_stocks)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stocks=[]
    for stock_id in user_favorite_stocks:
        cursor.execute("SELECT * FROM stock WHERE id=?", (stock_id,))
        stock = cursor.fetchone()
        stock_dict = dict(stock)
        cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC LIMIT 1", (stock_id,))
        price = cursor.fetchone()
        if price is not None:
            stock_dict['close'] = price['close']
            stock_dict['date'] = price['date']
            stock_dict['volume'] = price['volume']
            stock_dict['high'] = price['high']
            stock_dict['low'] = price['low']

        stocks.append(stock_dict)
    
    user_favorite_symbols = [stock['symbol'] for stock in stocks]
    print(user_favorite_symbols)
    print(stocks[0]['exchange'], stocks[0]['symbol'])
    return templates.TemplateResponse("favorites.html", {"request": request, "stocks": stocks, "favorite_symbols": user_favorite_symbols})


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

