import time
from typing import Any

from cs50 import SQL  # type: ignore
from flask import (  # noqa: F401
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,  # type: ignore
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers import Response as WerkzeugResponse

from flask_session import Session  # type: ignore
from helpers import login_required

# Configure application
app = Flask(__name__)

LEARNING_STEPS = [10, 60, 1440]  # minutes


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
            rows[0]["password_hash"],  # type: ignore
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
                "INSERT INTO users(username, password_hash) VALUES(?, ?)",
                username,
                password,  # type: ignore
            )
            flash("User has been created", "success")
            return render_template("login.html")

    else:
        return render_template("register.html")
    return None


@app.route("/decks")  # type: ignore
def decks() -> str:
    decks = db.execute(  # type: ignore
        "SELECT d.id, d.name, COUNT(c.id) AS card_count FROM decks d LEFT JOIN cards c "
        "ON c.deck_id = d.id WHERE d.user_id = ? GROUP BY d.id, d.name;",
        session["user_id"],
    )

    return render_template("decks.html", decks=decks)


@app.route("/api/create_decks", methods=["POST"])  # type: ignore
def create_deck() -> tuple[Response, Any]:
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Must provide name"}), 400

    db.execute(  # type: ignore
        "INSERT INTO decks(user_id, name) VALUES(?, ?)", session["user_id"], name
    )
    deck = db.execute(  # type: ignore
        "SELECT d.id, d.name, COUNT(c.id) AS card_count FROM decks d LEFT JOIN cards c "
        "ON c.deck_id = d.id WHERE d.user_id = ? GROUP BY d.id, d.name;",
        session["user_id"],
    )

    return jsonify(deck), 201


@app.route("/api/delete_deck/<int:deck_id>", methods=["DELETE"])
def delete_deck(deck_id: int) -> Response:
    db.execute(  # type: ignore
        "DELETE FROM decks WHERE user_id = ? AND id = ?", session["user_id"], deck_id
    )

    return jsonify({"success": True})


@app.route("/cards/<int:deck_id>")  # type: ignore
def cards(deck_id: int) -> WerkzeugResponse | str | None:
    cards = db.execute(  # type: ignore
        "SELECT id, front, back, deck_id FROM cards WHERE deck_id = ?", deck_id
    )

    return render_template("cards.html", cards=cards, deck_id=deck_id)


@app.route("/api/create_cards", methods=["POST"])  # type: ignore
def create_cards() -> tuple[Response, Any]:
    data = request.get_json()
    front = data.get("front")
    back = data.get("back")
    deck_id = data.get("deck_id")

    if not front or not back:
        return jsonify({"error": "Missing inputs"}), 400

    front = front.upper()
    back = back.upper()

    now = int(time.time())
    due = now + LEARNING_STEPS[0] * 60

    db.execute(  # type: ignore
        "INSERT INTO cards(deck_id, front, back, state, due) VALUES(?, ?, ?, ?, ?)",
        deck_id,
        front,
        back,
        "learning",
        due,  # type: ignore
    )
    cards = db.execute("SELECT * FROM cards WHERE deck_id = ?", deck_id)  # type: ignore

    return jsonify(cards), 201


@app.route("/api/delete_card/<int:card_id>", methods=["DELETE"])
def delete_card(card_id: int) -> Response:
    db.execute(  # type: ignore
        "DELETE FROM cards WHERE id = ?", card_id
    )

    return jsonify({"success": True})


@app.route("/api/search")
def search() -> Response:
    query = request.args.get("q")
    deck_id = request.args.get("deck_id")

    if query and deck_id:
        query = query.upper()
        cards = db.execute(  # type: ignore
            "SELECT front, back FROM cards WHERE deck_id = ? AND front LIKE ?",
            deck_id,
            "%" + query + "%",
        )
    else:
        cards = db.execute(  # type: ignore
            "SELECT front, back FROM cards WHERE deck_id = ?", deck_id
        )

    return jsonify(cards)


@app.route("/play/<int:deck_id>")  # type: ignore
def play(deck_id: int) -> WerkzeugResponse | str | None:
    return render_template("play.html")


if __name__ == "__main__":
    app.run(debug=True)  # noqa: S201
