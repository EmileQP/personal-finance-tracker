import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from datetime import timedelta
# To run the virtual environment in debug mode python -m flask run --debug
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True  # Set session to be permanent
app.config["SESSION_TYPE"] = "filesystem"  # Store session data in the filesystem
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=4)  # Set session lifetime to 7 days

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///rocket.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error="Incorrect Username!")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="Incorrect Password!")
        username = request.form.get("username")
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", username, username
        )
        if  '@' in username:
            username = db.execute("SELECT username FROM users WHERE email=?", username)[0]['username']
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return render_template("login.html", error="Incorrect Username or Password!")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash(f"Welcome back {username}!", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username1 = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("confirmation")
        email = request.form.get("email")
        if password != password2:
            return render_template("register.html", error="Passwords don't match!")

        if not username1:
            return render_template("register.html", error="Did not enter a Username!")
        
        if not email:
            return render_template("register.html", error="Did not enter an Email!")

        if not password:
            return render_template("register.html", error="Did not enter a Password!")

        password_hash = generate_password_hash(password)
        usernames = db.execute(
            "SELECT COUNT(username) as count FROM users WHERE username = ?", username1)

        if usernames[0]["count"] > 0:
            return render_template("register.html", error="Username is taken!")

        db.execute("INSERT INTO users (username, password, email) VALUES(?, ?, ?)", username1, password_hash, email)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        flash("Registered!", "success")
        return redirect("/")
    else:
        return render_template("register.html")

