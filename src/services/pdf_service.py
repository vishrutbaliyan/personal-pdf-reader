from __future__ import annotations

from pathlib import Path

import fitz
from PyQt6.QtGui import QImage

from src.config.app_config import PDF_RENDER_ZOOM
from src.models.pdf_document import PdfDocument
from src.services.exceptions import PdfReaderError
from src.utils.document_id import build_document_id
from src.utils.file_utils import display_file_name, is_pdf_file


class PdfService:
    """Low-level PDF loading and rendering service backed by PyMuPDF."""

    def __init__(self) -> None:
        self._document: fitz.Document | None = None

    def open_pdf(self, file_path: Path) -> PdfDocument:
        resolved_path = file_path.expanduser().resolve()

        if not is_pdf_file(resolved_path):
            raise PdfReaderError("Please choose a valid PDF file.")

        self.close()

        try:
            self._document = fitz.open(resolved_path)
        except Exception as exc:
            raise PdfReaderError(f"Could not open PDF: {exc}") from exc

        page_count = self._document.page_count
        if page_count <= 0:
            self.close()
            raise PdfReaderError("This PDF does not contain any pages.")

        metadata_title = (self._document.metadata or {}).get("title") or ""
        title = metadata_title.strip() or display_file_name(resolved_path)

        return PdfDocument(
            document_id=build_document_id(resolved_path),
            file_path=resolved_path,
            title=title,
            page_count=page_count,
        )

    def render_page(self, page_index: int) -> QImage:
        document = self._require_document()
        self._validate_page_index(page_index)

        try:
            page = document.load_page(page_index)
            matrix = fitz.Matrix(PDF_RENDER_ZOOM, PDF_RENDER_ZOOM)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        except Exception as exc:
            raise PdfReaderError(f"Could not render page: {exc}") from exc

        image = QImage(
            pixmap.samples,
            pixmap.width,
            pixmap.height,
            pixmap.stride,
            QImage.Format.Format_RGB888,
        ).copy()

        if image.isNull():
            raise PdfReaderError("The selected page could not be displayed.")

        return image

    def close(self) -> None:
        if self._document is not None:
            self._document.close()
            self._document = None

    def _require_document(self) -> fitz.Document:
        if self._document is None:
            raise PdfReaderError("No PDF is currently open.")
        return self._document

    def _validate_page_index(self, page_index: int) -> None:
        document = self._require_document()
        if page_index < 0 or page_index >= document.page_count:
            raise PdfReaderError("Page number is outside the document range.")
