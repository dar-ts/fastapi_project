from typing import Annotated, Union

from fastapi import APIRouter, Depends, Response, HTTPException, status
from icecream import ic
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import IncomingSeller, ReturnedSeller
from src.configurations.database import get_async_session
from src.schemas import Token
from src.models.sellers import Seller

auth_router = APIRouter(tags=["auth"], prefix = "/token")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(session: DBSession, token: str = Depends(oauth2_scheme)) -> ReturnedSeller:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    users = await session.execute(select(Seller).filter_by(email=email))
    user = users.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def authenticate_user(email: str, password: str, session: DBSession):
    user = await session.execute(select(Seller).filter(Seller.email == email, Seller.password == password))
    return user.scalar()


@auth_router.post("/", response_model=Token)
async def login_for_access_token(session: DBSession, form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password

    user = await authenticate_user(email, password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await create_token({"sub": email})
    return {"access_token": token, "token_type": "bearer"}