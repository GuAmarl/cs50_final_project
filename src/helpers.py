from collections.abc import Callable
from functools import wraps
from typing import Any

import requests
from flask import redirect, render_template, session


def apology(message: str, code: int = 400) -> tuple[Any, int]:
    """Render message as an apology to user."""

    def escape(s: str) -> str:
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


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


def lookup(symbol: str) -> dict[str, str | float] | None:
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper(),
        }  # type: ignore
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


def usd(value: float) -> str:
    """Format value as USD."""
    return f"${value:,.2f}"
