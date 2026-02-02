from flask import flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from datetime import datetime


app = flask(_name_)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db_connection():
    conn : sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            print_type TEXT,
            copies INTEGER,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()



init_db



@app.route("/")
def index():
    return render_template(index.html)

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        file = request.files["file"]
        print_type = request.form["print_type"]
        copies = request.form["copies"]

        if file:
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO orders (filename, print_type, copies, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (filename, print_type, copies, "Pending", datetime.now())
            )
            conn.commit()
            conn.close()

            return redirect(url_for("success"))

    return render_template("order.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/admin")
def admin():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", orders=orders)

@app.route("/update/<int:order_id>/<status>")
def update_status(order_id, status):
    conn = get_db_connection()
    conn.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)