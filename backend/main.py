from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .models import Base
from .database import engine
from .routers import admin, auth, todo, user

app = FastAPI()


Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="backend/static"), name="static")


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


@app.get("/")
def index(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(user.router)
