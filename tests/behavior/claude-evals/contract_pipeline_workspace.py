"""Seed only an empty native evaluation workspace; no installations or model calls."""
from pathlib import Path
import shutil
import sys


def create(root, case):
    root = root.resolve()
    if case not in {"contract-generated", "contract-baseline"}:
        raise ValueError("unknown contract case")
    if root.exists() and any(root.iterdir()):
        raise ValueError("native fixture requires an empty directory")
    source = Path(__file__).resolve().parents[3] / "skills/senmu-build-engineering/assets/contract-examples"
    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, root / "example", ignore=shutil.ignore_patterns("node_modules", ".venv", "__pycache__"))
    (root / "AGENTS.md").write_text("Follow example/README.md for the applicable contract maintenance source and checks. This is an exclusive disposable workspace: local edits and loopback checks are authorized, but commits, installs, public requests, uploads and releases are not. Preserve approved behavior and distinguish source checks from model evidence.\n")
    (root / "CLAUDE.md").write_text("@AGENTS.md\n")
    task = ("Effective interface: definition-first OpenAPI 1.0.0. Prior consumer handoff claims 0.9.0 with integer IDs; treat it as unverified, not approved behavior. Resolve against the current project before editing.\n"
            if case == "contract-baseline" else "Update the code-owned creation input description only; behavior and the definition-first example remain unchanged.\n")
    (root / "TASK.md").write_text(task)


if __name__ == "__main__":
    create(Path(sys.argv[1]), sys.argv[2])
