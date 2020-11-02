import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///main.db")

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("homepage.html")

@app.route("/delete/<trip_name>", methods=["GET"])
def delete(trip_name):
    user_id = session["user_id"]
    if request.method == "GET":
        ifTripExists = db.execute("SELECT trip_name FROM trips WHERE trip_Name = :trip_name AND user_id = :user_id", trip_name = trip_name, user_id = user_id)
        if ifTripExists:
            db.execute("DELETE FROM trip_countries WHERE user_id = :user_id AND trip_name = :trip_name", user_id = user_id, trip_name = trip_name)
            db.execute("DELETE FROM trips WHERE user_id = :user_id AND trip_name = :trip_name", user_id = user_id, trip_name = trip_name)

    return redirect("/user_home")



@app.route("/trip/<tripname>", methods=["GET"])
@login_required
def trip(tripname):
    user_id = session["user_id"]
    if request.method == "GET":
        ifTripExists = db.execute("SELECT trip_name FROM trips WHERE trip_Name = :trip_name", trip_name = tripname)
        if ifTripExists:
            countries = db.execute("SELECT country FROM trip_countries WHERE user_id = :user_id AND trip_name = :trip_name", user_id = user_id, trip_name = tripname)
        return render_template("trip.html", countries = countries, trip_name = tripname)

@app.route("/<tripname>/<country>", methods=["GET","POST"])
@login_required
def country(country, tripname):
    if request.method == "GET":
        user_id = session["user_id"]
        trip_name = tripname
        countries = request.form.to_dict()
        countries_filtered = find_keys('nameL', countries)
        country_location = db.execute("SELECT * FROM countries WHERE country = :country", country = country)

        ifTripExists = db.execute("SELECT trip_name FROM trips WHERE trip_Name = :trip_name", trip_name = trip_name)
        if not ifTripExists:
            db.execute("INSERT INTO trips (user_id, trip_name, date_time) VALUES (:user_id, :trip_name, :date_time)", user_id = user_id, trip_name = trip_name, date_time = datetime.datetime.now())

            for country in range(0, len(countries_filtered)):
                country = countries_filtered[f'nameList_{country}']
                db.execute("INSERT INTO trip_countries (user_id, trip_name, country) VALUES (:user_id, :trip_name, :country)", user_id = user_id, trip_name = trip_name, country = country)

        if ifTripExists:
            if countries:
                db.execute("DELETE FROM trip_countries WHERE trip_name = :trip_name AND user_id = :user_id", user_id = user_id, trip_name = trip_name)

                for country in range(0, len(countries_filtered)):
                    country = countries_filtered[f'nameList_{country}']
                    db.execute("INSERT INTO trip_countries (user_id, trip_name, country) VALUES (:user_id, :trip_name, :country)", user_id = user_id, trip_name = trip_name, country = country)

        return render_template("country.html", trip_name = trip_name, country = country, country_location = country_location)
    else:
        return redirect("/user_home")



@app.route("/user_home", methods=["GET", "POST"])
@login_required
def user_home():
    if request.method == "GET":
        user = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])
        trips = get_trips(session["user_id"])
        return render_template("user_home.html", user = user, trips = trips )
    else:
        return render_template("user_home.html")

@app.route("/trip_builder", methods=["GET","POST"])
@login_required
def trip_builder():
    if request.method == "GET":
        user = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])
        countries = get_countries()
        countriesJson = json.dumps(countries)
        return render_template("tripbuilder.html", user = user, countries = countries, countriesJson = countriesJson)
    else:
        user_id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])
        trips = get_trips(session["user_id"])
        ## when submited the items are saved to new table called flights with user_id, trip_name,

        trip_name = request.form.get("trip_name")
        countries = request.form.to_dict()
        print(trip_name)
        print(countries)
        countries_filtered = find_keys('nameL', countries)

        ifTripExists = db.execute("SELECT trip_name FROM trips WHERE trip_Name = :trip_name", trip_name = trip_name)
        if not ifTripExists:
            db.execute("INSERT INTO trips (user_id, trip_name, date_time) VALUES (:user_id, :trip_name, :date_time)", user_id = user_id, trip_name = trip_name, date_time = datetime.datetime.now())

            for country in range(0, len(countries_filtered)):
                country = countries_filtered[f'nameList_{country}']
                db.execute("INSERT INTO trip_countries (user_id, trip_name, country) VALUES (:user_id, :trip_name, :country)", user_id = user_id, trip_name = trip_name, country = country)

        if ifTripExists:
            db.execute("DELETE FROM trip_countries WHERE trip_name = :trip_name AND user_id = :user_id", user_id = user_id, trip_name = trip_name)

            for country in range(0, len(countries_filtered)):
                country = countries_filtered[f'nameList_{country}']
                db.execute("INSERT INTO trip_countries (user_id, trip_name, country) VALUES (:user_id, :trip_name, :country)", user_id = user_id, trip_name = trip_name, country = country)

        return redirect("/user_home")


@app.route("/login", methods=["GET", "POST"])
def login():
#"""Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/user_home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not ((request.form.get("password")) == (request.form.get("passwordVerify"))):
            return apology("must provide passwords that match", 403)

        # register in DB
        username = request.form.get("username")
        email = request.form.get("email")
        check_unique = db.execute("SELECT email FROM users WHERE email = :email", email = email)
        if check_unique:
            return apology("That email has been register. Please try a new one", 403)

        hashed = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, email, password_hash, date_time) VALUES (:username, :email, :hash, :date_time)", username = username, email = email, hash = hashed, date_time = datetime.datetime.now())

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user_id = session["user_id"]
        username = db.execute("SELECT * FROM users WHERE user_id = :user_id",
                          user_id=user_id)

        # Ensure username exists and password is correct
        if not check_password_hash(username[0]["password_hash"], request.form.get("current")):
            return apology("Current Password Incorrect", 403)

        if not (request.form.get("new_password1") == request.form.get("new_password2")):
            return apology("New Passwords Don't Match")

        hashed = generate_password_hash(request.form.get("new_password2"), method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET password_hash = :hash WHERE user_id = :user_id",
            user_id = user_id, hash = hashed)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM users WHERE user_id = :user_id",
                          user_id=user_id)
        return render_template("settings.html", username = username)

@app.route("/update/<new_username>", methods=["POST"])
@login_required
def update_username(new_username):
    user_id = session["user_id"]
    if request.method == "POST":
        db.execute("UPDATE users SET username = :user_name WHERE user_id = :user_id", user_name = new_username, user_id = user_id)
        return redirect("/settings")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")