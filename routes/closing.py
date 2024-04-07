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

router = APIRouter(tags=['closing'])
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()


#Page for Closing Highs
@router.get("/closing_highs")
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
@router.get("/closing_lows")
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