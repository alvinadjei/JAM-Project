import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required


'''
    Personal touch: I added a "Settings" page (link in top right after you login) that
    allows the user to change their password. The code for that is at the bottom of this
    file.
'''

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///jam.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Homepage
@app.route("/")
@login_required
def index():
    """Show user profile"""

    # Show user info in a table
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    profile = rows[0]
    name = profile["name"]
    primary_instrument = profile["primary_instrument"]
    genre = profile["genre"]
    instruments = profile["instruments"]
    status = profile["status"]

    return render_template("index.html", name=name, primary_instrument=primary_instrument, genre=genre, instruments=instruments, status=status)


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide full name", 400)

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email address", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must match", 400)

        # Ensure primary instrument was submitted
        elif not request.form.get("primary_instrument"):
            return apology("must provide primary instrument", 400)

        # Ensure genre was submitted
        elif request.form.get("genre") == "Please select a genre":
            return apology("must provide genre", 400)

        name = request.form.get("name")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))
        primary_instrument = request.form.get("primary_instrument")
        primary_instrument = primary_instrument.lower()
        genre = request.form.get("genre")
        genre = genre.lower()
        instruments = request.form.get("instruments")
        instruments = instruments.lower()
        status = "active"

        # Query database for email
        rows = db.execute("SELECT * FROM users")
        users = []
        for row in rows:
            users.append(row['email'])

        # Ensure email isn't already in use
        if email in users:
            return apology("This email address is already associated with an account")

        db.execute("INSERT INTO users (name, email, hash, primary_instrument, genre, instruments, status) VALUES (?, ?, ?, ?, ?, ?, ?)", name, email, password, primary_instrument, genre, instruments, status)

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Change settings"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide full name", 400)

        # Ensure new password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure new password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must match", 400)

        # Ensure primary instrument was submitted
        elif not request.form.get("primary_instrument"):
            return apology("must provide primary instrument", 400)

        # Ensure genre was submitted
        elif request.form.get("genre") == "Please select a genre":
            return apology("must provide genre", 400)

        # Ensure status was submitted
        elif not request.form.get("status"):
            return apology("must provide status update", 400)

        # Activate profile
        if request.form.get("status") == "activate":
            status = "active"

        # Deactivate profile
        elif request.form.get("status") == "deactivate":
            status = "inactive"

        # Generate password hash and update other info
        name = request.form.get("name")
        password = generate_password_hash(request.form.get("password"))
        primary_instrument = request.form.get("primary_instrument")
        primary_instrument = primary_instrument.lower()
        genre = request.form.get("genre")
        genre = genre.lower()
        instruments = request.form.get("instruments")
        instruments = instruments.lower()

        # Update password hash in SQL database
        db.execute("UPDATE users SET name = ? WHERE id = ?", name, session["user_id"])
        db.execute("UPDATE users SET hash = ? WHERE id = ?", password, session["user_id"])
        db.execute("UPDATE users SET primary_instrument = ? WHERE id = ?", primary_instrument, session["user_id"])
        db.execute("UPDATE users SET genre = ? WHERE id = ?", genre, session["user_id"])
        db.execute("UPDATE users SET instruments = ? WHERE id = ?", instruments, session["user_id"])
        db.execute("UPDATE users SET status = ? WHERE id = ?", status, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("settings.html")


# Search for musicians by intrument and genre
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Page where you can search for certain musicians"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("search.html")

    # # User reached route via POST
    else:

        # Ensure primary instrument was submitted
        if not request.form.get("instrument"):
            return apology("must provide primary instrument", 400)

        # Ensure genre was submitted
        elif request.form.get("genre") == "Please select a genre":
            return apology("must provide genre", 400)

        instrument = request.form.get("instrument")
        instrument = instrument.lower()
        genre = request.form.get("genre")
        genre = genre.lower()

        # Search results filtered by instrument and genre
        results1 = db.execute("SELECT * FROM users WHERE primary_instrument = ? AND genre = ? AND id != ? AND status = ?", instrument, genre, session["user_id"], "active")
        results2 = db.execute("SELECT * FROM users WHERE primary_instrument = ? AND genre != ? AND id != ? AND status = ?", instrument, genre, session["user_id"], "active")
        results3 = db.execute("SELECT * FROM users WHERE primary_instrument != ? AND genre = ? AND id != ? AND status = ?", instrument, genre, session["user_id"], "active")
        results4 = db.execute("SELECT * FROM users WHERE instruments LIKE ? AND id != ? AND status = ?", "%" + instrument + "%", session["user_id"], "active")
        return render_template("searched.html", instrument=instrument, genre=genre, results1=results1, results2=results2, results3=results3, results4=results4)


# Show the user's group
@app.route("/groups")
@login_required
def groups():
    """View your groups"""

    # Query database for user's name
    name = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])
    name = name[0]["name"]

    # Find the group that the user is in
    groups = []
    rows = db.execute("SELECT * FROM groups")
    for row in rows:
        for key in row:
            if row[key] == name:
                groups.append(row)
                break

    return render_template("groups.html", groups=groups)


# Create a new group
@app.route("/creator", methods=["GET", "POST"])
@login_required
def creator():

    # User reached route via GET
    if request.method == "GET":
        return render_template("creator.html")

    # User reached route via POST
    else:
        # Ensure group name
        if not request.form.get("name"):
            return apology("must provide group name", 400)

        # Ensure genre was submitted
        elif request.form.get("genre") == "Please select a genre":
            return apology("must provide genre", 400)

        # Ensure you specificied what musicians you are looking for
        elif not request.form.get("looking_for"):
            return apology("must provide what you are looking for")

        name = request.form.get("name")
        genre = request.form.get("genre")
        looking_for = request.form.get("looking_for")
        member_1 = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])
        member_1 = member_1[0]["name"]

        # Query database for group name
        rows = db.execute("SELECT * FROM groups")
        names = []
        for row in rows:
            names.append(row['name'])

        # Ensure group name isn't already in use
        if name in names:
            return apology("This group name is already in use")

        # Ensure user isn't already in a group
        for row in rows:
            for key in row:
                if row[key] == member_1:
                    return apology("User can only be in one group at a time")

        # Insert user input into the groups table in SQL
        db.execute("INSERT INTO groups (name, genre, member_1, looking_for) VALUES (?, ?, ?, ?)", name, genre, member_1, looking_for)

        # Update user's group_id
        group_id = db.execute("SELECT id FROM groups WHERE member_1 = ?", member_1)
        group_id = group_id[0]["id"]
        db.execute("UPDATE users SET group_id = ? WHERE id = ?", group_id, session["user_id"])

        # Create list containing info about the user's group
        groups = []
        rows = db.execute("SELECT * FROM groups")
        for row in rows:
            for key in row:
                if row[key] == name:
                    groups.append(row)
                    break

        return render_template("groups.html", groups=groups)


# Add members to user's group
@app.route("/manager", methods=["GET", "POST"])
@login_required
def manager():

    # User reached route via GET
    if request.method == "GET":
        return render_template("manager.html")

    # User reached route via POST
    else:
        # Ensure name is input
        if not request.form.get("name"):
            return apology("must provide name", 400)

        name = request.form.get("name")

        # Ensure that the person being added exists
        check = []
        names = db.execute("SELECT name FROM users")
        for row in names:
            if row["name"] == name:
                check.append(name)
        if len(check) < 1:
            return apology("Must add somebody who has an account")

        # Ensure that the person being added is active
        status = db.execute("SELECT status FROM users WHERE name = ?", name)
        status = status[0]["status"]
        if status == "inactive":
            return apology("The desired account is inactive.")

        # Ensure that user is already in a group
        group_id = db.execute("SELECT group_id FROM users WHERE id = ?", session["user_id"])
        group_id = group_id[0]["group_id"]

        if group_id == None:
            return apology("You must be in a group to add people")

        # Ensure that the person being added isn't already in a group
        groups = db.execute("SELECT member_1, member_2, member_3, member_4, member_5, member_6 FROM groups")
        for group in groups:
            for key in group:
                if group[key] == name:
                    return apology("Person being added is already in a group")

        # Update the person's group id
        db.execute("UPDATE users SET group_id = ? WHERE name = ?", group_id, name)

        # Update group in database
        members = db.execute("SELECT member_2, member_3, member_4, member_5, member_6 FROM groups WHERE id = ?", group_id)
        for row in members:
            if row["member_2"] == None:
                db.execute("UPDATE groups SET member_2 = ? WHERE id = ?", name, group_id)
            elif row["member_3"] == None:
                db.execute("UPDATE groups SET member_3 = ? WHERE id = ?", name, group_id)
            elif row["member_4"] == None:
                db.execute("UPDATE groups SET member_4 = ? WHERE id = ?", name, group_id)
            elif row["member_5"] == None:
                db.execute("UPDATE groups SET member_5 = ? WHERE id = ?", name, group_id)
            elif row["member_6"] == None:
                db.execute("UPDATE groups SET member_6 = ? WHERE id = ?", name, group_id)
            else:
                return apology("Your group is full")

        return render_template("groups.html", groups=groups)


# Remove members from a group (the user can also use this page to leave the group)
@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():

    # Collect the user's group_id
    gp_id = []
    group = db.execute("SELECT group_id FROM users WHERE id = ?", session["user_id"])
    for row in group:
        gp_id.append(row["group_id"])
    if len(gp_id) > 0:
        group_id = gp_id[0]
    else:
        return apology("Must be in a group to remove people")

    # Collect the names of the group members
    members = db.execute("SELECT member_1, member_2, member_3, member_4, member_5, member_6 FROM groups WHERE id = ?", group_id)
    names = []
    for row in members:
        for key in row:
            names.append(row[key])

    # User reached route via GET
    if request.method == "GET":
        return render_template("remove.html", names=names)

    # User reached route via POST
    else:

        if request.form.get("name") == "Please select a member to remove":
            return apology("Please select a member to remove")

        n = []
        name_input = request.form.get("name")
        for row in members:
            n.append(row[name_input])
        if len(n) > 0:
            name = n[0]
        else:
            return apology("Please select a member to remove")

        # Update user table (in SQL)
        db.execute("UPDATE users SET group_id = ? WHERE name = ?", None, name)

        # Update group in database
        if names[0] == name:
            db.execute("UPDATE groups SET member_1 = ? WHERE id = ?", None, group_id)

        elif names[1] == name:
            db.execute("UPDATE groups SET member_2 = ? WHERE id = ?", None, group_id)

        elif names[2] == name:
            db.execute("UPDATE groups SET member_3 = ? WHERE id = ?", None, group_id)

        elif names[3] == name:
            db.execute("UPDATE groups SET member_4 = ? WHERE id = ?", None, group_id)

        elif names[4] == name:
            db.execute("UPDATE groups SET member_5 = ? WHERE id = ?", None, group_id)

        elif names[5] == name:
            db.execute("UPDATE groups SET member_6 = ? WHERE id = ?", None, group_id)

        # Collect the names of group members
        members = db.execute("SELECT member_1, member_2, member_3, member_4, member_5, member_6 FROM groups WHERE id = ?", group_id)
        names = []
        for row in members:
            for key in row:
                names.append(row[key])

        # If the group is empty, delete the group so new groups can use its name
        if names[0] == None and names[1] == None and names[2] == None and names[3] == None and names[4] == None and names[5] == None:
            db.execute("DELETE FROM groups WHERE id = ?", group_id)

        # Find the group that the user is in
        groups = []
        rows = db.execute("SELECT * FROM groups")
        for row in rows:
            for key in row:
                if row[key] == name:
                    groups.append(row)
                    break

        return render_template("groups.html", groups=groups)


# Browse active groups
@app.route("/browse")
@login_required
def browse():

    # Query database for info about all active groups
    groups = db.execute("SELECT name, genre, member_1, member_2, member_3, member_4, member_5, member_6, looking_for FROM groups")
    members = db.execute("SELECT member_1, member_2, member_3, member_4, member_5, member_6 FROM groups")

    # Collect the names of each group's members
    email_names = []
    for row in members:
        for key in row:
            if row[key] != None:
                email_names.append(row[key])
                break

    # Collect an email address from a member of the group
    emails = []
    for email_name in email_names:
        email = db.execute("SELECT email FROM users WHERE name = ?", email_name)
        email = email[0]["email"]
        emails.append(email)

    # Add emails to each library in groups
    for i in range(len(groups)):
        groups[i]["email"] = emails[i]

    return render_template("browse.html", groups=groups, emails=emails)
