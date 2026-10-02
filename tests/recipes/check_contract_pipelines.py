"""Opt-in real contract chains in disposable copies; never install tools or grade a model."""
import argparse
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "skills/senmu-build-engineering/assets/contract-examples"
MODES = ("definition-first", "declaration-first")


def fingerprint(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and not {"node_modules", ".venv", "__pycache__"} & set(p.parts)}


def run(root, mode, *, generate=False, failure=None):
    command = [sys.executable, "check.py", mode] + (["--generate"] if generate else [])
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=90)
    output = result.stdout + result.stderr
    if failure is None:
        if result.returncode:
            raise AssertionError(f"Expected pass: {command}\n{output}")
    elif result.returncode == 0 or failure not in output:
        raise AssertionError(f"Expected failure {failure!r}: {command}\n{output}")
    return {"mode": mode, "exit_code": result.returncode, "expected_failure": failure}


def cases(mode):
    result = [
        ("stale-generated-contract", f"{mode}/generated/openapi.json", '"version": "1.0.0"', '"version": "0.0.0"', False, "contract-drift"),
        ("hand-edited-client", f"{mode}/generated/api.d.ts", "export interface paths", "// hand edit\nexport interface paths", False, "client-drift"),
        ("consumer-wrong-request-type", "consumer.ts", 'name: "sample"', 'name: 42', False, "types:"),
        ("missing-persistence", "store.py", '        db.execute("INSERT INTO items VALUES (?, ?, ?)", (item["id"], name, note))', '        # Deliberate failure: no insertion.', False, "behavior:"),
    ]
    if mode == "definition-first":
        result += [
            ("referenced-file-drift", f"{mode}/schemas/item.yaml", "required: [id, name, note]", "description: Updated description\nrequired: [id, name, note]", False, "contract-drift"),
            ("missing-required-response-field", f"{mode}/schemas/item.yaml", "required: [id, name, note]", "required: [id, name, note, createdAt]", True, "response:"),
            ("wrong-referenced-response-type", f"{mode}/schemas/item.yaml", "  name:\n    type: string", "  name:\n    type: integer", True, "response:"),
            ("broken-reference", f"{mode}/openapi.yaml", "./schemas/item.yaml", "./schemas/absent.yaml", False, "bundle:"),
            ("inactive-operation-id", f"{mode}/openapi.yaml", "      operationId: createItem\n", "", False, "definition:"),
        ]
    else:
        result += [
            ("declaration-drift", f"{mode}/app.py", 'name: str = Field(min_length=1)', 'name: str = Field(min_length=1, description="Name")', False, "contract-drift"),
            ("required-output-bypassed", f"{mode}/app.py", '        return save(database, request.name, request.note)', '        from fastapi.responses import JSONResponse\n        item = save(database, request.name, request.note)\n        del item["note"]\n        return JSONResponse(item, status_code=201)', False, "response:"),
        ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES)
    parser.add_argument("--case", action="append", help="focus a known failure case; normal and restored checks remain")
    args = parser.parse_args()
    selected = [args.mode] if args.mode else list(MODES)
    known = {c[0] for mode in selected for c in cases(mode)}
    if args.case and not set(args.case) <= known:
        parser.error("unknown case")
    for tool in ("redocly", "openapi-typescript", "tsc", "node"):
        if shutil.which(tool) is None:
            raise SystemExit(f"Required contract tool unavailable: {tool}; no checks claimed")
    tools = {package: version(package) for package in ("openapi-core", "fastapi", "pydantic", "requests")}
    before, receipts = fingerprint(EXAMPLES), []
    for mode in selected:
        with tempfile.TemporaryDirectory(prefix="buildos-contract-proof-") as directory:
            root = Path(directory) / "example"
            shutil.copytree(EXAMPLES, root, ignore=shutil.ignore_patterns("node_modules", ".venv", "__pycache__"))
            initial = fingerprint(root)
            receipts.append({"case": "normal", **run(root, mode)})
            if fingerprint(root) != initial:
                raise AssertionError("read-only check modified the example")
            for name, relative, old, new, generate, diagnostic in cases(mode):
                if args.case and name not in args.case:
                    continue
                originals = {p: (root / p).read_bytes() for p in
                             (relative, f"{mode}/generated/openapi.json", f"{mode}/generated/api.d.ts")}
                target = root / relative
                text = target.read_text()
                if old not in text:
                    raise AssertionError(f"mutation did not match: {relative}")
                target.write_text(text.replace(old, new))
                receipts.append({"case": name, **run(root, mode, generate=generate, failure=diagnostic)})
                for relative_path, body in originals.items():
                    (root / relative_path).write_bytes(body)
                receipts.append({"case": name + "-restored", **run(root, mode)})
            receipts.append({"case": "regeneration", **run(root, mode, generate=True)})
            if fingerprint(root) != initial:
                raise AssertionError("regeneration was not reproducible")
    if fingerprint(EXAMPLES) != before:
        raise AssertionError("the proof modified the source examples")
    print(json.dumps({"status": "passed", "tools": tools, "checks": receipts,
                      "claim": "schema/generator/real-consumer/SQLite fixture evidence; no native model evaluation"}, indent=2))


if __name__ == "__main__":
    main()
