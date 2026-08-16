import pytest
from app import create_app
from config import TestConfig
from extensions import db as _db


@pytest.fixture(scope="function")
def app():
    """Creates a fresh Flask app configured for the test database."""
    flask_app = create_app(TestConfig)

    with flask_app.app_context():
        _db.create_all()   # build all tables fresh
        yield flask_app     # test runs here
        _db.session.remove()
        _db.drop_all()      # wipe everything after the test


@pytest.fixture(scope="function")
def client(app):
    """Flask's built-in test client — lets us send fake HTTP requests without a real server."""
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Gives tests direct access to the db session, e.g. to set up seed data."""
    return _db

@pytest.fixture
def logged_in_client_with_account(client, db):
    """
    Registers a user, logs them in, and gives them a wallet account.
    Returns the client (already authenticated) ready for deposit/withdraw/transfer tests.
    """
    from models import Account

    client.post("/api/register", json={
        "name": "Wallet User",
        "email": "walletuser@example.com",
        "password": "test123"
    })
    client.post("/api/login", json={
        "email": "walletuser@example.com",
        "password": "test123"
    })

    # Directly create an account in the DB (no API endpoint exists for this, by design)
    from models import User
    user = User.query.filter_by(email="walletuser@example.com").first()
    account = Account(
        user_id=user.id,
        account_number="PSTEST001",
        balance=1000.00,
        status="active"
    )
    db.session.add(account)
    db.session.commit()

    return client

@pytest.fixture
def two_accounts_setup(client, db):
    """
    Creates two users, each with their own account.
    Returns (client, source_account_number, destination_account_number)
    The client is logged in as the SOURCE user.
    """
    from models import User, Account

    # User A (source)
    client.post("/api/register", json={
        "name": "User A", "email": "usera@example.com", "password": "test123"
    })
    user_a = User.query.filter_by(email="usera@example.com").first()
    account_a = Account(user_id=user_a.id, account_number="PSTESTA", balance=1000.00, status="active")
    db.session.add(account_a)

    # User B (destination)
    client.post("/api/register", json={
        "name": "User B", "email": "userb@example.com", "password": "test123"
    })
    user_b = User.query.filter_by(email="userb@example.com").first()
    account_b = Account(user_id=user_b.id, account_number="PSTESTB", balance=500.00, status="active")
    db.session.add(account_b)

    db.session.commit()

    # Log in as User A (the source)
    client.post("/api/login", json={"email": "usera@example.com", "password": "test123"})

    return client, "PSTESTA", "PSTESTB"