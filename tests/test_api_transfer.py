import pytest
pytestmark = pytest.mark.integration
def test_transfer_valid(two_accounts_setup):
    client, source_acc, dest_acc = two_accounts_setup

    response = client.post("/api/transfer", json={
        "account_number": dest_acc,
        "amount": "300"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["new_balance"] == "700.00"  # 1000 - 300


def test_transfer_insufficient_balance(two_accounts_setup):
    client, source_acc, dest_acc = two_accounts_setup

    response = client.post("/api/transfer", json={
        "account_number": dest_acc,
        "amount": "9999"
    })

    assert response.status_code == 400
    assert "Insufficient balance" in response.get_json()["error"]


def test_transfer_to_nonexistent_account(two_accounts_setup):
    client, source_acc, dest_acc = two_accounts_setup

    response = client.post("/api/transfer", json={
        "account_number": "PSDOESNOTEXIST",
        "amount": "100"
    })

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_transfer_to_self(two_accounts_setup):
    client, source_acc, dest_acc = two_accounts_setup

    response = client.post("/api/transfer", json={
        "account_number": source_acc,  # transferring to own account
        "amount": "100"
    })

    assert response.status_code == 400
    assert "own account" in response.get_json()["error"]


def test_transfer_exact_balance_boundary(two_accounts_setup):
    """Boundary Value Analysis: transferring exactly the full balance should succeed."""
    client, source_acc, dest_acc = two_accounts_setup

    response = client.post("/api/transfer", json={
        "account_number": dest_acc,
        "amount": "1000"  # exactly equal to source balance
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["new_balance"] == "0.00"