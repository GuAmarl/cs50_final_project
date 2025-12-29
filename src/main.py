from typing import Any

from cs50 import SQL  # type: ignore
from flask import Flask, Response, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers import Response as WerkzeugResponse

from flask_session import Session  # type: ignore
from helpers import login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cards.db")


@app.after_request
def after_request(response: Response) -> Response:
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index() -> str:
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login() -> str | WerkzeugResponse | tuple[Any, int]:
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", "danger")
            return render_template("login.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Must provide password", "danger")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(  # type: ignore
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(  # type: ignore
            rows[0]["hash"],  # type: ignore
            request.form.get("password"),  # type: ignore
        ):
            flash("Invalid username and/or password", "danger")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("You were successfully logged in", "success")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout() -> WerkzeugResponse:
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])  # type: ignore
def register() -> WerkzeugResponse | str | None:
    """Register user"""

    if request.method == "POST":
        # Get and check form variables
        username = request.form.get("username")
        if not username:
            flash("Must provide username", "danger")
            return render_template("register.html")

        # Checks if user already exists
        user_exists = db.execute("SELECT id FROM users WHERE username = ?", username)  # type: ignore
        if user_exists:
            flash("User already exists", "danger")
            return render_template("register.html")

        password = request.form.get("password")
        if not password:
            flash("Must provide password", "danger")
            return render_template("register.html")

        password = generate_password_hash(password)  # type: ignore

        confirmation = request.form.get("confirmation")
        if not confirmation:
            flash("Must provide confirmation password", "danger")
            return render_template("register.html")

        if not check_password_hash(password, confirmation):  # type: ignore
            flash("Passwords must match", "danger")
            return render_template("register.html")

        # If user doesn't exists, create one
        if not user_exists:
            db.execute(  # type: ignore
                "INSERT INTO users(username, hash) VALUES(?, ?)",
                username,
                password,  # type: ignore
            )
            flash("User has been created", "success")
            return render_template("login.html")

    else:
        return render_template("register.html")
    return None


if __name__ == "__main__":
    app.run(debug=True)  # noqa: S201
