#!/usr/bin/env python3
"""Opt-in example pipelines. Dependencies must already be installed; no network setup.

Default checks regenerate into a temporary directory and do not repair source artifacts.
Only --generate writes the selected example's two generated artifacts.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
from threading import Thread
import time
from wsgiref.simple_server import make_server, WSGIRequestHandler

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
MODES = ("definition-first", "declaration-first")


class CheckFailure(RuntimeError):
    def __init__(self, stage: str, detail: str):
        super().__init__(f"{stage}: {detail}")
        self.stage = stage


def run(command: list[str], stage: str, cwd: Path) -> str:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=60,
                                env={**os.environ, "REDOCLY_TELEMETRY": "off", "PYTHONDONTWRITEBYTECODE": "1"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckFailure(stage, str(exc)) from exc
    if result.returncode:
        raise CheckFailure(stage, result.stdout + result.stderr)
    return result.stdout


def prepare(mode: str, temporary: Path, *, generate: bool = False) -> Path:
    """Delegate parsing, complete local references and type generation to mature tools."""
    if mode not in MODES:
        raise ValueError("unknown example")
    for tool in ("redocly", "openapi-typescript", "tsc", "node"):
        if shutil.which(tool) is None:
            raise CheckFailure("tools", f"{tool} is unavailable; no checks claimed")
    config = str(ROOT / "redocly.yaml")
    source = ROOT / mode / "openapi.yaml"
    if mode == "declaration-first":
        source = temporary / "declared.json"
        source.write_text(run([sys.executable, str(ROOT / mode / "app.py")], "export", ROOT), encoding="utf-8")
    run(["redocly", "lint", str(source), "--config", config], "definition", ROOT)
    bundled = temporary / "openapi.json"
    run(["redocly", "bundle", str(source), "--output", str(bundled), "--ext", "json", "--config", config], "bundle", ROOT)
    bundled.write_text(json.dumps(json.loads(bundled.read_text()), sort_keys=True, indent=2) + "\n", encoding="utf-8")
    types = temporary / "api.d.ts"
    run(["openapi-typescript", str(bundled), "--output", str(types), "--redocly", config], "generate-types", ROOT)
    output = ROOT / mode / "generated"
    for fresh, stage in ((bundled, "contract-drift"), (types, "client-drift")):
        target = output / fresh.name
        if generate:
            output.mkdir(exist_ok=True)
            target.write_bytes(fresh.read_bytes())
        elif not target.is_file() or target.read_bytes() != fresh.read_bytes():
            raise CheckFailure(stage, f"{mode}/generated/{fresh.name} is stale; update the maintenance source, then regenerate")
    return bundled


@contextmanager
def server(mode: str, database: Path):
    spec = importlib.util.spec_from_file_location("contract_example_app", ROOT / mode / "app.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.create_app(database)
    if mode == "definition-first":
        class QuietHandler(WSGIRequestHandler):
            def log_message(self, *args):
                pass
        http = make_server("127.0.0.1", 0, app, handler_class=QuietHandler)
        thread = Thread(target=http.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{http.server_port}"
        finally:
            http.shutdown()
            thread.join(timeout=5)
            http.server_close()
    else:
        import uvicorn
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            http = uvicorn.Server(uvicorn.Config(app, log_level="error", lifespan="off", ws="none"))
            thread = Thread(target=http.run, kwargs={"sockets": [sock]}, daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 5
                while not http.started and thread.is_alive() and time.monotonic() < deadline:
                    time.sleep(0.01)
                if not http.started:
                    raise CheckFailure("server", "loopback server did not start")
                yield f"http://127.0.0.1:{port}"
            finally:
                http.should_exit = True
                thread.join(timeout=5)
                if thread.is_alive():
                    raise CheckFailure("server", "loopback server did not stop")


def validate_exchange(api, event: dict, *, invalid_request: bool = False) -> None:
    """Validate captured real consumer traffic, not freshly reconstructed test traffic."""
    import requests
    from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse
    from openapi_core.validation.request.exceptions import RequestValidationError, InvalidRequestBody
    from openapi_core.validation.response.exceptions import ResponseValidationError
    request = requests.Request(event["method"], event["url"],
                               json=event.get("requestBody"), headers={"Content-Type": "application/json"}).prepare()
    wrapped = RequestsOpenAPIRequest(request)
    try:
        api.validate_request(wrapped)
    except RequestValidationError as exc:
        if not (invalid_request and isinstance(exc, InvalidRequestBody)):
            raise CheckFailure("request", str(exc)) from exc
    else:
        if invalid_request:
            raise CheckFailure("request", "invalid-name fixture unexpectedly satisfies the request schema")
    response = requests.Response()
    response.status_code = event["status"]
    response.headers.update(event["headers"])
    response._content = json.dumps(event["body"]).encode()
    try:
        api.validate_response(wrapped, RequestsOpenAPIResponse(response))
    except ResponseValidationError as exc:
        raise CheckFailure("response", f"{event['method']} {event['url']}: {exc}") from exc


def exercise(mode: str, bundled: Path, temporary: Path) -> dict:
    from openapi_core import OpenAPI
    import requests
    # The examples contain only trusted, local references. Never point this runner at arbitrary projects.
    api = OpenAPI.from_file_path(str(bundled))
    client = temporary / "client"
    (client / "generated").mkdir(parents=True)
    shutil.copyfile(ROOT / "consumer.ts", client / "consumer.ts")
    shutil.copyfile(ROOT / mode / "generated/api.d.ts", client / "generated/api.d.ts")
    run(["tsc", "consumer.ts", "--strict", "--target", "ES2022", "--module", "commonjs",
         "--lib", "ES2022,DOM,DOM.Iterable", "--outDir", "dist"], "types", client)
    database = temporary / "items.sqlite"
    with server(mode, database) as base:
        captured = json.loads(run(["node", str(client / "dist/consumer.js"), base], "consumer", client))
        events = captured["events"]
        if len(events) != 4:
            raise CheckFailure("behavior", "consumer did not exercise the four expected operations")
        for index, event in enumerate(events):
            validate_exchange(api, event, invalid_request=index == 2)
        if [event["status"] for event in events] != [201, 200, 400 if mode == "definition-first" else 422, 404]:
            raise CheckFailure("behavior", "unexpected success, validation or missing-item status")
        created = events[0]["body"]
        if events[1]["body"] != created or created["name"] != "sample" or created["note"] is not None:
            raise CheckFailure("behavior", "creation and retrieval do not preserve the approved values")
    # Reopen both provider and database. This tests file-backed persistence, not production crash recovery.
    with server(mode, database) as base:
        response = requests.get(base + "/items/" + created["id"], timeout=5)
        validate_exchange(api, {"method": "GET", "url": response.url, "status": response.status_code,
                               "headers": dict(response.headers), "body": response.json()})
        if response.status_code != 200 or response.json() != created:
            raise CheckFailure("behavior", "saved item cannot be read after reopening the provider")
    with sqlite3.connect(database) as db:
        count = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count != 1:
            raise CheckFailure("behavior", "invalid request changed the persisted item count")
    return {"mode": mode, "status": "passed", "real_consumer_exchanges": len(events),
            "reopened_database_verified": True, "native_model_evaluated": False}


def check(mode: str, *, generate: bool = False) -> dict:
    with tempfile.TemporaryDirectory(prefix="buildos-contract-") as directory:
        temporary = Path(directory)
        bundled = prepare(mode, temporary, generate=generate)
        return exercise(mode, bundled, temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=MODES)
    parser.add_argument("--generate", action="store_true", help="explicitly refresh only this example's generated artifacts")
    args = parser.parse_args()
    try:
        result = check(args.mode, generate=args.generate)
    except (CheckFailure, OSError, ValueError, ImportError) as exc:
        print(json.dumps({"status": "failed", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
