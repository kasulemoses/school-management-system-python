"""Run backend commands with the project's own Python interpreter."""

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "apps" / "api"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["dev", "test", "check", "format"])
    arguments = parser.parse_args()

    python = API / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        raise SystemExit("Run setup first: python3.13 scripts/bootstrap.py")

    commands = {
        "dev": [["uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]],
        "test": [["pytest"]],
        "check": [
            ["ruff", "check", "--config", "pyproject.toml", ".", "../../scripts"],
            ["ruff", "format", "--config", "pyproject.toml", "--check", ".", "../../scripts"],
            ["pytest"],
        ],
        "format": [
            [
                "ruff",
                "check",
                "--config",
                "pyproject.toml",
                "--fix",
                "--exit-zero",
                ".",
                "../../scripts",
            ],
            ["ruff", "format", "--config", "pyproject.toml", ".", "../../scripts"],
            ["ruff", "check", "--config", "pyproject.toml", ".", "../../scripts"],
        ],
    }
    for command in commands[arguments.command]:
        try:
            result = subprocess.run([str(python), "-m", *command], cwd=API, check=False)
        except KeyboardInterrupt:
            raise SystemExit(130) from None
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
