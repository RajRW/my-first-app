"""Backend for My First App: a tiny to-do list.

Uses only Python's standard library, so there is nothing to install.
It does three jobs:
  1. stores tasks in a small database file (SQLite)
  2. answers API requests from the frontend (/api/tasks)
  3. serves the frontend files (HTML, CSS, JavaScript)

Run it with:  python backend/server.py
Then open:    http://localhost:8010
"""

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"
DB_PATH = ROOT / "data" / "tasks.db"
PORT = 8010

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


# ---------- Database: the only code that touches the tasks table ----------

def connect(db_path=DB_PATH):
    """Open the database, creating the file and the table if they don't exist."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    db.execute(
        "CREATE TABLE IF NOT EXISTS tasks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "title TEXT NOT NULL, "
        "done INTEGER NOT NULL DEFAULT 0)"
    )
    return db


def to_dict(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def list_tasks(db):
    rows = db.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [to_dict(row) for row in rows]


def get_task(db, task_id):
    row = db.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    return to_dict(row) if row else None


def add_task(db, title):
    title = title.strip()
    if not title:
        raise ValueError("A task needs a title.")
    cursor = db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    db.commit()
    return get_task(db, cursor.lastrowid)


def set_done(db, task_id, done):
    db.execute("UPDATE tasks SET done = ? WHERE id = ?", (int(bool(done)), task_id))
    db.commit()
    return get_task(db, task_id)


def delete_task(db, task_id):
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return cursor.rowcount > 0


def clear_done(db):
    """Delete every finished task. Returns how many were removed."""
    cursor = db.execute("DELETE FROM tasks WHERE done = 1")
    db.commit()
    return cursor.rowcount


# ---------- Web server: turns browser requests into database calls ----------

class Handler(BaseHTTPRequestHandler):
    db_path = DB_PATH

    def do_GET(self):
        if self.path == "/api/tasks":
            with self.open_db() as db:
                self.send_json(200, list_tasks(db))
        else:
            self.send_file()

    def do_POST(self):
        if self.path != "/api/tasks":
            return self.send_json(404, {"error": "Not found"})
        body = self.read_json()
        if body is None:
            return
        try:
            with self.open_db() as db:
                task = add_task(db, str(body.get("title", "")))
        except ValueError as error:
            return self.send_json(400, {"error": str(error)})
        self.send_json(201, task)

    def do_PATCH(self):
        task_id = self.task_id_from_path()
        if task_id is None:
            return self.send_json(404, {"error": "Not found"})
        body = self.read_json()
        if body is None:
            return
        with self.open_db() as db:
            task = set_done(db, task_id, body.get("done", False))
        if task is None:
            return self.send_json(404, {"error": "No such task"})
        self.send_json(200, task)

    def do_DELETE(self):
        if self.path == "/api/tasks/done":
            with self.open_db() as db:
                return self.send_json(200, {"cleared": clear_done(db)})
        task_id = self.task_id_from_path()
        if task_id is None:
            return self.send_json(404, {"error": "Not found"})
        with self.open_db() as db:
            deleted = delete_task(db, task_id)
        if not deleted:
            return self.send_json(404, {"error": "No such task"})
        self.send_json(200, {"deleted": task_id})

    # ----- helpers -----

    def open_db(self):
        return _ClosingConnection(connect(self.db_path))

    def task_id_from_path(self):
        """'/api/tasks/7' -> 7, anything else -> None."""
        prefix = "/api/tasks/"
        if self.path.startswith(prefix) and self.path[len(prefix):].isdigit():
            return int(self.path[len(prefix):])
        return None

    def read_json(self):
        """Read the request body as a JSON object. Replies 400 and returns None if it isn't one."""
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            body = None
        if not isinstance(body, dict):
            self.send_json(400, {"error": "Expected a JSON object"})
            return None
        return body

    def send_json(self, status, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self):
        """Serve a file from the frontend folder ('/' means index.html)."""
        name = self.path.split("?")[0].lstrip("/") or "index.html"
        file_path = (FRONTEND_DIR / name).resolve()
        # Never serve anything outside the frontend folder.
        if FRONTEND_DIR not in file_path.parents or not file_path.is_file():
            return self.send_json(404, {"error": "Not found"})
        payload = file_path.read_bytes()
        self.send_response(200)
        self.send_header(
            "Content-Type", CONTENT_TYPES.get(file_path.suffix, "application/octet-stream")
        )
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class _ClosingConnection:
    """Lets us write `with self.open_db() as db:` and have the database closed afterwards."""

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self.db

    def __exit__(self, *exc):
        self.db.close()


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"My First App is running at http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
