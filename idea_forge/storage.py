"""SQLite persistence. The score is not stored."""

import datetime
import os
import sqlite3
import threading

_LOCK = threading.Lock()

STATUSES = ("new", "kept", "parked", "dismissed")

STATUS_LABELS = (
    ("new", "New"),
    ("kept", "Kept"),
    ("parked", "Parked"),
    ("dismissed", "Dismissed"),
)


def resolve_db_path():
    return os.environ.get("IDEA_FORGE_DB", os.path.join("instance", "idea_forge.sqlite"))


def connect(path):
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id TEXT NOT NULL,
                pattern_id TEXT NOT NULL,
                twist_id TEXT NOT NULL,
                name TEXT NOT NULL,
                pitch TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL,
                UNIQUE (problem_id, pattern_id, twist_id)
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_ideas(path):
    conn = connect(path)
    try:
        return conn.execute(
            "SELECT id, problem_id, pattern_id, twist_id, name, pitch, status, created_at "
            "FROM ideas ORDER BY id ASC"
        ).fetchall()
    finally:
        conn.close()


def get_idea(path, idea_id):
    conn = connect(path)
    try:
        return conn.execute(
            "SELECT id, problem_id, pattern_id, twist_id, name, pitch, status, created_at "
            "FROM ideas WHERE id = ?",
            (idea_id,),
        ).fetchone()
    finally:
        conn.close()


def count_ideas(path):
    conn = connect(path)
    try:
        row = conn.execute("SELECT COUNT(*) AS n FROM ideas").fetchone()
        return int(row["n"])
    finally:
        conn.close()


def insert_idea(path, spec):
    created = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with _LOCK:
        conn = connect(path)
        try:
            cursor = conn.execute(
                "INSERT INTO ideas ("
                "problem_id, pattern_id, twist_id, name, pitch, status, created_at"
                ") VALUES (?, ?, ?, ?, ?, 'new', ?)",
                (
                    spec["problem_id"],
                    spec["pattern_id"],
                    spec["twist_id"],
                    spec["name"],
                    spec["pitch"],
                    created,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()


def set_status(path, idea_id, status):
    if status not in STATUSES:
        return False
    with _LOCK:
        conn = connect(path)
        try:
            cursor = conn.execute(
                "UPDATE ideas SET status = ? WHERE id = ?",
                (status, idea_id),
            )
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()


def _format_stored(number):
    value = float(number)
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return repr(value)


def get_weights(path):
    conn = connect(path)
    try:
        rows = conn.execute(
            "SELECT key, value FROM settings WHERE key IN "
            "('weight_impact', 'weight_portfolio', 'weight_feasibility')"
        ).fetchall()
    finally:
        conn.close()
    found = dict((row["key"], row["value"]) for row in rows)
    if not found:
        return (45, 25, 30)

    def read(key, default):
        raw = found.get(key)
        if raw is None:
            return default
        return float(raw)

    return (
        read("weight_impact", 45),
        read("weight_portfolio", 25),
        read("weight_feasibility", 30),
    )


def set_weights(path, impact, portfolio, feasibility):
    pairs = (
        ("weight_impact", _format_stored(impact)),
        ("weight_portfolio", _format_stored(portfolio)),
        ("weight_feasibility", _format_stored(feasibility)),
    )
    with _LOCK:
        conn = connect(path)
        try:
            for key, value in pairs:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, value),
                )
            conn.commit()
        finally:
            conn.close()
