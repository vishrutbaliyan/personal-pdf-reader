from __future__ import annotations

from src.models.pdf_document import PdfDocument
from src.models.recent_book import RecentBook
from src.storage.recent_books_store import RecentBooksStore
from src.utils.time_utils import current_timestamp


class RecentBooksService:
    """Business logic for recently opened books."""

    MAX_RECENT_BOOKS = 10

    def __init__(
        self,
        recent_books_store: RecentBooksStore | None = None,
    ) -> None:
        self._recent_books_store = (
            recent_books_store or RecentBooksStore()
        )

    def get_recent_books(self) -> list[RecentBook]:
        books: list[RecentBook] = []

        for raw_book in self._recent_books_store.get_recent_books():
            try:
                books.append(RecentBook.from_dict(raw_book))
            except (TypeError, ValueError):
                continue

        return books

    def record_opened_book(self, document: PdfDocument) -> None:
        books = self.get_recent_books()

        books = [
            book
            for book in books
            if book.document_id != document.document_id
        ]

        books.insert(
            0,
            RecentBook(
                document_id=document.document_id,
                file_path=str(document.file_path),
                title=document.title,
                last_opened_at=current_timestamp(),
            ),
        )

        books = books[: self.MAX_RECENT_BOOKS]

        self._recent_books_store.save_recent_books(
            [book.to_dict() for book in books]
        )