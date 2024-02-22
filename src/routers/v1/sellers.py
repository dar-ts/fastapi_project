from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedSeller, ReturnedSellerBooks, ReturnedAllSellers

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Ручка для регистрации продавца
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def register_seller(seller: IncomingSeller, session: DBSession):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password,
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка для получения списка всех продавцов (без пароля)
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.unique().scalars().all()
    return {"sellers": sellers}


# Ручка для получения данных о конкретном продавце (без пароля) с книгами
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerBooks)
async def get_seller(seller_id: int, session: DBSession):
    seller = await session.get(Seller, seller_id)
    return seller
   

# Ручка для обновления данных о продавце (без обновления книг и пароля)
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления данных о продавце. Удаляются также все его книги.
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)
    if deleted_seller:
        for book in deleted_seller.books:
            await session.delete(book)

        await session.delete(deleted_seller)
        #await session.flush()

    return Response(status_code=status.HTTP_204_NO_CONTENT)