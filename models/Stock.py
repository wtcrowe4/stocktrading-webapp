from pydantic import BaseModel


class Stock (BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str
    class Config:
        orm_mode = True