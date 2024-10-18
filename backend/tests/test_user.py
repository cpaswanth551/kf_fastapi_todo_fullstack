from ..routers.user import get_current_user, get_db
from .utils import *

from fastapi import status


def test_return_user(test_user):
    response = client.get("/user")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "appu"
    assert response.json()["email"] == "codingwithrobytest@email.com"
    assert response.json()["first_name"] == "Eric"
    assert response.json()["last_name"] == "Roby"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "(111)-111-1111"


def test_reset_password(test_user):
    response = client.post(
        "/user/password",
        json={"password": "testpassword", "new_password": "newpassord"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_reset_password_wrong_password(test_user):
    response = client.post(
        "/user/password",
        json={"password": "wrongpassowrd", "new_password": "newpassord"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change"}


def test_change_phone_number(test_user):
    response = client.post("user/phonenumber/9999999999")

    assert response.status_code == status.HTTP_204_NO_CONTENT
