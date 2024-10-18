from fastapi import Depends, APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext

from ..database import get_db
from ..models import Users
from .auth import get_current_user, bcryt_content


router = APIRouter(prefix="/user", tags=["Users"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get("")
async def read_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed"
        )

    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.post("/password/", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    db: db_dependency, user: user_dependency, user_verification: UserVerification
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed"
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcryt_content.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")

    user_model.hashed_password = bcryt_content.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.post("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    db: db_dependency, user: user_dependency, phone_number: str
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed.."
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
