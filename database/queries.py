from datetime import datetime

from database.db import get_db


def _format_member_since(created_at):
    if not created_at:
        return ""

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(created_at, fmt)
            return parsed.strftime("%B %Y")
        except ValueError:
            continue

    return created_at


def get_user_by_id(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return None

        return {
            "name": row["name"],
            "email": row["email"],
            "member_since": _format_member_since(row["created_at"]),
        }
    finally:
        conn.close()


def get_summary_stats(user_id):
    conn = get_db()
    try:
        totals = conn.execute(
            "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        top = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        return {
            "total_spent": float(totals["total"] or 0),
            "transaction_count": int(totals["count"] or 0),
            "top_category": top["category"] if top else "—",
        }
    finally:
        conn.close()


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT date, description, category, amount
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC, created_at DESC, id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

        return [
            {
                "date": row["date"],
                "description": row["description"],
                "category": row["category"],
                "amount": float(row["amount"]),
            }
            for row in rows
        ]
    finally:
        conn.close()


def get_category_breakdown(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (user_id,),
        ).fetchall()

        if not rows:
            return []

        total_spent = sum(row["total"] for row in rows)
        if total_spent <= 0:
            return []

        percentages = [
            int(round((row["total"] / total_spent) * 100)) for row in rows
        ]
        remainder = 100 - sum(percentages)
        if remainder != 0:
            percentages[0] += remainder

        return [
            {
                "name": row["category"],
                "amount": float(row["total"]),
                "pct": int(percentages[index]),
            }
            for index, row in enumerate(rows)
        ]
    finally:
        conn.close()
