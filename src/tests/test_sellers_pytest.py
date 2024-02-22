import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


@pytest.mark.asyncio
async def test_register_seller(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Popov",
        "email": "popov@yandex.ru",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert "id" in result_data
    assert result_data["first_name"] == "Ivan"
    assert result_data["last_name"] == "Popov"
    assert result_data["email"] == "popov@yandex.ru"
    assert "password" not in result_data 


@pytest.mark.asyncio
async def test_get_all_sellers(db_session, async_client):

    seller = sellers.Seller(first_name= "Ivan",
        last_name ="Popov",
        email = "popov@yandex.ru",
        password =" password123")
    seller_2 = sellers.Seller(first_name=  "Maria",
        last_name = "Ivanova",
        email = "ivanova@mail.ru",
        password =" password456")

    db_session.add_all([seller, seller_2])
    await db_session.flush()


    response = await async_client.get("/api/v1/sellers/")
    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()
    assert "sellers" in result_data
    assert len(result_data["sellers"]) == 2

    expected_result = [
        {
            "first_name": "Maria",
            "last_name": "Ivanova",
            "email": "ivanova@mail.ru",
            "id": seller_2.id
        },
        {
            "first_name": "Ivan",
            "last_name": "Popov",
            "email": "popov@yandex.ru",
            "id": seller.id
        }
    ]

    assert result_data["sellers"] == expected_result

@pytest.mark.asyncio
async def test_get_seller(db_session, async_client):
    seller_data = {
        "first_name": "Ivan",
        "last_name": "Popov",
        "email": "popov@yandex.ru",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/sellers/", json=seller_data)
    seller_id = response.json()["id"]
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id = 1)

    db_session.add(book)
    await db_session.flush()
    response = await async_client.get(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()


    assert "id" in result_data
    assert result_data["first_name"] == "Ivan"
    assert result_data["last_name"] == "Popov"
    assert result_data["email"] == "popov@yandex.ru"
    assert result_data["books"] ==[{
        "id": 1,
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "count_pages": 104,
        "year": 2001,
        "seller_id":1
    }
]

    assert "password" not in result_data  

@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(first_name= "Ivan",
        last_name ="Popov",
        email = "popov@yandex.ru",
        password =" password123")
    db_session.add(seller)
    await db_session.flush()

    
    updated_data = {
        "first_name": "Updated",
        "last_name": "Seller",
        "email": "updated@yandex.ru",
        "id": seller.id
    }
    response = await async_client.put(f"/api/v1/sellers/{seller.id}", json=updated_data)

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    assert "id" in result_data
    assert result_data["first_name"] == "Updated"
    assert result_data["last_name"] == "Seller"
    assert result_data["email"] == "updated@yandex.ru"
    assert "password" not in result_data  

@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = {
    "first_name": "Ivan",
    "last_name": "Popov",
    "email": "popov@yandex.ru",
    "password": "password123"
}
    response= await async_client.post("/api/v1/sellers/", json=seller)
    seller_id = response.json()["id"]
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id = seller_id)

    db_session.add(book)
    await db_session.flush()
    

    response = await async_client.delete(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()
    all_sellers = await db_session.execute(select(sellers.Seller))
    assert len(all_sellers.unique().scalars().all()) == 0

    all_books = await db_session.execute(select(books.Book))
    assert len(all_books.scalars().all()) == 0

