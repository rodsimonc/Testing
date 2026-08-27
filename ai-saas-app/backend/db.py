import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "app.db"


def init():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            input_text TEXT NOT NULL,
            summary TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)


@contextmanager
def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def create_user(email: str) -> tuple[int, str]:
    api_key = "sk_" + secrets.token_urlsafe(24)
    with connect() as con:
        cur = con.execute("INSERT INTO users (email, api_key) VALUES (?, ?)", (email, api_key))
        return cur.lastrowid, api_key


def user_from_key(api_key: str) -> sqlite3.Row | None:
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE api_key = ?", (api_key,)).fetchone()
        return row


def save_summary(user_id: int, input_text: str, summary: str) -> int:
    with connect() as con:
        cur = con.execute(
            "INSERT INTO summaries (user_id, input_text, summary) VALUES (?, ?, ?)",
            (user_id, input_text, summary),
        )
        return cur.lastrowid


def list_summaries(user_id: int, limit: int = 20) -> list[sqlite3.Row]:
    with connect() as con:
        return con.execute(
            "SELECT id, summary, created_at FROM summaries WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
