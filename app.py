from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "cybersecretkey"

DATABASE = "database.db"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# AUTO CREATE DATABASE TABLES
def init_db():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        message TEXT
    )
    """)

    db.commit()
    db.close()


init_db()


@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        db = get_db()

        try:
            db.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username, hashed)
            )
            db.commit()
        except:
            return "Username already exists"

        return redirect("/login")

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):

            session["user"] = username

            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])


# SEND MESSAGE
@app.route("/send", methods=["POST"])
def send():

    if "user" not in session:
        return redirect("/login")

    message = request.form["message"]

    db = get_db()

    db.execute(
        "INSERT INTO messages(user,message) VALUES (?,?)",
        (session["user"], message)
    )

    db.commit()

    return redirect("/dashboard")


# GET MESSAGES
@app.route("/messages")
def messages():

    db = get_db()

    msgs = db.execute(
        "SELECT user,message FROM messages ORDER BY id DESC LIMIT 50"
    ).fetchall()

    data = []

    for m in msgs:
        data.append({
            "user": m["user"],
            "msg": m["message"]
        })

    return jsonify({"messages": data})


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)