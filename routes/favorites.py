from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
#from fastapi.staticfiles import StaticFiles
# from fastapi_pagination import Page, add_pagination, paginate
import sqlite3
import os
import dotenv
from fastapi import APIRouter
#from fastapi.responses import RedirectResponse
# from models.Stock import Stock
# from models.Stock_Price import Stock_Price
#from urllib.parse import quote, unquote

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

router = APIRouter(tags=['favorites'])
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()

# Get Recent/Favorites
# user_recent_stocks = []

# cursor.execute("SELECT * FROM recent_stock;")
# rows = cursor.fetchall()
# for row in rows:
#     cursor.execute("SELECT * FROM stock WHERE id=?", (row['stock_id'],))
#     stock = cursor.fetchone()
#     user_recent_stocks.append(stock)




#Page for Favorite Stocks

@router.get("/favorites")
async def favorite_stocks(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get Favorite Stocks
    user_favorite_stocks = []
    user_favorite_symbols = []
    user_favorite_stock_ids = []

    cursor.execute("""SELECT stock_id FROM favorite_stock""")
    rows = cursor.fetchall()
    for row in rows:
        user_favorite_stock_ids.append(row['stock_id'])

    print(user_favorite_stock_ids)


    cursor.execute('SELECT * from favorite_stock')
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute("""SELECT symbol from stock where id=?""", (row['stock_id'],))
        symbol = cursor.fetchone()
        user_favorite_symbols.append(symbol['symbol'])
        
        # cursor.execute("""SELECT stock_id from favorite_stock""")
        # stock_id = cursor.fetchone()
        # user_favorite_stock_ids.append(stock_id['stock_id'])

        cursor.execute("""SELECT * FROM stock WHERE id=?""", (row['stock_id'],))
        stock = cursor.fetchone()  
        user_favorite_stocks.append(dict(stock))


    
    
    stock_data = []
    for stock_id in user_favorite_stock_ids:
        cursor.execute("""
            SELECT * FROM stock 
            JOIN stock_price ON stock.id = stock_price.stock_id
            WHERE stock.id = ?
            ORDER BY stock_price.date DESC
            LIMIT 1;
        """, (stock_id,))
        row = cursor.fetchone()
        
        if row:
            stock_dict = dict(row)
            stock_data.append(stock_dict)

    






# @router.get("/favorites")
# async def favorite_stocks(request: Request):
#     user_favorite_stocks = []
#     user_favorite_symbols = []
#     user_favorite_stock_ids = []

#     cursor.execute("SELECT * FROM favorite_stock;")
#     rows = cursor.fetchall()
#     for row in rows:
#         cursor.execute("SELECT * FROM stock WHERE id=?", (row['stock_id'],))
#         stock = cursor.fetchone()
#         user_favorite_stocks.append(stock)


#     cursor.execute('SELECT * from favorite_stock')
#     rows = cursor.fetchall()
#     for row in rows:
#         cursor.execute("""SELECT symbol from stock where id=?""", (row['stock_id'],))
#         symbol = cursor.fetchone()
#         user_favorite_symbols.append(symbol)
#         cursor.execute("""SELECT stock_id from favorite_stock""")
#         stock_id = cursor.fetchone()
#         user_favorite_stock_ids.append(stock_id)

#     stock_data = []
#     for stock_id in user_favorite_stock_ids:
#         cursor.execute("""
#             SELECT * FROM stock 
#             JOIN stock_price ON stock.id = stock_price.stock_id
#             WHERE stock.id = ?
#             ORDER BY stock_price.date DESC
#             LIMIT 1;
#         """, (stock_id,))
#         row = cursor.fetchone()
        
#         if row:
#             stock_dict = dict(row)
#             stock_data.append(stock_dict)





    #for user favorite stocks array get the stock information and the latest stock prices
    #user_favorite_stocks = list(dict.fromkeys(user_favorite_stocks))
    # print(user_favorite_stocks)
    # conn = sqlite3.connect(db_url)
    # conn.row_factory = sqlite3.Row
    # cursor = conn.cursor()
    # stocks=[]
    # # for stock_id in user_favorite_stocks:
    # #     cursor.execute("SELECT * FROM stock WHERE id=?", (stock_id,))
    # #     stock = cursor.fetchone()
    # #     stock_dict = dict(stock)
    # #     cursor.execute("SELECT * FROM stock_price WHERE stock_id=? ORDER BY date DESC LIMIT 1", (stock_id,))
    # #     price = cursor.fetchone()
    # #     if price is not None:
    # #         stock_dict['close'] = price['close']
    # #         stock_dict['date'] = price['date']
    # #         stock_dict['volume'] = price['volume']
    # #         stock_dict['high'] = price['high']
    # #         stock_dict['low'] = price['low']

    # #     stocks.append(stock_dict)
    
    # user_favorite_symbols = [stock['symbol'] for stock in stocks]
    # print(user_favorite_symbols)
    # print(user_favorite_stocks[0]['exchange'], user_favorite_stocks[0]['symbol'])
    return templates.TemplateResponse("favorites.html", {"request": request, "stock_data": stock_data, "stocks": user_favorite_stocks, "favorite_symbols": user_favorite_symbols})
