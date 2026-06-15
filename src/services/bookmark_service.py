from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

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
            bookmark_id=str(uuid4()),
            document_id=document.document_id,
            page_index=page_index,
            label=self._bookmark_label(page_index, label),
            created_at=current_timestamp(),
        )
        self._bookmark_store.add_bookmark(bookmark)
        return bookmark

    def rename_bookmark(
        self,
        document: PdfDocument | None,
        bookmark_id: str,
        label: str,
    ) -> Bookmark:
        bookmark = self._find_bookmark(document, bookmark_id)
        new_label = label.strip()
        if not new_label:
            raise PdfReaderError("Bookmark label cannot be empty.")

        updated_bookmark = replace(bookmark, label=new_label)
        self._bookmark_store.update_bookmark(updated_bookmark)
        return updated_bookmark

    def delete_bookmark(self, document: PdfDocument | None, bookmark_id: str) -> None:
        self._find_bookmark(document, bookmark_id)
        active_document = self._require_document(document)
        self._bookmark_store.delete_bookmark(active_document.document_id, bookmark_id)

    def set_bookmark_pinned(
        self,
        document: PdfDocument | None,
        bookmark_id: str,
        pinned: bool,
    ) -> Bookmark:
        bookmark = self._find_bookmark(document, bookmark_id)
        updated_bookmark = replace(bookmark, pinned=pinned)
        self._bookmark_store.update_bookmark(updated_bookmark)
        return updated_bookmark

    def get_bookmarks(self, document: PdfDocument | None) -> list[Bookmark]:
        if document is None:
            return []
        return self._bookmark_store.get_bookmarks(document.document_id)

    def _find_bookmark(self, document: PdfDocument | None, bookmark_id: str) -> Bookmark:
        active_document = self._require_document(document)
        for bookmark in self._bookmark_store.get_bookmarks(active_document.document_id):
            if bookmark.bookmark_id == bookmark_id:
                return bookmark
        raise PdfReaderError("The selected bookmark could not be found.")

    def _require_document(self, document: PdfDocument | None) -> PdfDocument:
        if document is None:
            raise PdfReaderError("Open a PDF before managing bookmarks.")
        return document

    def _bookmark_label(self, page_index: int, label: str | None) -> str:
        cleaned_label = (label or "").strip()
        return cleaned_label or f"Page {page_index + 1}"
