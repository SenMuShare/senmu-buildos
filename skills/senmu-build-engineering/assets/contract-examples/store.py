"""Synthetic local SQLite store; never open a user's database."""
import sqlite3
from uuid import uuid4


def save(path, name, note):
    item = {"id": str(uuid4()), "name": name, "note": note}
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, name TEXT NOT NULL, note TEXT)")
        db.execute("INSERT INTO items VALUES (?, ?, ?)", (item["id"], name, note))
    return item


def load(path, item_id):
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, name TEXT NOT NULL, note TEXT)")
        row = db.execute("SELECT id, name, note FROM items WHERE id = ?", (item_id,)).fetchone()
    return dict(zip(("id", "name", "note"), row)) if row else None
