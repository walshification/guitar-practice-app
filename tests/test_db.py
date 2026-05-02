from datetime import date, timedelta
from pathlib import Path

import pytest

import guitar.db as db


@pytest.fixture(autouse=True)
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(db, 'DB_DIR', tmp_path)
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / 'sessions.db')


def _insert(started_at: str, activity: str = 'timer', duration: int = 60) -> None:
    with db._connect() as conn:
        conn.execute(
            "INSERT INTO sessions (started_at, duration_seconds, activity)"
            " VALUES (?, ?, ?)",
            (started_at, duration, activity),
        )


# --- init_db / migrations ---

def test_init_db_creates_tables() -> None:
    db.init_db()
    with db._connect() as conn:
        tables = {
            r[0] for r in
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert 'sessions' in tables
    assert 'schema_version' in tables


def test_init_db_sets_schema_version() -> None:
    db.init_db()
    with db._connect() as conn:
        row = conn.execute("SELECT version FROM schema_version").fetchone()
    assert row['version'] == len(db.MIGRATIONS)


def test_init_db_idempotent() -> None:
    db.init_db()
    db.init_db()
    with db._connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
    assert count == 1


def test_migration_skips_already_applied(monkeypatch: pytest.MonkeyPatch) -> None:
    db.init_db()
    # Simulate a future migration being applied then rolled back in MIGRATIONS list
    extra = [(1, "SELECT 1")]  # version already applied — should be skipped
    monkeypatch.setattr(db, 'MIGRATIONS', extra)
    db.init_db()  # must not raise or duplicate schema_version rows
    with db._connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
    assert count == 1


def test_migration_upgrade_updates_version(monkeypatch: pytest.MonkeyPatch) -> None:
    db.init_db()
    upgraded = db.MIGRATIONS + [
        (2, "CREATE TABLE IF NOT EXISTS v2_test (id INTEGER)")
    ]
    monkeypatch.setattr(db, 'MIGRATIONS', upgraded)
    db.init_db()
    with db._connect() as conn:
        row = conn.execute("SELECT version FROM schema_version").fetchone()
    assert row['version'] == 2


# --- log_session / get_history ---

def test_log_session_inserts_row() -> None:
    db.log_session('scales', 120)
    rows = db.get_history()
    assert len(rows) == 1
    assert rows[0]['activity'] == 'scales'
    assert rows[0]['duration_seconds'] == 120


def test_log_session_notes_default_empty() -> None:
    db.log_session('scales', 60)
    rows = db.get_history()
    assert rows[0]['notes'] == ''


def test_log_session_with_notes() -> None:
    db.log_session('scales', 60, notes='felt good')
    rows = db.get_history()
    assert rows[0]['notes'] == 'felt good'


def test_get_history_ordered_descending() -> None:
    db.init_db()
    _insert('2024-01-01T10:00:00', activity='scales')
    _insert('2024-01-02T10:00:00', activity='timer')
    rows = db.get_history()
    assert rows[0]['activity'] == 'timer'
    assert rows[1]['activity'] == 'scales'


def test_get_history_limit() -> None:
    for i in range(5):
        db.log_session('scales', 60)
    rows = db.get_history(limit=3)
    assert len(rows) == 3


# --- get_streak ---

def test_get_streak_empty_db() -> None:
    db.init_db()
    assert db.get_streak() == 0


def test_get_streak_today_only() -> None:
    db.init_db()
    _insert(date.today().isoformat() + 'T10:00:00')
    assert db.get_streak() == 1


def test_get_streak_yesterday_only() -> None:
    db.init_db()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    _insert(yesterday + 'T10:00:00')
    assert db.get_streak() == 1


def test_get_streak_consecutive_days() -> None:
    db.init_db()
    for days_ago in range(3):
        d = (date.today() - timedelta(days=days_ago)).isoformat()
        _insert(d + 'T10:00:00')
    assert db.get_streak() == 3


def test_get_streak_breaks_on_gap() -> None:
    db.init_db()
    _insert(date.today().isoformat() + 'T10:00:00')
    # skip yesterday, add two days ago
    two_days_ago = (date.today() - timedelta(days=2)).isoformat()
    _insert(two_days_ago + 'T10:00:00')
    assert db.get_streak() == 1


def test_get_streak_multiple_sessions_same_day() -> None:
    db.init_db()
    today = date.today().isoformat()
    _insert(today + 'T09:00:00')
    _insert(today + 'T18:00:00')
    assert db.get_streak() == 1
