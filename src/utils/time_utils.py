from __future__ import annotations

from datetime import datetime, timezone


def current_timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
