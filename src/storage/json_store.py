from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStore:
    """Small JSON persistence helper shared by concrete storage classes."""

    def __init__(self, file_path: Path, default_data: dict[str, Any] | None = None) -> None:
        self._file_path = file_path
        self._default_data = default_data or {}
        self._ensure_file_exists()

    def read(self) -> dict[str, Any]:
        try:
            with self._file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return dict(self._default_data)

        if not isinstance(data, dict):
            return dict(self._default_data)

        return data

    def write(self, data: dict[str, Any]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")

    def _ensure_file_exists(self) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self.write(dict(self._default_data))
