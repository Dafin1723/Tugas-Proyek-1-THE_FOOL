from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "thefool-secret"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            print_type TEXT,
            quantity INTEGER,
            created_at TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        filename = request.form["filename"]
        print_type = request.form["print_type"]
        quantity = request.form["quantity"]

        conn = get_db()
        conn.execute("""
            INSERT INTO orders 
            (filename, print_type, quantity, created_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, print_type, quantity, datetime.now().strftime("%Y-%m-%d %H:%M"), "Pending"))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", orders=orders)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
