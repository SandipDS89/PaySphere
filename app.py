from functools import wraps
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import Config
from extensions import db
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from models import User, Account, Transaction


def login_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def home():
    return "PaySphere is running and connected!"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_role"] = user.role

        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/create-account")
@login_required_api
def create_account():
    user_id = session["user_id"]

    existing_account = Account.query.filter_by(user_id=user_id).first()
    if existing_account:
        flash("You already have an account.", "warning")
        return redirect(url_for("dashboard"))

    total_accounts = Account.query.count()
    new_account_number = f"PS{100001 + total_accounts}"

    new_account = Account(
        user_id=user_id,
        account_number=new_account_number,
        balance=0.00,
        status="active"
    )

    db.session.add(new_account)
    db.session.commit()

    flash(f"Account created successfully! Your account number is {new_account_number}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required_api
def dashboard():
    user_id = session["user_id"]
    account = Account.query.filter_by(user_id=user_id).first()
    return render_template("dashboard.html", account=account)


def get_valid_amount(raw_value):
    """
    Helper function: converts form input into a safe Decimal amount.
    Returns None if invalid (not a number, zero, or negative).
    We use Decimal instead of float for money — same reason as our database column.
    """
    try:
        amount = Decimal(raw_value)
    except (InvalidOperation, TypeError):
        return None

    if amount <= 0:
        return None

    return amount


@app.route("/deposit", methods=["GET", "POST"])
@login_required_api
def deposit():
    user_id = session["user_id"]
    account = Account.query.filter_by(user_id=user_id).first()

    if not account:
        flash("You need to create an account first.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        raw_amount = request.form.get("amount", "")
        amount = get_valid_amount(raw_amount)

        if amount is None:
            flash("Please enter a valid amount greater than 0.", "danger")
            return redirect(url_for("deposit"))

        if account.status != "active":
            flash("Your account is not active. Deposits are not allowed.", "danger")
            return redirect(url_for("dashboard"))

        # Update balance
        account.balance = account.balance + amount

        # Create transaction record
        txn = Transaction(
            source_account_id=None,             # money "enters" the system, no source
            destination_account_id=account.id,
            transaction_type="DEPOSIT",
            amount=amount,
            status="SUCCESS",
            description="Deposit to account"
        )
        db.session.add(txn)
        db.session.commit()

        flash(f"₹{amount} deposited successfully! New balance: ₹{account.balance}", "success")
        return redirect(url_for("dashboard"))

    return render_template("deposit.html", account=account)


@app.route("/withdraw", methods=["GET", "POST"])
@login_required_api
def withdraw():
    user_id = session["user_id"]
    account = Account.query.filter_by(user_id=user_id).first()

    if not account:
        flash("You need to create an account first.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        raw_amount = request.form.get("amount", "")
        amount = get_valid_amount(raw_amount)

        if amount is None:
            flash("Please enter a valid amount greater than 0.", "danger")
            return redirect(url_for("withdraw"))

        if account.status != "active":
            flash("Your account is not active. Withdrawals are not allowed.", "danger")
            return redirect(url_for("dashboard"))

        if amount > account.balance:
            flash("Insufficient balance for this withdrawal.", "danger")
            return redirect(url_for("withdraw"))

        # Update balance
        account.balance = account.balance - amount

        # Create transaction record
        txn = Transaction(
            source_account_id=account.id,
            destination_account_id=None,        # money "leaves" the system, no destination
            transaction_type="WITHDRAW",
            amount=amount,
            status="SUCCESS",
            description="Withdrawal from account"
        )
        db.session.add(txn)
        db.session.commit()

        flash(f"₹{amount} withdrawn successfully! New balance: ₹{account.balance}", "success")
        return redirect(url_for("dashboard"))

    return render_template("withdraw.html", account=account)

@app.route("/transfer", methods=["GET", "POST"])
@login_required_api
def transfer():
    user_id = session["user_id"]
    source_account = Account.query.filter_by(user_id=user_id).first()

    if not source_account:
        flash("You need to create an account first.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        destination_account_number = request.form.get("account_number", "").strip()
        raw_amount = request.form.get("amount", "")
        amount = get_valid_amount(raw_amount)

        # --- Validation ---
        if amount is None:
            flash("Please enter a valid amount greater than 0.", "danger")
            return redirect(url_for("transfer"))

        if source_account.status != "active":
            flash("Your account is not active. Transfers are not allowed.", "danger")
            return redirect(url_for("dashboard"))

        destination_account = Account.query.filter_by(
            account_number=destination_account_number
        ).first()

        if not destination_account:
            flash("Destination account not found.", "danger")
            return redirect(url_for("transfer"))

        if destination_account.id == source_account.id:
            flash("You cannot transfer money to your own account.", "danger")
            return redirect(url_for("transfer"))

        if destination_account.status != "active":
            flash("Destination account is not active.", "danger")
            return redirect(url_for("transfer"))

        if amount > source_account.balance:
            flash("Insufficient balance for this transfer.", "danger")
            return redirect(url_for("transfer"))

        # --- Perform the atomic transfer ---
        try:
            source_account.balance = source_account.balance - amount
            destination_account.balance = destination_account.balance + amount

            txn = Transaction(
                source_account_id=source_account.id,
                destination_account_id=destination_account.id,
                transaction_type="TRANSFER",
                amount=amount,
                status="SUCCESS",
                description=f"Transfer to {destination_account.account_number}"
            )
            db.session.add(txn)
            db.session.commit()

            flash(
                f"₹{amount} transferred successfully to {destination_account.account_number}!",
                "success"
            )
            return redirect(url_for("dashboard"))

        except Exception:
            db.session.rollback()
            flash("Something went wrong. Transfer was not completed.", "danger")
            return redirect(url_for("transfer"))

    return render_template("transfer.html", account=source_account)

@app.route("/transactions")
@login_required_api
def transactions():
    user_id = session["user_id"]
    account = Account.query.filter_by(user_id=user_id).first()

    if not account:
        flash("You need to create an account first.", "warning")
        return redirect(url_for("dashboard"))

    txn_list = Transaction.query.filter(
        or_(
            Transaction.source_account_id == account.id,
            Transaction.destination_account_id == account.id
        )
    ).order_by(Transaction.created_at.desc()).all()

    return render_template("transactions.html", account=account, transactions=txn_list)

# ============ REST API ============

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    new_user = User(name=name, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful.",
        "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}
    }), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role

    return jsonify({
        "message": f"Welcome back, {user.name}!",
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
    }), 200


@app.route("/api/account", methods=["GET"])
@login_required_api
def api_get_account():
    account = Account.query.filter_by(user_id=session["user_id"]).first()

    if not account:
        return jsonify({"error": "No account found. Please create one first."}), 404

    return jsonify({
        "account_number": account.account_number,
        "balance": str(account.balance),
        "status": account.status
    }), 200


@app.route("/api/account/balance", methods=["GET"])
@login_required_api
def api_get_balance():
    account = Account.query.filter_by(user_id=session["user_id"]).first()

    if not account:
        return jsonify({"error": "No account found. Please create one first."}), 404

    return jsonify({"balance": str(account.balance)}), 200


@app.route("/api/deposit", methods=["POST"])
@login_required_api
def api_deposit():
    account = Account.query.filter_by(user_id=session["user_id"]).first()
    if not account:
        return jsonify({"error": "No account found. Please create one first."}), 404

    data = request.get_json(silent=True) or {}
    amount = get_valid_amount(str(data.get("amount", "")))

    if amount is None:
        return jsonify({"error": "amount must be a number greater than 0."}), 400

    if account.status != "active":
        return jsonify({"error": "Account is not active."}), 403

    account.balance = account.balance + amount
    txn = Transaction(
        source_account_id=None,
        destination_account_id=account.id,
        transaction_type="DEPOSIT",
        amount=amount,
        status="SUCCESS",
        description="Deposit via API"
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({"message": "Deposit successful.", "new_balance": str(account.balance)}), 200


@app.route("/api/withdraw", methods=["POST"])
@login_required_api
def api_withdraw():
    account = Account.query.filter_by(user_id=session["user_id"]).first()
    if not account:
        return jsonify({"error": "No account found. Please create one first."}), 404

    data = request.get_json(silent=True) or {}
    amount = get_valid_amount(str(data.get("amount", "")))

    if amount is None:
        return jsonify({"error": "amount must be a number greater than 0."}), 400

    if account.status != "active":
        return jsonify({"error": "Account is not active."}), 403

    if amount > account.balance:
        return jsonify({"error": "Insufficient balance."}), 400

    account.balance = account.balance - amount
    txn = Transaction(
        source_account_id=account.id,
        destination_account_id=None,
        transaction_type="WITHDRAW",
        amount=amount,
        status="SUCCESS",
        description="Withdrawal via API"
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({"message": "Withdrawal successful.", "new_balance": str(account.balance)}), 200


@app.route("/api/transfer", methods=["POST"])
@login_required_api
def api_transfer():
    source_account = Account.query.filter_by(user_id=session["user_id"]).first()
    if not source_account:
        return jsonify({"error": "No account found. Please create one first."}), 404

    data = request.get_json(silent=True) or {}
    destination_account_number = (data.get("account_number") or "").strip()
    amount = get_valid_amount(str(data.get("amount", "")))

    if amount is None:
        return jsonify({"error": "amount must be a number greater than 0."}), 400

    if source_account.status != "active":
        return jsonify({"error": "Your account is not active."}), 403

    destination_account = Account.query.filter_by(account_number=destination_account_number).first()

    if not destination_account:
        return jsonify({"error": "Destination account not found."}), 404

    if destination_account.id == source_account.id:
        return jsonify({"error": "Cannot transfer to your own account."}), 400

    if destination_account.status != "active":
        return jsonify({"error": "Destination account is not active."}), 403

    if amount > source_account.balance:
        return jsonify({"error": "Insufficient balance."}), 400

    try:
        source_account.balance = source_account.balance - amount
        destination_account.balance = destination_account.balance + amount

        txn = Transaction(
            source_account_id=source_account.id,
            destination_account_id=destination_account.id,
            transaction_type="TRANSFER",
            amount=amount,
            status="SUCCESS",
            description=f"Transfer via API to {destination_account.account_number}"
        )
        db.session.add(txn)
        db.session.commit()

        return jsonify({
            "message": "Transfer successful.",
            "new_balance": str(source_account.balance)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Transfer failed. Please try again."}), 500


@app.route("/api/transactions", methods=["GET"])
@login_required_api
def api_transactions():
    account = Account.query.filter_by(user_id=session["user_id"]).first()
    if not account:
        return jsonify({"error": "No account found. Please create one first."}), 404

    txn_list = Transaction.query.filter(
        or_(
            Transaction.source_account_id == account.id,
            Transaction.destination_account_id == account.id
        )
    ).order_by(Transaction.created_at.desc()).all()

    results = []
    for txn in txn_list:
        results.append({
            "id": txn.id,
            "type": txn.transaction_type,
            "amount": str(txn.amount),
            "status": txn.status,
            "description": txn.description,
            "created_at": txn.created_at.isoformat(),
            "source_account_id": txn.source_account_id,
            "destination_account_id": txn.destination_account_id
        })

    return jsonify({"transactions": results}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database connected and tables created!")
    app.run(debug=True)