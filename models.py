from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One user can have multiple accounts (we'll usually just use one per user)
    accounts = db.relationship("Account", backref="owner", lazy=True)

    def set_password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)

    def __repr__(self):
        return f"<User {self.email}>"


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Account {self.account_number} - Balance: {self.balance}>"


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    source_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    destination_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # DEPOSIT, WITHDRAW, TRANSFER
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to easily access the actual Account objects, not just IDs
    source_account = db.relationship("Account", foreign_keys=[source_account_id])
    destination_account = db.relationship("Account", foreign_keys=[destination_account_id])

    def __repr__(self):
        return f"<Transaction {self.transaction_type} - {self.amount}>"