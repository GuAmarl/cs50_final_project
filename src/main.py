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
from helpers import login_required, update_card  # type: ignore

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cards.db")


# session["LEARNING_STEPS"] = [600, 86400]  # 10 min, 1 day
# session["RELEARNING_STEPS"] = [600]  # 10 min
# session["MIN_EASE"] = 1.3


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
    session["LEARNING_STEPS"] = [600, 86400]  # 10 min, 1 day
    session["RELEARNING_STEPS"] = [600]  # 10 min
    session["MIN_EASE"] = 1.3
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
    # decks = db.execute(  # type: ignore
    #     "SELECT d.id, d.name, COUNT(c.id) AS card_count FROM decks d LEFT JOIN cards c "
    #     "ON c.deck_id = d.id WHERE d.user_id = ? GROUP BY d.id, d.name;",
    #     session["user_id"],
    # )

    decks = db.execute(  # type: ignore
        """SELECT
            d.id,
            d.name,

            COUNT(c.id) AS card_count,

            COUNT(
                CASE
                    WHEN c.due <= strftime('%s', 'now') THEN 1
                END
            ) AS num_play_cards

        FROM decks d
        LEFT JOIN cards c ON c.deck_id = d.id
        WHERE d.user_id = ?
        GROUP BY d.id, d.name""",
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
    due = now + session["LEARNING_STEPS"][0] * 60

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
    cards_to_play = db.execute(  # type: ignore
        "SELECT c.id, c.deck_id, d.name, c.front, c.back, c.state "
        "FROM cards as c JOIN decks as d "
        "ON c.deck_id = d.id WHERE deck_id = ? "
        "AND due <= strftime('%s', 'now') ORDER BY due LIMIT 1",
        deck_id,
    )

    if cards_to_play:
        cards_to_play = cards_to_play[0]  # type: ignore

    num_cards = int(
        db.execute(  # type: ignore
            "SELECT COUNT(*) as num FROM cards "
            "WHERE deck_id = ? "
            "AND due <= strftime('%s', 'now')",
            deck_id,
        )[0]["num"]
    )

    return render_template(
        "play.html", cards_to_play=cards_to_play, num_cards=num_cards
    )


@app.route("/api/play_cards", methods=["POST"])
def play_cards() -> Response | tuple[Response, Any]:
    data = request.get_json()
    grade = data.get("grade")
    card_id = data.get("card_id")
    deck_id = data.get("deck_id")

    if grade not in (0, 1, 2, 3):
        return jsonify({"error": "Invalid grade"}), 400

    grade = int(grade)
    card_id = int(card_id)
    deck_id = int(deck_id)

    update_card(db, card_id, grade)

    cards_to_play = db.execute(  # type: ignore
        "SELECT c.id, d.name, c.front, c.back, c.state FROM cards as c JOIN decks as d "
        "ON c.deck_id = d.id WHERE deck_id = ? "
        "AND due <= strftime('%s', 'now') ORDER BY due LIMIT 1",
        deck_id,
    )

    if not cards_to_play:
        return jsonify({"done": True})

    return jsonify(cards_to_play[0])


if __name__ == "__main__":
    app.run(debug=True)  # noqa: S201
