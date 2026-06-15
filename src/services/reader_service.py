from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QImage

from src.config.app_config import DEFAULT_ZOOM_FACTOR, MAX_ZOOM_FACTOR, MIN_ZOOM_FACTOR, ZOOM_STEP
from src.models.pdf_document import PdfDocument
from src.services.exceptions import PdfReaderError
from src.services.pdf_service import PdfService
from src.storage.progress_store import ProgressStore


class ReaderService:
    """Coordinates the active document, page state, and reading navigation."""

    def __init__(
        self,
        pdf_service: PdfService | None = None,
        progress_store: ProgressStore | None = None,
    ) -> None:
        self._pdf_service = pdf_service or PdfService()
        self._progress_store = progress_store or ProgressStore()
        self._current_document: PdfDocument | None = None
        self._current_page_index = 0
        self._zoom_factor = DEFAULT_ZOOM_FACTOR

    @property
    def current_document(self) -> PdfDocument | None:
        return self._current_document

    @property
    def current_page_index(self) -> int:
        return self._current_page_index

    @property
    def total_pages(self) -> int:
        return self._current_document.page_count if self._current_document else 0

    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor

    def open_document(self, file_path: Path) -> QImage:
        self._current_document = self._pdf_service.open_pdf(file_path)
        self._current_page_index = self._restored_page_index(self._current_document)
        image = self._render_current_page()
        self._save_current_progress()
        return image

    def next_page(self) -> QImage:
        self._require_document()
        if not self.can_go_next():
            raise PdfReaderError("You are already on the last page.")

        return self._go_to_page(self._current_page_index + 1)

    def previous_page(self) -> QImage:
        self._require_document()
        if not self.can_go_previous():
            raise PdfReaderError("You are already on the first page.")

        return self._go_to_page(self._current_page_index - 1)

    def go_to_page(self, page_index: int) -> QImage:
        document = self._require_document()
        if page_index < 0 or page_index >= document.page_count:
            raise PdfReaderError("Page number is outside the document range.")

        return self._go_to_page(page_index)

    def zoom_in(self) -> QImage:
        return self._set_zoom(self._zoom_factor + ZOOM_STEP)

    def zoom_out(self) -> QImage:
        return self._set_zoom(self._zoom_factor - ZOOM_STEP)

    def reset_zoom(self) -> QImage:
        return self._set_zoom(DEFAULT_ZOOM_FACTOR)

    def can_go_next(self) -> bool:
        return self._current_document is not None and self._current_page_index < self.total_pages - 1

    def can_go_previous(self) -> bool:
        return self._current_document is not None and self._current_page_index > 0

    def page_label(self) -> str:
        if self._current_document is None:
            return "Page - / -"
        return f"Page {self._current_page_index + 1} / {self.total_pages}"

    def zoom_label(self) -> str:
        return f"{round(self._zoom_factor * 100)}%"

    def close(self) -> None:
        self._pdf_service.close()
        self._current_document = None
        self._current_page_index = 0

    def _render_current_page(self) -> QImage:
        self._require_document()
        return self._pdf_service.render_page(self._current_page_index, self._zoom_factor)

    def _go_to_page(self, page_index: int) -> QImage:
        previous_page_index = self._current_page_index
        self._current_page_index = page_index

        try:
            image = self._render_current_page()
        except PdfReaderError:
            self._current_page_index = previous_page_index
            raise

        self._save_current_progress()
        return image

    def _set_zoom(self, zoom_factor: float) -> QImage:
        self._require_document()
        self._zoom_factor = max(MIN_ZOOM_FACTOR, min(zoom_factor, MAX_ZOOM_FACTOR))
        return self._render_current_page()

    def _restored_page_index(self, document: PdfDocument) -> int:
        progress = self._progress_store.get_progress(document.document_id)
        if progress is None:
            return 0

        # Clamp stored progress in case the PDF was replaced with fewer pages.
        return max(0, min(progress.page_index, document.page_count - 1))

    def _save_current_progress(self) -> None:
        document = self._require_document()
        self._progress_store.save_progress(document, self._current_page_index)

    def _require_document(self) -> PdfDocument:
        if self._current_document is None:
            raise PdfReaderError("Open a PDF before navigating pages.")
        return self._current_document
