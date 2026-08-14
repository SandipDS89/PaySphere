from app import app
from extensions import db
from models import User, Account, Transaction

with app.app_context():
    print("Seeding PaySphere sample data...")

    # --- Sample users ---
    admin = User(name="Admin User", email="admin@paysphere.com", role="admin")
    admin.set_password("admin123")

    customer1 = User(name="Ravi Sharma", email="ravi@example.com", role="customer")
    customer1.set_password("password123")

    customer2 = User(name="Priya Singh", email="priya@example.com", role="customer")
    customer2.set_password("password123")

    customer3 = User(name="Amit Kumar", email="amit@example.com", role="customer")
    customer3.set_password("password123")

    db.session.add_all([admin, customer1, customer2, customer3])
    db.session.commit()
    print(f"Created {4} users.")

    # --- Sample accounts ---
    acc1 = Account(user_id=customer1.id, account_number="PS100001", balance=5000.00, status="active")
    acc2 = Account(user_id=customer2.id, account_number="PS100002", balance=3000.00, status="active")
    acc3 = Account(user_id=customer3.id, account_number="PS100003", balance=1000.00, status="active")

    db.session.add_all([acc1, acc2, acc3])
    db.session.commit()
    print(f"Created {3} accounts.")

    # --- Sample transactions ---
    txn1 = Transaction(
        source_account_id=None, destination_account_id=acc1.id,
        transaction_type="DEPOSIT", amount=5000.00, status="SUCCESS",
        description="Initial deposit"
    )
    txn2 = Transaction(
        source_account_id=None, destination_account_id=acc2.id,
        transaction_type="DEPOSIT", amount=3000.00, status="SUCCESS",
        description="Initial deposit"
    )
    txn3 = Transaction(
        source_account_id=acc1.id, destination_account_id=acc3.id,
        transaction_type="TRANSFER", amount=1000.00, status="SUCCESS",
        description="Transfer to PS100003"
    )

    db.session.add_all([txn1, txn2, txn3])
    db.session.commit()
    print(f"Created {3} transactions.")

    print("✅ Seeding complete!")
    print("\nSample login credentials:")
    print("Admin:     admin@paysphere.com / admin123")
    print("Customer1: ravi@example.com / password123")
    print("Customer2: priya@example.com / password123")
    print("Customer3: amit@example.com / password123")