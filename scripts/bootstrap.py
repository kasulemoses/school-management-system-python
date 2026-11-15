"""Install project-local tooling and synchronize the locked Python environment."""

import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UV_VERSION = "0.13.8"


def main() -> None:
    if sys.version_info[:2] != (3, 13):
        raise SystemExit("This checkpoint uses Python 3.13. Run: python3.13 scripts/bootstrap.py")

    tool_environment = ROOT / ".tools" / "uv"
    binary_directory = tool_environment / ("Scripts" if os.name == "nt" else "bin")
    tool_python = binary_directory / ("python.exe" if os.name == "nt" else "python")
    uv = binary_directory / ("uv.exe" if os.name == "nt" else "uv")
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = str(ROOT / ".cache" / "uv")
    environment["UV_PYTHON_DOWNLOADS"] = "never"
    environment["PIP_CACHE_DIR"] = str(ROOT / ".cache" / "pip")

    if not tool_python.exists():
        print("Creating the isolated dependency-tool environment...", flush=True)
        venv.create(tool_environment, with_pip=True)

    if not uv.exists() or subprocess.check_output(
        [str(uv), "--version"], text=True, env=environment
    ).split()[:2] != ["uv", UV_VERSION]:
        print("Installing the pinned dependency tool locally...", flush=True)
        subprocess.run(
            [str(tool_python), "-m", "pip", "install", f"uv=={UV_VERSION}"],
            check=True,
            env=environment,
        )

    print("Installing the backend's locked dependencies...", flush=True)
    subprocess.run(
        [
            str(uv),
            "sync",
            "--frozen",
            "--project",
            str(ROOT / "apps" / "api"),
            "--python",
            sys.executable,
        ],
        check=True,
        env=environment,
    )
    print("Ready. Start the API: python3.13 scripts/api.py dev", flush=True)


if __name__ == "__main__":
    main()
