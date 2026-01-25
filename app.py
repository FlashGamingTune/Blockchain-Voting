from blockchain import create_block
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

# Flask app setup
app = Flask(__name__)
app.secret_key =  "secret123"

# Database functions
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
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

# Routes
@app.route("/")
def home():
    return redirect("/login")


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
@app.route("/vote", methods=["GET", "POST"])
def vote():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        if session["has_voted"] == 1:
            return "You have already voted!"

        candidate_id = request.form["candidate_id"]
        voter_id = session["user_id"]

        # Get previous hash
        cursor.execute(
            "SELECT current_hash FROM blockchain ORDER BY id DESC LIMIT 1"
        )
        last_block = cursor.fetchone()

        previous_hash = last_block["current_hash"] if last_block else "0"

        # Create blockchain block
        block = create_block(voter_id, candidate_id, previous_hash)

        # Store block in database
        cursor.execute("""
        INSERT INTO blockchain
        (voter_id, candidate_id, timestamp, previous_hash, current_hash)
        VALUES (?, ?, ?, ?, ?)
        """, (
            block["voter_id"],
            block["candidate_id"],
            block["timestamp"],
            block["previous_hash"],
            block["current_hash"]
        ))

        cursor.execute(
            "UPDATE users SET has_voted = 1 WHERE id = ?",
            (voter_id,)
        )

        conn.commit()
        conn.close()

        session["has_voted"] = 1

        return "Vote cast successfully!"

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
            return redirect("/results")
        else:
            return "Invalid admin login"

    return render_template("admin.html")

# Admin
@app.route("/results")
def results():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidates.name, candidates.party, COUNT(blockchain.id) AS votes
        FROM blockchain
        JOIN candidates ON blockchain.candidate_id = candidates.id
        GROUP BY candidates.id
    """)
    results = cursor.fetchall()
    conn.close()

    return render_template("result.html", results=results)


# Admin - Manage Candidates
@app.route("/admin/candidates", methods=["GET", "POST"])
def manage_candidates():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        party = request.form["party"]

        cursor.execute(
            "INSERT INTO candidates (name, party) VALUES (?, ?)",
            (name, party)
        )
        conn.commit()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    conn.close()

    return render_template("manage_candidates.html", candidates=candidates)




# App runner (ALWAYS LAST)
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)