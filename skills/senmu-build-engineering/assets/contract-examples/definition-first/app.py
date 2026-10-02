"""Definition-first WSGI provider, deliberately independent of schema validation."""
import json
from store import save, load


def create_app(database):
    def application(environ, start_response):
        method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
        status, body = "404 Not Found", {"detail": "missing item"}
        if method == "POST" and path == "/items":
            try:
                request = json.loads(environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)))
            except (ValueError, TypeError):
                request = None
            if (not isinstance(request, dict) or not isinstance(request.get("name"), str)
                    or not request["name"] or set(request) - {"name", "note"}
                    or (request.get("note") is not None and not isinstance(request["note"], str))):
                status, body = "400 Bad Request", {"detail": "invalid input"}
            else:
                status, body = "201 Created", save(database, request["name"], request.get("note"))
        elif method == "GET" and path.startswith("/items/"):
            found = load(database, path.removeprefix("/items/"))
            if found:
                status, body = "200 OK", found
        data = json.dumps(body).encode()
        start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(data)))])
        return [data]
    return application
