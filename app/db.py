import sqlite3
from flask import g, current_app

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL DEFAULT '',
        deadline TEXT NULL,
        tags TEXT NOT NULL DEFAULT '',
        recurrence TEXT NOT NULL DEFAULT 'none',
        is_completed INTEGER NOT NULL DEFAULT 0,
        is_archived INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Automatic column migrations for existing databases
    existing_columns = [
        row["name"] for row in db.execute("PRAGMA table_info(notes)").fetchall()
    ]
    if "tags" not in existing_columns:
        db.execute("ALTER TABLE notes ADD COLUMN tags TEXT NOT NULL DEFAULT ''")
    if "is_archived" not in existing_columns:
        db.execute("ALTER TABLE notes ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0")
    if "recurrence" not in existing_columns:
        db.execute("ALTER TABLE notes ADD COLUMN recurrence TEXT NOT NULL DEFAULT 'none'")

    db.commit()

def init_app_db(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
