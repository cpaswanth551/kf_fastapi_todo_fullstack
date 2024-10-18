from fastapi import status
from ..routers.todo import get_current_user, get_db
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todo/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "completed": False,
            "title": "Learn to code!",
            "description": "Need to learn everyday!",
            "id": 1,
            "priority": 5,
            "owner_id": 1,
        }
    ]


def test_read_todo_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "completed": False,
        "title": "Learn to code!",
        "description": "Need to learn everyday!",
        "id": 1,
        "priority": 5,
        "owner_id": 1,
    }


def test_read_todo_autenticated_notfound(test_todo):
    response = client.get("/todo/19")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "todo with id 19 not Found.."}


def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo!",
        "description": "New todo description",
        "priority": 5,
        "completed": False,
    }
    response = client.post("/todo/", json=request_data)

    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.completed == request_data.get("completed")


def test_update_todo(test_todo):

    request_data = {
        "title": "Change the title of the todo already saved!",
        "description": "Need to learn everyday!",
        "priority": 5,
        "completed": False,
    }

    response = client.put("/todo/1", json=request_data)

    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == "Change the title of the todo already saved!"


def test_update_todo_not_found(test_todo):

    request_data = {
        "title": "Change the title of the todo already saved!",
        "description": "Need to learn everyday!",
        "priority": 5,
        "completed": False,
    }

    response = client.put("/todo/144", json=request_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "todo not found"}


def test_delete_todo(test_todo):
    response = client.delete("/todo/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todo/1000")

    assert response.status_code == 404
    assert response.json() == {"detail": "todo not found"}
