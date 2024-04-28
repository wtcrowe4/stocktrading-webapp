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
router = APIRouter(tags=['intraday'])
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
#add_pagination(app)


# Connect to the database
conn = sqlite3.connect(db_url)
conn.row_factory = sqlite3.Row  
cursor = conn.cursor()



#Page for Intraday Highs
@router.get("/intraday_highs")
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
    header_title = "Intraday Highs"
    return templates.TemplateResponse("intraday.html", {"request": request, "stocks": rows, "header_txt": header_title})


#Page for Intraday Lows
@router.get("/intraday_lows")
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
    header_title = "Intraday Lows"
    return templates.TemplateResponse("intraday.html", {"request": request, "stocks": rows, "header_txt": header_title})

app.include_router(router, tags=['intraday'])