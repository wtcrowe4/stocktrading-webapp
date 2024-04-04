from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/stock/{symbol}")
def stock_data(request: Request, symbol):
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
    print("recent", user_recent_stocks)

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

