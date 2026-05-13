import sqlite3
from datetime import datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret-key"

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

with app.app_context():
    init_db()
    seed_db()


@app.context_processor
def inject_nav_user():
    if session.get("user_id"):
        return {"nav_user_name": "Demo User"}
    return {}


def _format_currency(amount):
    return f"₹{amount:.2f}"


def _format_date(value):
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
        return parsed.strftime("%B %d, %Y")
    except ValueError:
        return value


def _get_initials(name):
    parts = [part for part in name.split() if part]
    initials = "".join(part[0] for part in parts[:2]).upper()
    return initials or name[:1].upper()


def _get_badge_class(category):
    mapping = {
        "food": "badge-food",
        "shopping": "badge-shopping",
        "bills": "badge-bills",
        "entertainment": "badge-entertainment",
    }
    return mapping.get(category.lower(), "")


def _get_bar_class(pct):
    return f"bar-{pct}"


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

    user_row = get_user_by_id(session["user_id"])
    if not user_row:
        abort(404)

    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "member_since": user_row["member_since"],
        "initials": _get_initials(user_row["name"]),
        "plan": "Starter",
    }

    summary = get_summary_stats(session["user_id"])
    stats = [
        {
            "label": "Total spent",
            "value": _format_currency(summary["total_spent"]),
            "note": "All time",
        },
        {
            "label": "Transactions",
            "value": str(summary["transaction_count"]),
            "note": "All time",
        },
        {
            "label": "Top category",
            "value": summary["top_category"],
            "note": "By total spent",
        },
    ]

    transactions = [
        {
            "date": _format_date(transaction["date"]),
            "description": transaction["description"],
            "category": transaction["category"],
            "badge_class": _get_badge_class(transaction["category"]),
            "amount": f"- {_format_currency(transaction['amount'])}",
        }
        for transaction in get_recent_transactions(session["user_id"])
    ]

    breakdown = get_category_breakdown(session["user_id"])
    categories = [
        {
            "name": item["name"],
            "total": _format_currency(item["amount"]),
            "bar_class": _get_bar_class(item["pct"]),
            "badge_class": _get_badge_class(item["name"]),
        }
        for item in breakdown
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
