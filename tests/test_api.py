import pytest


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_create_user(client):
    payload = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "JohnPass99",
        "full_name": "John Doe",
    }
    resp = client.post("/users/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "john_doe"
    assert data["email"] == "john@example.com"
    assert "hashed_password" not in data
    assert "password" not in data


def test_duplicate_username(client):
    payload = {"username": "dupuser", "email": "dup1@example.com", "password": "DupPass99"}
    client.post("/users/", json=payload)
    resp = client.post("/users/", json={**payload, "email": "dup2@example.com"})
    assert resp.status_code == 400


def test_duplicate_email(client):
    payload = {"username": "uniqueuser1", "email": "shared@example.com", "password": "SharedPass9"}
    client.post("/users/", json=payload)
    resp = client.post("/users/", json={**payload, "username": "uniqueuser2"})
    assert resp.status_code == 400


def test_get_user(client):
    payload = {"username": "getme_user", "email": "getme@example.com", "password": "GetMe9999"}
    create_resp = client.post("/users/", json=payload)
    user_id = create_resp.json()["id"]
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["username"] == "getme_user"


def test_get_user_not_found(client):
    resp = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_list_users(client):
    resp = client.get("/users/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_update_user(client):
    payload = {"username": "update_me", "email": "updateme@example.com", "password": "UpdateMe9"}
    user_id = client.post("/users/", json=payload).json()["id"]
    resp = client.patch(f"/users/{user_id}", json={"full_name": "Updated Name"})
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Updated Name"


def test_delete_user(client):
    payload = {"username": "delete_me", "email": "deleteme@example.com", "password": "DeleteMe9"}
    user_id = client.post("/users/", json=payload).json()["id"]
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 204
    resp2 = client.get(f"/users/{user_id}")
    assert resp2.status_code == 404
