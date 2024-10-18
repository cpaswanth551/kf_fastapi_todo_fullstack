from fastapi import Depends, APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from ..models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed!"
        )

    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed!"
        )

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"todo not found",
        )

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
