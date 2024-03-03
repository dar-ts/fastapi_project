from pydantic import BaseModel, Field
from .books import ReturnedBook
__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedSellerBooks", "ReturnedAllSellers"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


class IncomingSeller(BaseSeller):
    password: str


class ReturnedSeller(BaseSeller):
    id: int

class ReturnedSellerBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
