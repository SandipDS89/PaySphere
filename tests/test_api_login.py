import pytest
pytestmark = pytest.mark.integration
def _register_user(client, email="logintest@example.com", password="test123"):
    """Helper: registers a user so we have someone to log in as."""
    return client.post("/api/register", json={
        "name": "Login Test User",
        "email": email,
        "password": password
    })


def test_login_valid_credentials(client):
    _register_user(client)

    response = client.post("/api/login", json={
        "email": "logintest@example.com",
        "password": "test123"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "Welcome back" in data["message"]


def test_login_wrong_password(client):
    _register_user(client)

    response = client.post("/api/login", json={
        "email": "logintest@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]


def test_login_nonexistent_email(client):
    response = client.post("/api/login", json={
        "email": "doesnotexist@example.com",
        "password": "test123"
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]


def test_account_requires_login(client):
    # No login performed - should be rejected
    response = client.get("/api/account")

    assert response.status_code == 401
    assert "Unauthorized" in response.get_json()["error"]