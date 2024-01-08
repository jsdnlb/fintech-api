import os
from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
import pytest

client = TestClient(app)
load_dotenv()


@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "age": 25,
        "role": "user",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "hashed_password": "testpassword",
        "disabled": False,
    }


def test_get_all_users_without_auth():
    response = client.get("/users/")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_get_all_users():
    token = "Bearer " + os.getenv("TOKEN")
    headers = {"Authorization": token}

    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "users_ids" in data
    assert "result" in data
    assert isinstance(data["users_ids"], list)
    assert isinstance(data["result"], list)


def test_get_user_by_id():
    token = "Bearer " + os.getenv("TOKEN")
    headers = {"Authorization": token}
    known_user_id = os.getenv("USER_ID")
    response = client.get(f"/users/{known_user_id}", headers=headers)

    assert response.status_code == 200
    user = response.json()
    print(user)
    assert "username" in user
    assert "age" in user
    assert isinstance(user["id"], str)