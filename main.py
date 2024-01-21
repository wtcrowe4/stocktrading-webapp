from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Home page"}

@app.get("/stocks")
async def stocks():
    return {"message": "Specific stock"}


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



