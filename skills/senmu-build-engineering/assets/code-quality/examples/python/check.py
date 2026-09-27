"""One example quality command; run from any working directory."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
COMMANDS = (
    (sys.executable, "-m", "ruff", "check", "."),
    (sys.executable, "-m", "ruff", "format", "--check", "."),
    (sys.executable, "-m", "mypy", "sample_app"),
    ("lint-imports", "--config", ".importlinter", "--no-cache"),
    (sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"),
)

if __name__ == "__main__":
    for command in COMMANDS:
        subprocess.run(command, cwd=ROOT, check=True)
