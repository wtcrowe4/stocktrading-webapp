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
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()



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


    
    # Input from search bar
    searchInput = request.query_params.get('searchInput')
    if searchInput:
        print(searchInput)
        cursor.execute("SELECT * FROM stock WHERE symbol LIKE ? OR name LIKE ? ORDER BY symbol LIMIT 50", (f'%{searchInput}%', f'%{searchInput}%'))
        rows = cursor.fetchall()

        # Get the total count of stocks that match the search criteria
        cursor.execute("SELECT COUNT(*) FROM stock WHERE symbol LIKE ? OR name LIKE ?", (f'%{searchInput}%', f'%{searchInput}%'))
        total_stocks = cursor.fetchone()[0]
        pages = total_stocks // 50
        print(pages)
        
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
            
            
            #stock_dict['url_symbol'] = quote(stock_dict['symbol'], safe='')
            stock = stock_dict
            
            stocks.append(stock)
          
        
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
        
        #stock_dict['url_symbol'] = quote(stock_dict['symbol'], safe='')
             
        
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
user_recent_stock_ids = [10966, 377, 5007, 5553, 6380, 105, 9312, 6562]
user_recent_stocks = []
for id in user_recent_stock_ids:
    cursor.execute("SELECT * FROM stock WHERE id=?", (id,))
    stock = cursor.fetchone()
    user_recent_stocks.append(dict(stock))
    
user_favorite_stock_ids = [377, 5007, 5553, 6380, 9312] 
user_favorite_stocks = []
for id in user_favorite_stock_ids:
    cursor.execute("SELECT * FROM stock WHERE id=?", (id,))
    stock = cursor.fetchone()
    user_favorite_stocks.append(dict(stock))

@app.get("/stock/{symbol}")
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
@app.get("/stock/{symbol1}/{symbol2}")
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


# Routes for favorite stocks
@app.post("/add_favorite/{stock_id}")
async def add_favorite_stock(stock_id: int):
    global user_favorite_stocks
    stock = sqlite3.connect(db_url).cursor().execute("SELECT * FROM stock WHERE id=?", (stock_id,)).fetchone()
    if stock not in user_favorite_stocks:
        user_favorite_stocks.append(stock)
        print("Added to favorites:", stock, user_favorite_stocks)
    stock_symbol = sqlite3.connect(db_url).cursor().execute("SELECT symbol FROM stock WHERE id=?", (stock_id,)).fetchone()[0]
    url_symbol = quote(stock_symbol, safe='')
    #return {"message": "Stock added to favorites", "favorite_stocks": user_favorite_stocks}
    return RedirectResponse(url=f"/stock/{url_symbol}", status_code=303)

@app.post("/remove_favorite/{stock_id}")
async def remove_favorite_stock(stock_id: int):
    global user_favorite_stocks
    if stock_id in user_favorite_stocks:
        user_favorite_stocks.remove(stock_id)
        print("Removed from favorites:", stock_id, user_favorite_stocks)
    stock_symbol = sqlite3.connect(db_url).cursor().execute("SELECT symbol FROM stock WHERE id=?", (stock_id,)).fetchone()[0]
    url_symbol = quote(stock_symbol, safe='')
    #return {"message": "Stock removed from favorites", "favorite_stocks": user_favorite_stocks}
    return RedirectResponse(url=f"/stock/{url_symbol}", status_code=303)


#Route for strategies
@app.post("/add_strategy/{stock_id}")
async def add_strategy(request: Request, stock_id: int, strategy: int = Form(...)):
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)", (stock_id, strategy))
    conn.commit()
    stock_symbol = sqlite3.connect(db_url).cursor().execute("SELECT symbol FROM stock WHERE id=?", (stock_id,)).fetchone()[0]
    print("Added strategy", strategy, "to stock", stock_id)
    return RedirectResponse(url=f"/portfolio", status_code=303)
    



#Page for Popular Stocks
@app.get("/popular")
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

#Page for Recent Stocks
@app.get("/recent")
async def recent_stocks(request: Request, user_recent_stocks=user_recent_stocks):
    #for user recent stocks array get the stock information and the latest stock prices
    #user_recent_stocks = list(dict.fromkeys(user_recent_stocks))    
    print(user_recent_stocks)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stock_data=[]
    
    for stock in user_recent_stocks:
        print(stock)
        
        cursor.execute("""
            SELECT stock.*, stock_price.close, stock_price.date, stock_price.volume, stock_price.high, stock_price.low
            FROM stock
            JOIN stock_price ON stock.id = stock_price.stock_id
            WHERE stock.id IN (?, ?, ?, ?, ?, ?, ?, ?)
            ORDER BY stock_price.date DESC
        """, user_recent_stock_ids)
        rows = cursor.fetchall()

        stock_data = []
        for row in rows:
            stock_dict = dict(row)
            stock_data.append(stock_dict)
    
    user_recent_symbols = [stock['symbol'] for stock in user_recent_stocks]
    print(user_recent_symbols)
    
    return templates.TemplateResponse("recent.html", {"request": request, "stocks": user_recent_stocks, "stock_data": stock_data, "recent_symbols": user_recent_symbols})


#Page for Favorite Stocks
@app.get("/favorites")
async def favorite_stocks(request: Request, user_favorite_stocks=user_favorite_stocks):
    #for user favorite stocks array get the stock information and the latest stock prices
    #user_favorite_stocks = list(dict.fromkeys(user_favorite_stocks))
    print(user_favorite_stocks)
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stocks=[]
    # for stock_id in user_favorite_stocks:
    #     cursor.execute("SELECT * FROM stock WHERE id=?", (stock_id,))
    #     stock = cursor.fetchone()
    #     stock_dict = dict(stock)
    #     cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC LIMIT 1", (stock_id,))
    #     price = cursor.fetchone()
    #     if price is not None:
    #         stock_dict['close'] = price['close']
    #         stock_dict['date'] = price['date']
    #         stock_dict['volume'] = price['volume']
    #         stock_dict['high'] = price['high']
    #         stock_dict['low'] = price['low']

    #     stocks.append(stock_dict)
    
    user_favorite_symbols = [stock['symbol'] for stock in stocks]
    print(user_favorite_symbols)
    print(user_favorite_stocks[0]['exchange'], user_favorite_stocks[0]['symbol'])
    return templates.TemplateResponse("favorites.html", {"request": request, "stocks": user_favorite_stocks, "favorite_symbols": user_favorite_symbols})


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
        SELECT symbol, name, date, MAX(close) as close 
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY date DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    header_txt = "Closing Highs"
    
    return templates.TemplateResponse("closing.html", {"request": request, "stocks": rows, "header_txt": header_txt})


# Page for Closing Lows
@app.get("/closing_lows")
async def closing_lows(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, name, date, MIN(close) as close 
        FROM stock JOIN stock_price ON stock.id = stock_price.stock_id
        GROUP BY stock_id
        ORDER BY date DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    header_txt = "Closing Lows"
    
    return templates.TemplateResponse("closing.html", {"request": request, "stocks": rows, "header_txt": header_txt})



# Page for Portfolio/currently active strategies
@app.get("/portfolio")
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


    return templates.TemplateResponse("portfolio.html", {"request": request, "active_strategies": portfolio_list })






# Page for 404 not found errors
@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

