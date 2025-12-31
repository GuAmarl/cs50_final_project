import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from cs50 import SQL  # type: ignore
from flask import Config, redirect, session


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# AGAIN (grade = 0)  # noqa: ERA001
# User completely failed the card
def handle_again(config: Config, card: dict[str, Any], now: int) -> dict[str, Any]:
    # Penalize ease but never below minimum
    ease = max(config["MIN_EASE"], card["ease"] - 0.2)  # type: ignore

    # Move card to relearning phase
    # First relearning step for interval
    # Reset repetitions (card is no longer stable)
    return {
        "state": "relearning",
        "step": 0,
        "interval": config["RELEARNING_STEPS"][0],
        "ease": ease,
        "repetitions": 0,
        "due": now + config["RELEARNING_STEPS"][0],
    }


# HARD (grade = 1)  # noqa: ERA001
# User recalled with difficulty
def handle_hard(config: Config, card: dict[str, Any], now: int) -> dict[str, Any]:
    ease = max(config["MIN_EASE"], card["ease"] - 0.15)  # type: ignore

    if card["state"] in ("learning", "relearning"):
        # Stay on the same step
        step = min(card["step"], len(config["LEARNING_STEPS"]) - 1)  # type: ignore
        interval = config["LEARNING_STEPS"][step]  # type: ignore
        reps = card["repetitions"]
    else:
        # Review card: small interval increase
        interval = int(card["interval"] * 1.2)
        # Ensure repetitions is valid for SM-2 logic
        reps = max(1, card["repetitions"])
        step = card["step"]

    return {
        "state": card["state"],
        "step": step,
        "interval": interval,
        "ease": ease,
        "repetitions": reps,
        "due": now + interval,
    }


# GOOD (grade = 2)  # noqa: ERA001
# User recalled correctly
def handle_good(config: Config, card: dict[str, Any], now: int) -> dict[str, Any]:
    if card["state"] in ("learning", "relearning"):
        step = card["step"] + 1
        steps = (  # type: ignore
            config["LEARNING_STEPS"]
            if card["state"] == "learning"
            else config["RELEARNING_STEPS"]
        )

        if step < len(steps):  # type: ignore
            # Continue learning steps
            return {
                "state": card["state"],
                "step": step,
                "interval": steps[step],
                "ease": card["ease"],
                "repetitions": card["repetitions"],
                "due": now + steps[step],
            }

        # Graduate to review
        return {
            "state": "review",
            "step": 0,
            "interval": steps[-1],
            "ease": card["ease"],
            "repetitions": 1,
            "due": now + steps[-1],
        }

    # Review logic (SM-2 inspired)
    reps = card["repetitions"]
    if reps == 1:
        interval = 86400
    elif reps == 2:
        interval = 86400 * 6
    else:
        interval = int(card["interval"] * card["ease"])

    return {
        "state": "review",
        "step": 0,
        "interval": interval,
        "ease": card["ease"],
        "repetitions": reps + 1,
        "due": now + interval,
    }


# EASY (grade = 3)  # noqa: ERA001
# User recalled effortlessly
def handle_easy(config: Config, card: dict[str, Any], now: int) -> dict[str, Any]:
    # Reward ease
    ease = max(config["MIN_EASE"], card["ease"] + 0.15)  # type: ignore

    if card["state"] in ("learning", "relearning"):
        # Skip remaining steps and go directly to review
        interval = config["LEARNING_STEPS"][-1] * 2  # type: ignore
        return {
            "state": "review",
            "step": 0,
            "interval": interval,
            "ease": ease,
            "repetitions": 1,
            "due": now + interval,
        }

    # Strong growth for review cards
    interval = int(card["interval"] * ease * 1.3)
    return {
        "state": "review",
        "step": card["step"],
        "interval": interval,
        "ease": ease,
        "repetitions": card["repetitions"] + 1,
        "due": now + interval,
    }


def update_card(config: Config, db: SQL, card_id: int, grade: int) -> str:  # type: ignore
    """
    Update a flashcard scheduling parameters based on user feedback.

    Grades:
        0 = Again
        1 = Hard
        2 = Good
        3 = Easy

    Card states:
        - learning   : initial learning phase
        - review     : spaced repetition (SM-2 based)
        - relearning : after a lapse (Again in review)
    """

    now = int(time.time())

    # Load card current state
    card = db.execute(  # type: ignore
        """
        SELECT state, step, interval, ease, repetitions
        FROM cards
        WHERE id = ?
        """,
        card_id,
    )[0]

    if not card:
        return "ERROR"

    card: dict[str, Any] = dict(card)  # type: ignore

    handlers = {
        0: handle_again,
        1: handle_hard,
        2: handle_good,
        3: handle_easy,
    }

    handler = handlers.get(grade)
    if not handler:
        return "INVALID_GRADE"

    updated = handler(config, card, now)

    # Persist changes
    db.execute(  # type: ignore
        """
        UPDATE cards
        SET
            state = ?,
            step = ?,
            interval = ?,
            ease = ?,
            repetitions = ?,
            due = ?,
            last_review = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        updated["state"],
        updated["step"],
        updated["interval"],
        updated["ease"],
        updated["repetitions"],
        updated["due"],
        now,
        card_id,
    )

    return "SUCCESS"
