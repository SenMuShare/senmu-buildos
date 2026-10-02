"""Synthetic local HTTP workspace. Not a general OpenAPI validator or model result."""
from pathlib import Path
import json
import sys

SCHEMA = {"type": "object", "required": ["id", "name"], "properties": {
    "id": {"type": "string"}, "name": {"type": "string"}}}
SPEC = {"openapi": "3.0.3", "info": {"title": "Synthetic item API", "version": "1.0.0"},
    "paths": {"/items": {"post": {"operationId": "createItem", "requestBody": {
        "required": True, "content": {"application/json": {"schema": {
            "type": "object", "required": ["name"], "properties": {"name": {"type": "string", "minLength": 1}}}}}},
        "responses": {"201": {"description": "Saved item", "content": {"application/json": {"schema": SCHEMA}}},
                      "400": {"description": "Invalid name"}}}},
        "/items/{item_id}": {"get": {"operationId": "getItem", "parameters": [
            {"name": "item_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {"200": {"description": "Saved item", "content": {"application/json": {"schema": SCHEMA}}},
                          "404": {"description": "Unknown item"}}}}}}
FILES = {
    "AGENTS.md": """# Synthetic project rules
Use governance/PROJECT_MAP.md when the owner is unknown. Before shared-interface changes, find its maintenance source, affected consumers and real checks. Keep proposed and current behavior distinct; do not edit a contract merely to pass a test.
This is an exclusive disposable workspace. Local edits and loopback tests are authorized. No commits, installation, public network calls or releases are authorized. Existing API and legacy behavior must be preserved unless the task explicitly changes them.
""",
    "CLAUDE.md": "@AGENTS.md\n",
    "README.md": "# Item fixture\nRun python3 -m unittest discover -s tests -p 'test_*.py'.\n",
    "governance/PROJECT_MAP.md": """# Map
## 责任与入口地图
| Capability | Responsibility | Implementation | Contract | Verification | State/delivery |
| --- | --- | --- | --- | --- | --- |
| Item creation | create a retrievable item | `server.py` | [API](../api/openapi.json#/paths/~1items/post) | `tests/test_api.py` | in-memory fixture store |
| Page styling | style a static page | `web/style.css` | `web/README.md` | `web/README.md` | static page |
""",
    "api/openapi.json": json.dumps(SPEC, indent=2)+"\n",
    "api/README.md": "Definition-first: openapi.json is the effective contract. No generated client is maintained. createItem returns a saved item with a string id; getItem must retrieve it. Tests use specific assertions for this fixture, not general schema validation.\n",
    "server.py": '''import json
ITEMS = {}

def application(environ, start_response):
    method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
    status, body = "404 Not Found", {"error": "not_found"}
    if method == "POST" and path == "/items":
        try:
            request = json.loads(environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)))
        except (ValueError, TypeError):
            request = {}
        if not isinstance(request, dict) or not isinstance(request.get("name"), str) or not request["name"]:
            status, body = "400 Bad Request", {"error": "invalid_name"}
        else:
            item_id = str(len(ITEMS) + 1)
            ITEMS[item_id] = {"id": item_id, "name": request["name"]}
            status, body = "201 Created", {"id": len(ITEMS), "name": request["name"]}
    elif method == "GET" and path.startswith("/items/") and path.removeprefix("/items/") in ITEMS:
        status, body = "200 OK", ITEMS[path.removeprefix("/items/")]
    data = json.dumps(body).encode()
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(data)))])
    return [data]
''',
    "legacy.py": "# Approved unchanged compatibility owner.\ndef legacy_id():\n    return 17\n",
    "web/style.css": ".card { padding: 8px; }\n",
    "web/README.md": "Static fixture: preserve HTML semantics. No HTTP API is needed for a spacing change. Check the changed CSS and report no browser rendering evidence when unavailable.\n",
    "tests/test_api.py": '''import json
from pathlib import Path
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server, WSGIRequestHandler
from server import application, ITEMS

class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass

class ActualApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = make_server("127.0.0.1", 0, application, handler_class=QuietHandler)
        cls.thread = Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.http.server_port)
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.thread.join(timeout=5); cls.http.server_close()
    def setUp(self):
        ITEMS.clear()
    def request(self, name):
        return Request(self.base+"/items", data=json.dumps({"name": name}).encode(),
                       headers={"Content-Type": "application/json"}, method="POST")
    def test_real_response_matches_agreed_identifier(self):
        spec = json.loads(Path("api/openapi.json").read_text())
        agreed = spec["paths"]["/items"]["post"]["responses"]["201"]["content"]["application/json"]["schema"]
        self.assertEqual(agreed["properties"]["id"]["type"], "string")
        with urlopen(self.request("sample"), timeout=5) as response:
            self.assertEqual(response.status, 201)
            actual = json.load(response)
        self.assertIsInstance(actual["id"], str)
        self.assertEqual(actual["name"], "sample")
    def test_success_means_retrievable_data(self):
        with urlopen(self.request("saved"), timeout=5) as response:
            created = json.load(response)
        with urlopen(self.base+"/items/"+str(created["id"]), timeout=5) as response:
            self.assertEqual(json.load(response)["name"], "saved")
    def test_validation_failure_preserves_empty_store(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.request(""), timeout=5)
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(ITEMS, {})
if __name__ == "__main__":
    unittest.main()
''',
}

def create(root: Path) -> None:
    root = root.resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError("fixture requires an empty directory")
    root.mkdir(parents=True, exist_ok=True)
    for relative, body in FILES.items():
        path = root/relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(body)

if __name__ == "__main__":
    create(Path(sys.argv[1]))
