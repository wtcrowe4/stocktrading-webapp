from sqlite3 import Date
from pydantic import BaseModel


class Stock_Price(BaseModel):
    id: int
    stock_id: int
    date: Date
    open: float
    high: float
    low: float
    close: float
    volume: int

    class Config:
        orm_mode = True