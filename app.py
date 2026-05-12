import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret-key"

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

with app.app_context():
    init_db()
    seed_db()


@app.context_processor
def inject_nav_user():
    if session.get("user_id"):
        return {"nav_user_name": "Demo User"}
    return {}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not all([name, email, password, confirm_password]):
            flash("All fields are required.")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("register.html")

        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            flash("Email already registered.")
            return render_template("register.html")

        flash("Account created successfully. Please sign in.")
        return redirect(url_for("login"))

    abort(405)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Invalid email or password.")
            return render_template("login.html")

        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect(url_for("profile"))

    abort(405)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "May 2024",
        "initials": "DU",
        "plan": "Starter",
    }

    stats = [
        {"label": "Total spent", "value": "Rs 18,240", "note": "This month"},
        {"label": "Transactions", "value": "34", "note": "Last 30 days"},
        {"label": "Top category", "value": "Food", "note": "42% of spend"},
    ]

    transactions = [
        {
            "date": "May 12, 2026",
            "description": "Grocery shopping",
            "category": "Food",
            "badge_class": "badge-food",
            "amount": "- Rs 55.00",
        },
        {
            "date": "May 10, 2026",
            "description": "New shoes",
            "category": "Shopping",
            "badge_class": "badge-shopping",
            "amount": "- Rs 85.00",
        },
        {
            "date": "May 08, 2026",
            "description": "Movie tickets",
            "category": "Entertainment",
            "badge_class": "badge-entertainment",
            "amount": "- Rs 25.00",
        },
        {
            "date": "May 05, 2026",
            "description": "Electricity bill",
            "category": "Bills",
            "badge_class": "badge-bills",
            "amount": "- Rs 120.00",
        },
    ]

    categories = [
        {
            "name": "Food",
            "total": "Rs 420.00",
            "bar_class": "bar-72",
            "badge_class": "badge-food",
        },
        {
            "name": "Shopping",
            "total": "Rs 185.00",
            "bar_class": "bar-48",
            "badge_class": "badge-shopping",
        },
        {
            "name": "Bills",
            "total": "Rs 160.00",
            "bar_class": "bar-38",
            "badge_class": "badge-bills",
        },
        {
            "name": "Entertainment",
            "total": "Rs 95.00",
            "bar_class": "bar-28",
            "badge_class": "badge-entertainment",
        },
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
