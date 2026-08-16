import pytest
pytestmark = pytest.mark.integration
def test_deposit_valid_amount(logged_in_client_with_account):
    client = logged_in_client_with_account

    response = client.post("/api/deposit", json={"amount": "500"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["new_balance"] == "1500.00"


def test_deposit_negative_amount(logged_in_client_with_account):
    client = logged_in_client_with_account

    response = client.post("/api/deposit", json={"amount": "-100"})

    assert response.status_code == 400
    assert "greater than 0" in response.get_json()["error"]


def test_deposit_zero_amount(logged_in_client_with_account):
    client = logged_in_client_with_account

    response = client.post("/api/deposit", json={"amount": "0"})

    assert response.status_code == 400


def test_deposit_without_account(client):
    # Register + login, but skip account creation entirely
    client.post("/api/register", json={
        "name": "No Wallet User",
        "email": "nowallet@example.com",
        "password": "test123"
    })
    client.post("/api/login", json={
        "email": "nowallet@example.com",
        "password": "test123"
    })

    response = client.post("/api/deposit", json={"amount": "500"})

    assert response.status_code == 404
    assert "No account found" in response.get_json()["error"]