from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def _parse_env_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "=" not in line:
        return None
    k, v = line.split("=", 1)
    k = k.strip()
    v = v.strip()
    # remove optional surrounding quotes
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return k, v


def load_env(dotenv_path: str | Path | None = None) -> None:
    """Lightweight .env loader (no extra dependency).

    - Does not override variables already set in the environment.
    - Supports simple KEY=VALUE and comments beginning with '#'.
    """
    path = Path(dotenv_path) if dotenv_path else Path.cwd() / ".env"
    if not path.exists():
        return
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_env_line(line)
            if not parsed:
                continue
            k, v = parsed
            if k not in os.environ:
                os.environ[k] = v
    except Exception:
        # Fail closed: env loading is optional; ignore parse errors.
        pass
