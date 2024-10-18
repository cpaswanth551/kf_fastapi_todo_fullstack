from ..routers.admin import get_current_user, get_db

from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all(test_todo):
    response = client.get("/admin/todos")

    assert response.status_code == 200

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


def test_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")

    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todo/1666")

    assert response.status_code == 404
    assert response.json() == {"detail": "todo not found"}
