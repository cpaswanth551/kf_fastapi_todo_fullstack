from fastapi import Depends, APIRouter, HTTPException, Path, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.templating import Jinja2Templates

from ..database import get_db
from ..models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/todo", tags=["Todos"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory="backend/templates")


def redirect_to_login():
    redirect_response = RedirectResponse(
        url="/auth/login-page", status_code=status.HTTP_302_FOUND
    )
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


### pages #####


@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse(
            "todo.html", {"request": request, "todos": todos, "user": user}
        )

    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(
            "add_todo.html", {"request": request, "user": user}
        )

    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse(
            "edit-todo.html", {"request": request, "todo": todo, "user": user}
        )

    except:
        return redirect_to_login()


### Endpoints #####


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool


@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}")
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"todo with id {todo_id} not Found..",
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed.."
        )
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed.."
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed
    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentication Failed.."
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
