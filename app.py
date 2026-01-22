from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

# 1️⃣ Flask app setup
app = Flask(__name__)
app.secret_key =  "secret123"

# 2️⃣ Database functions
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# 3️⃣ Create tables if they don't exist
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        has_voted INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        party TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blockchain (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id INTEGER,
        candidate_id INTEGER,
        timestamp TEXT,
        previous_hash TEXT,
        current_hash TEXT
    )
    """)

    conn.commit()
    conn.close()

# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["has_voted"] = user["has_voted"]
            return redirect("/vote")
        else:
            return "Invalid login"

    return render_template("login.html")

# Voting Page
@app.route("/vote")
def vote():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    conn.close()

    return render_template("vote.html", candidates=candidates)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Admin Login
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            return "Invalid admin login"

    return render_template("admin.html")


# 4️⃣ App runner (ALWAYS LAST)
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)