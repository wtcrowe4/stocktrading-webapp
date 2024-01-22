from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import os
import dotenv

dotenv.load_dotenv()

db_url = os.getenv('DATABASE_URL')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    conn = sqlite3.connect(db_url)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock")
    rows = cursor.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows})
    
    

@app.get("/stocks")
async def stocks():
    return {"message": "Specific stocks"}


# @app.get("/stocks/{symbol}")
# async def stock(symbol):
#     return {"message": "Hello World"}

# @app.get("/stocks/{symbol}/bars")
# async def bars(symbol):
#     return {"message": "Hello World"}

# @app.get("/stocks/{symbol}/bars/{start}/{end}")
# async def bars(symbol, start, end):
#     return {"message": "Hello World"}

# @app.get("/stocks/{symbol}/bars/{start}/{end}/{timeframe}")
# async def bars(symbol, start, end, timeframe):
#     return {"message": "Hello World"}



