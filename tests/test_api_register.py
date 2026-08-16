import pytest
pytestmark = pytest.mark.integration
def test_register_valid_user(client):
    response = client.post("/api/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "test123"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Registration successful."
    assert data["user"]["email"] == "testuser@example.com"


def test_register_duplicate_email(client):
    # First registration should succeed
    client.post("/api/register", json={
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "test123"
    })

    # Second registration with same email should fail
    response = client.post("/api/register", json={
        "name": "Second User",
        "email": "duplicate@example.com",
        "password": "test123"
    })

    assert response.status_code == 409
    assert "already exists" in response.get_json()["error"]


def test_register_missing_fields(client):
    response = client.post("/api/register", json={
        "name": "",
        "email": "",
        "password": ""
    })

    assert response.status_code == 400


def test_register_invalid_email_format(client):
    response = client.post("/api/register", json={
        "name": "Test User",
        "email": "notanemail",
        "password": "test123"
    })

    assert response.status_code == 400
    assert "valid email" in response.get_json()["error"]


def test_register_short_password(client):
    response = client.post("/api/register", json={
        "name": "Test User",
        "email": "shortpass@example.com",
        "password": "123"
    })

    assert response.status_code == 400