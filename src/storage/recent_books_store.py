from __future__ import annotations

from src.config.paths import RECENT_BOOKS_FILE_PATH
from src.storage.json_store import JsonStore


class RecentBooksStore:
    """Persists recently opened books."""

    def __init__(self, json_store: JsonStore | None = None) -> None:
        self._json_store = json_store or JsonStore(
            RECENT_BOOKS_FILE_PATH,
            {"recent_books": []},
        )

    def get_recent_books(self) -> list[dict]:
        data = self._json_store.read()
        raw_books = data.get("recent_books", [])

        if not isinstance(raw_books, list):
            return []

        return raw_books

    def save_recent_books(self, recent_books: list[dict]) -> None:
        self._json_store.write(
            {
                "recent_books": recent_books,
            }
        )