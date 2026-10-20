"""Database management and SQLite connection utilities."""

import sqlite3
from pathlib import Path
from typing import Generator
from config.settings import DATABASE_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Return an open SQLite connection with Row factory, foreign keys, and busy timeout."""
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path = DATABASE_PATH, reset: bool = False) -> None:
    """Initialize or reset the SQLite database using schema.sql."""
    conn = get_db_connection(db_path)
    if reset:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = OFF;")
        # Fetch all existing tables and drop them
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row["name"] for row in cur.fetchall()]
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table};")
        conn.commit()
        cur.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
