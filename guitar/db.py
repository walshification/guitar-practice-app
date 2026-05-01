import sqlite3
from datetime import date, datetime
from pathlib import Path

DB_DIR = Path.home() / '.guitar-practice'
DB_PATH = DB_DIR / 'sessions.db'


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id              INTEGER PRIMARY KEY,
                started_at      TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                activity        TEXT NOT NULL,
                notes           TEXT DEFAULT ''
            )
        """)


def log_session(activity: str, duration_seconds: int, notes: str = '') -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO sessions (started_at, duration_seconds, activity, notes)"
            " VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), duration_seconds, activity, notes),
        )


def get_history(limit: int = 20) -> list[sqlite3.Row]:
    init_db()
    with _connect() as conn:
        return conn.execute(
            "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()


def get_streak() -> int:
    """Return the number of consecutive days (ending today) with at least one session.
    """
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT date(started_at) as day FROM sessions ORDER BY day DESC"
        ).fetchall()

    if not rows:
        return 0

    days = [date.fromisoformat(r['day']) for r in rows]
    streak = 0
    current = date.today()

    for day in days:
        if day == current:
            streak += 1
            current = date.fromordinal(current.toordinal() - 1)
        elif day == date.fromordinal(current.toordinal() - 1):
            # yesterday counts even if today hasn't been practiced yet
            streak += 1
            current = day
            current = date.fromordinal(current.toordinal() - 1)
        else:
            break

    return streak
