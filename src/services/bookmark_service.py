from __future__ import annotations

from src.models.bookmark import Bookmark
from src.models.pdf_document import PdfDocument
from src.services.exceptions import PdfReaderError
from src.storage.bookmark_store import BookmarkStore
from src.utils.time_utils import current_timestamp


class BookmarkService:
    """Business logic for creating and retrieving PDF bookmarks."""

    def __init__(self, bookmark_store: BookmarkStore | None = None) -> None:
        self._bookmark_store = bookmark_store or BookmarkStore()

    def add_bookmark(
        self,
        document: PdfDocument | None,
        page_index: int,
        label: str | None = None,
    ) -> Bookmark:
        if document is None:
            raise PdfReaderError("Open a PDF before adding a bookmark.")

        if page_index < 0 or page_index >= document.page_count:
            raise PdfReaderError("Cannot bookmark a page outside the document range.")

        bookmark = Bookmark(
            document_id=document.document_id,
            page_index=page_index,
            label=self._bookmark_label(page_index, label),
            created_at=current_timestamp(),
        )
        self._bookmark_store.add_bookmark(bookmark)
        return bookmark

    def get_bookmarks(self, document: PdfDocument | None) -> list[Bookmark]:
        if document is None:
            return []
        return self._bookmark_store.get_bookmarks(document.document_id)

    def _bookmark_label(self, page_index: int, label: str | None) -> str:
        cleaned_label = (label or "").strip()
        return cleaned_label or f"Page {page_index + 1}"
