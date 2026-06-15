from __future__ import annotations

from src.config.paths import BOOKMARKS_FILE_PATH
from src.models.bookmark import Bookmark
from src.storage.json_store import JsonStore


class BookmarkStore:
    """Persists bookmark lists keyed by document_id."""

    def __init__(self, json_store: JsonStore | None = None) -> None:
        self._json_store = json_store or JsonStore(BOOKMARKS_FILE_PATH)

    def get_bookmarks(self, document_id: str) -> list[Bookmark]:
        data = self._json_store.read()
        raw_bookmarks = data.get(document_id, [])

        if not isinstance(raw_bookmarks, list):
            return []

        bookmarks: list[Bookmark] = []
        for raw_bookmark in raw_bookmarks:
            if not isinstance(raw_bookmark, dict):
                continue

            try:
                bookmark = Bookmark.from_dict(raw_bookmark)
            except (TypeError, ValueError):
                continue

            if bookmark.document_id == document_id:
                bookmarks.append(bookmark)

        return self._sorted_bookmarks(bookmarks)

    def add_bookmark(self, bookmark: Bookmark) -> None:
        data = self._json_store.read()
        bookmarks = self.get_bookmarks(bookmark.document_id)
        bookmarks.append(bookmark)
        self._save_bookmarks(data, bookmark.document_id, bookmarks)

    def update_bookmark(self, bookmark: Bookmark) -> None:
        data = self._json_store.read()
        bookmarks = self.get_bookmarks(bookmark.document_id)
        updated_bookmarks = [
            bookmark if item.bookmark_id == bookmark.bookmark_id else item
            for item in bookmarks
        ]
        self._save_bookmarks(data, bookmark.document_id, updated_bookmarks)

    def delete_bookmark(self, document_id: str, bookmark_id: str) -> None:
        data = self._json_store.read()
        bookmarks = [
            bookmark
            for bookmark in self.get_bookmarks(document_id)
            if bookmark.bookmark_id != bookmark_id
        ]
        self._save_bookmarks(data, document_id, bookmarks)

    def _save_bookmarks(
        self,
        data: dict[str, object],
        document_id: str,
        bookmarks: list[Bookmark],
    ) -> None:
        data[document_id] = [item.to_dict() for item in self._sorted_bookmarks(bookmarks)]
        self._json_store.write(data)

    def _sorted_bookmarks(self, bookmarks: list[Bookmark]) -> list[Bookmark]:
        return sorted(bookmarks, key=lambda item: (not item.pinned, item.page_index, item.created_at))
