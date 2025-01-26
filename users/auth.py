from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, status, Request, WebSocket
from users.utils import user as UserClass, usertype
from typing import Literal, Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY") # run `openssl rand -hex 32`
ALGORITHM = os.getenv("ALGORITHM")
VERSION = os.getenv("VERSION")

users_router = APIRouter()


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)

oath2_bearer = CustomOAuth2PasswordBearer(tokenUrl="/api/{version}/auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str
    
    

async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : str = payload.get("sub")
        is_employee: bool = payload.get("employee")
        is_customer: bool = payload.get("customer")
        if id is None or is_employee is None or is_customer is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"id": id, "is_employee": is_employee, "is_customer": is_customer}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@users_router.post("/register")
async def create_user(name: str, password: str, role: Literal["CUSTOMER", "EMPLOYEE"] = "CUSTOMER"):
    if role == "CUSTOMER":
        role = usertype.CUSTOMER
    elif role == "EMPLOYEE":
        role = usertype.EMPLOYEE
    return UserClass.create_user(name, password, role)


@users_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return UserClass.authenticate_user(form_data.username, form_data.password)
    
    

    

