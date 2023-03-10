from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from functools import wraps

#configure flask
app = Flask(__name__)


#connect database
db= sqlite3.connect('where.db')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#def login require
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



#register route
@app.route("/register", methods=["GET", "POST"])
def register():

    # Get the form data
    if request.method == "POST":
        # Create a new database connection
        db = sqlite3.connect('where.db')

        username= request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmation')

        #check if any required field are empty
        if not username or not password or not confirm_password:
            flash('Required field empty')
            return redirect('/register')

        #password match
        if password != confirm_password:
           flash('Passwords do not match')
           return redirect('/register')

        #hashing the password
        hash = generate_password_hash(password)

        try:
            # Check if the username already exists in the database
            result = db.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = result.fetchone()
            if user:
                flash('Username already exists')
                return redirect('/register')

            # If username is not taken, insert the new user into the database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
            db.commit()
            flash('You are now registered and can log in!', 'success')
            return redirect('/login')

        except:
            db.rollback()
            flash('There was an error while registering. Please try again.')
            return redirect('/register')

        finally:
            # Close the database connection
            db.close()

    else:
        return render_template("register.html")



    
    #login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Create a new database connection
    db = sqlite3.connect('where.db')

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return flash("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return flash("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return flash("invalid username and/or password", 403)
        
        #update timestamp coumn with the current date and time 
        db.execute("UPDATE users SET timestamp = CURRENT_TIMESTAMP WHERE id = ?", (rows[0][0],))
        db.commit()

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # save the users location to the database
        location = request.remote_addr
        user_id = session.get("user_id")
        db.execute("UPDATE users SET location = ? WHERE id = ?", (location, user_id))
        db.commit()

        # Redirect user to home page
        return render_template("map.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    


@app.route('/')
def index():
    return render_template('login.html')


@app.route("/logout")
def logout():
    """log user out"""

    session.clear()

    return redirect("/login")