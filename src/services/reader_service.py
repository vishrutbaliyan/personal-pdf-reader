from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QImage

from src.models.pdf_document import PdfDocument
from src.services.exceptions import PdfReaderError
from src.services.pdf_service import PdfService


class ReaderService:
    """Coordinates the active document, page state, and reading navigation."""

    def __init__(self, pdf_service: PdfService | None = None) -> None:
        self._pdf_service = pdf_service or PdfService()
        self._current_document: PdfDocument | None = None
        self._current_page_index = 0

    @property
    def current_document(self) -> PdfDocument | None:
        return self._current_document

    @property
    def current_page_index(self) -> int:
        return self._current_page_index

    @property
    def total_pages(self) -> int:
        return self._current_document.page_count if self._current_document else 0

    def open_document(self, file_path: Path) -> QImage:
        self._current_document = self._pdf_service.open_pdf(file_path)
        self._current_page_index = 0
        return self._render_current_page()

    def next_page(self) -> QImage:
        self._require_document()
        if not self.can_go_next():
            raise PdfReaderError("You are already on the last page.")

        self._current_page_index += 1
        return self._render_current_page()

    def previous_page(self) -> QImage:
        self._require_document()
        if not self.can_go_previous():
            raise PdfReaderError("You are already on the first page.")

        self._current_page_index -= 1
        return self._render_current_page()

    def can_go_next(self) -> bool:
        return self._current_document is not None and self._current_page_index < self.total_pages - 1

    def can_go_previous(self) -> bool:
        return self._current_document is not None and self._current_page_index > 0

    def page_label(self) -> str:
        if self._current_document is None:
            return "Page - / -"
        return f"Page {self._current_page_index + 1} / {self.total_pages}"

    def close(self) -> None:
        self._pdf_service.close()
        self._current_document = None
        self._current_page_index = 0

    def _render_current_page(self) -> QImage:
        self._require_document()
        return self._pdf_service.render_page(self._current_page_index)

    def _require_document(self) -> PdfDocument:
        if self._current_document is None:
            raise PdfReaderError("Open a PDF before navigating pages.")
        return self._current_document
