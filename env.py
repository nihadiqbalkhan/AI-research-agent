"""Tiny, dependency-free .env loader.

Reads a .env file (if present) in the project root and sets any variables
it defines into os.environ, without overriding variables you've already
exported in your shell. Avoids adding python-dotenv as a hard dependency
just for this.
"""
import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = None) -> None:
    env_path = path or (_PROJECT_ROOT / ".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:  # don't override real shell exports
            os.environ[key] = value
