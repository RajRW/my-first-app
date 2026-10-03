"""Tests for the backend. Run with:  python -m unittest discover backend"""

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import server


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db = server.connect(Path(self.folder.name) / "test.db")

    def tearDown(self):
        self.db.close()
        self.folder.cleanup()

    def test_starts_empty(self):
        self.assertEqual(server.list_tasks(self.db), [])

    def test_add_task(self):
        task = server.add_task(self.db, "  Buy milk  ")
        self.assertEqual(task, {"id": 1, "title": "Buy milk", "done": False})
        self.assertEqual(server.list_tasks(self.db), [task])

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValueError):
            server.add_task(self.db, "   ")

    def test_mark_done(self):
        task = server.add_task(self.db, "Buy milk")
        self.assertTrue(server.set_done(self.db, task["id"], True)["done"])
        self.assertFalse(server.set_done(self.db, task["id"], False)["done"])

    def test_delete(self):
        task = server.add_task(self.db, "Buy milk")
        self.assertTrue(server.delete_task(self.db, task["id"]))
        self.assertFalse(server.delete_task(self.db, task["id"]))
        self.assertEqual(server.list_tasks(self.db), [])

    def test_clear_done_removes_only_finished_tasks(self):
        milk = server.add_task(self.db, "Buy milk")
        bread = server.add_task(self.db, "Buy bread")
        server.set_done(self.db, milk["id"], True)
        self.assertEqual(server.clear_done(self.db), 1)
        self.assertEqual(server.list_tasks(self.db), [bread])


class ApiTests(unittest.TestCase):
    """Starts the real web server on a spare port and talks to it like a browser would."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()

        class TestHandler(server.Handler):
            db_path = Path(self.folder.name) / "test.db"

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.folder.cleanup()

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self.url + path, data=data, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_full_life_of_a_task(self):
        self.assertEqual(self.call("GET", "/api/tasks"), (200, []))

        status, task = self.call("POST", "/api/tasks", {"title": "Learn Git"})
        self.assertEqual(status, 201)
        self.assertEqual(task["title"], "Learn Git")

        status, task = self.call("PATCH", f"/api/tasks/{task['id']}", {"done": True})
        self.assertEqual((status, task["done"]), (200, True))

        status, _ = self.call("DELETE", f"/api/tasks/{task['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(self.call("GET", "/api/tasks"), (200, []))

    def test_clear_finished(self):
        _, done = self.call("POST", "/api/tasks", {"title": "Learn Git"})
        _, todo = self.call("POST", "/api/tasks", {"title": "Learn GitHub"})
        self.call("PATCH", f"/api/tasks/{done['id']}", {"done": True})

        self.assertEqual(self.call("DELETE", "/api/tasks/done"), (200, {"cleared": 1}))
        self.assertEqual(self.call("GET", "/api/tasks"), (200, [todo]))

    def test_blank_title_gives_400(self):
        status, body = self.call("POST", "/api/tasks", {"title": ""})
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_unknown_task_gives_404(self):
        self.assertEqual(self.call("DELETE", "/api/tasks/999")[0], 404)
        self.assertEqual(self.call("PATCH", "/api/tasks/999", {"done": True})[0], 404)

    def test_serves_the_frontend(self):
        with urllib.request.urlopen(self.url + "/") as response:
            self.assertIn("text/html", response.headers["Content-Type"])

    def test_does_not_serve_files_outside_frontend(self):
        self.assertEqual(self.call("GET", "/../backend/server.py")[0], 404)


if __name__ == "__main__":
    unittest.main()
