"""Opt-in real tool checks in disposable copies; never install or edit a project."""
from pathlib import Path
from importlib.metadata import version
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "skills/senmu-build-engineering/assets/code-quality/examples"


def run(command, root, *, failure=None):
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
    output = result.stdout + result.stderr
    # Tools can emit ANSI styling even when their output is captured. Preserve
    # raw failure evidence, but match diagnostics against visible text only.
    visible = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", output)
    if failure is None:
        if result.returncode != 0:
            raise AssertionError(f"Expected pass: {command}\n{output}")
    elif result.returncode == 0 or failure not in visible:
        raise AssertionError(f"Expected failure containing {failure!r}: {command}\n{output}")
    return {"command": command, "expected_failure": failure, "exit_code": result.returncode}


def fingerprint(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    for tool in ("ruff", "mypy", "lint-imports", "node", "npm", "tsc", "depcruise"):
        if shutil.which(tool) is None:
            raise SystemExit(f"Required example tool unavailable: {tool}; no checks claimed")
    before = fingerprint(EXAMPLES)
    receipts = []
    for language in ("python", "typescript"):
        with tempfile.TemporaryDirectory(prefix="buildos-rule-proof-") as directory:
            root = Path(directory) / language
            shutil.copytree(EXAMPLES / language, root)
            command = [sys.executable, "check.py"] if language == "python" else ["npm", "run", "check"]
            receipts.append({"language": language, "case": "normal", **run(command, root)})
            if language == "python":
                path = root / "sample_app/domain.py"
                original = path.read_text()
                cases = [
                    ("mutable-default", path, original + '\n\ndef accumulate(items: list[int] = []) -> int:\n    return len(items)\n', "B006"),
                    ("wrong-return-type", path, original.replace("return result", 'return "wrong"'), "Incompatible return"),
                    ("forbidden-import", path, 'from sample_app import adapters\n\n\n' + original + '\n\ndef adapter_probe() -> str:\n    return adapters.identity()\n', "Domain stays independent of adapters BROKEN"),
                    ("wrong-business-result", path, original.replace("subtotal - discount", "subtotal + discount"), "FAILED"),
                ]
            else:
                client = root / "src/client.ts"
                internal = root / "src/pricing/internal.ts"
                cases = [
                    ("private-import", client, client.read_text().replace("pricing/index.js", "pricing/internal.js"), "pricing-public-entry"),
                    ("wrong-type", client, client.read_text().replace("total(100, 20)", '"wrong"'), "TS2322"),
                    ("cycle", internal, 'import { exampleTotal } from "../client.js";\n' + internal.read_text() + '\nexport function cycleProbe(): number { return exampleTotal; }\n', "no-cycles"),
                    ("wrong-business-result", internal, internal.read_text().replace("subtotal - discount", "subtotal + discount"), "ERR_ASSERTION"),
                ]
            for name, path, mutated, diagnostic in cases:
                saved = path.read_bytes()
                try:
                    path.write_text(mutated)
                    receipts.append({"language": language, "case": name, **run(command, root, failure=diagnostic)})
                finally:
                    path.write_bytes(saved)
                receipts.append({"language": language, "case": name + "-restored", **run(command, root)})
    if before != fingerprint(EXAMPLES):
        raise AssertionError("An example source was modified")
    # Import Linter has no --version flag. The documented setup installs it
    # in this interpreter's environment; retain executable locations as well.
    versions = {"import-linter (Python environment)": version("import-linter")}
    for tool in ("ruff", "mypy", "node", "npm", "tsc", "depcruise"):
        result = subprocess.run([tool, "--version"], capture_output=True, text=True, check=True, timeout=30)
        versions[tool] = (result.stdout + result.stderr).strip()
    print(json.dumps({"status": "passed", "tools": versions, "python": sys.executable,
                      "import_linter_executable": shutil.which("lint-imports"), "checks": receipts,
                      "claim": "real tool/fixture evidence only; no native model evaluation"}, indent=2))


if __name__ == "__main__":
    main()
