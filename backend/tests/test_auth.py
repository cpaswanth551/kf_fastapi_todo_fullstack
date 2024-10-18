from datetime import timedelta

from fastapi import HTTPException
from ..routers.auth import (
    get_current_user,
    create_access_token,
    autenticate_user,
    SECRET_KEY,
    ALGORITHM,
)
from jose import jwt
from .utils import *


def test_autenticate_user(test_user):
    db = TestingSessionLocal()

    autenticated_user = autenticate_user(test_user.username, "testpassword", db)
    assert autenticated_user is not None
    assert autenticated_user.username == test_user.username

    non_existing_user = autenticate_user("wronguser", "testpassword", db)
    assert non_existing_user is False

    wrong_password_user = autenticate_user(test_user.username, "wrongpassword", db)
    assert wrong_password_user is False


def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decode_token = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False}
    )

    assert decode_token["sub"] == username
    assert decode_token["id"] == user_id
    assert decode_token["role"] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excifo:
        await get_current_user(token=token)

    assert excifo.value.status_code == 401

    assert excifo.value.detail == "Could not validate user."
