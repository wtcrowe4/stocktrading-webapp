from typing import List
from urllib import request
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


# from .routes import stock_data, popular, intraday, closing, recent, favorites, portfolio
from routes import stock_data_router, popular_router, intraday_router, closing_router, recent_router, favorites_router, portfolio_router

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
app.include_router(stock_data_router)
app.include_router(popular_router)
app.include_router(intraday_router)
app.include_router(closing_router)
app.include_router(recent_router)
app.include_router(favorites_router)
app.include_router(portfolio_router)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/styles", StaticFiles(directory="styles"), name="styles")
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()

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



# Splash page
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("splash.html", {"request": request})


# All page
@app.get("/all")   #, response_model=Page[StockData]
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
          
        
        return templates.TemplateResponse("all.html", {"request": request, "stocks": stocks, "searchInput": searchInput, "pages": pages})

            
    
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

    return templates.TemplateResponse("all.html", {"request": request, 
                                                    "stocks": stocks, 
                                                    "searchInput": searchInput, 
                                                    "pages": pages})
    #return paginate(templates.TemplateResponse("ho






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


# #Route for strategies
@app.post("/add_strategy/{stock_id}")
async def add_strategy(request: Request, stock_id: int, strategy: int = Form(...)):
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)", (stock_id, strategy))
    conn.commit()
    stock_symbol = sqlite3.connect(db_url).cursor().execute("SELECT symbol FROM stock WHERE id=?", (stock_id,)).fetchone()[0]
    print("Added strategy", strategy, "to stock", stock_id)
    return RedirectResponse(url=f"/portfolio", status_code=303)
    



# # Page for 404 not found errors
@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
