import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, format_timestamp
from datetime import timedelta, datetime
# To run the virtual environment in debug mode python -m flask run --debug
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True  # Set session to be permanent
app.config["SESSION_TYPE"] = "filesystem"  # Store session data in the filesystem
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=4)  # Set session lifetime to 7 days

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///rocket.db")

# Filter
app.jinja_env.filters['format_timestamp'] = format_timestamp

@app.route("/")
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
    session.clear()
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
    

@app.route('/messages/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def messages(contact_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        message = request.form['message']
        if message:
            db.execute('''
                INSERT INTO messages (sender_id, receiver_id, message)
                VALUES (?, ?, ?)
            ''', int(user_id), int(contact_id), str(message))
        return redirect(url_for('messages', contact_id=contact_id))

    messages = db.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp
    ''', int(user_id), int(contact_id), int(contact_id), int(user_id))

    contact1 = db.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    contact2 = db.execute('SELECT username FROM users WHERE id = ?', (contact_id,))
    return render_template('messages.html', messages=messages, contact1=contact1[0]['username'], contact2=contact2[0]['username'], contact_me=contact_id)

@app.route('/contacts')
@login_required
def contacts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    add_contacts = db.execute(
        "SELECT DISTINCT sender_id FROM messages WHERE receiver_id = ? AND sender_id != ?", 
        user_id, user_id
    )
    add_contacts2 = db.execute(
        "SELECT DISTINCT receiver_id FROM messages WHERE sender_id = ? AND receiver_id != ?", 
        user_id, user_id
    )

    # Add contacts from the first query if they do not already exist
    for contact in add_contacts:
        contact_id = contact['sender_id']
        # Check if the contact already exists
        existing_contact = db.execute(
            "SELECT 1 FROM contacts WHERE user_id = ? AND contact_id = ?", 
            user_id, contact_id
        )
        if not existing_contact:
            db.execute(
                "INSERT INTO contacts (user_id, contact_id) VALUES (?, ?)", 
                user_id, contact_id
            )

    # Add contacts from the second query if they do not already exist
    for contact in add_contacts2:
        contact_id = contact['receiver_id']
        # Check if the contact already exists
        existing_contact = db.execute(
            "SELECT 1 FROM contacts WHERE user_id = ? AND contact_id = ?", 
            user_id, contact_id
        )
        if not existing_contact:
            db.execute(
                "INSERT INTO contacts (user_id, contact_id) VALUES (?, ?)", 
                user_id, contact_id
            )
    msg = {}
    """        
    latest = db.execute("SELECT message FROM messages WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp ASC", user_id, user_id)[0]['message']
    sender = db.execute("SELECT sender_id FROM messages WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp ASC", user_id, user_id)[0]['sender_id']
    name = db.execute("SELECT username FROM users WHERE id = ?", sender)[0]['username']
    """
    contacts = db.execute('''
        SELECT u.id, u.username
        FROM contacts c
        JOIN users u ON c.contact_id = u.id
        WHERE c.user_id = ?
    ''', (user_id,))
    return render_template('contacts.html', contacts=contacts)

@app.route('/autocomplete')
@login_required
def autocomplete():
    query = request.args.get('query', '')
    if query:
        user_id = session['user_id']
        # Fetch username and id, excluding the current user
        suggestions = db.execute(
            "SELECT id, username FROM users WHERE username LIKE ? AND id != ? LIMIT 10", 
            f'%{query}%', user_id
        )
        # Format the results as a list of dictionaries with 'id' and 'username'
        suggestions = [{'id': row['id'], 'username': row['username']} for row in suggestions]
        return jsonify(suggestions=suggestions)
    return jsonify(suggestions=[])

def load_messages():
    # Get the page number and limit from query parameters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))  # Number of messages to load per request
    
    user_id = session['user_id']
    contact_id = request.args.get('contact_id')
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Fetch messages
    messages = db.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC  -- Ascending order for older messages
        LIMIT ? OFFSET ?
    ''', (user_id, contact_id, contact_id, user_id, limit, offset))
    
    return jsonify({'messages': messages})