from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QCloseEvent, QImage
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from src.config.app_config import (
    APP_NAME,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    SUPPORTED_FILE_FILTER,
)
from src.config.paths import LIGHT_STYLE_PATH
from src.services.exceptions import PdfReaderError
from src.services.reader_service import ReaderService
from src.ui.pdf_viewer import PdfViewer
from src.ui.toolbar import ReaderToolbar


class MainWindow(QMainWindow):
    """Main shell for the reader UI. Reading behavior is delegated to ReaderService."""

    def __init__(self) -> None:
        super().__init__()
        self._reader_service = ReaderService()

        self._toolbar = ReaderToolbar()
        self._viewer = PdfViewer()

        self._setup_window()
        self._connect_signals()
        self._load_stylesheet()
        self._refresh_toolbar()

    def _setup_window(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._viewer, 1)

        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        self._toolbar.open_requested.connect(self._open_pdf)
        self._toolbar.previous_requested.connect(self._show_previous_page)
        self._toolbar.next_requested.connect(self._show_next_page)

    def _load_stylesheet(self) -> None:
        if LIGHT_STYLE_PATH.exists():
            self.setStyleSheet(LIGHT_STYLE_PATH.read_text(encoding="utf-8"))

    def _open_pdf(self) -> None:
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            str(Path.home()),
            SUPPORTED_FILE_FILTER,
        )

        if not selected_file:
            return

        try:
            image = self._reader_service.open_document(Path(selected_file))
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _show_previous_page(self) -> None:
        try:
            image = self._reader_service.previous_page()
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _show_next_page(self) -> None:
        try:
            image = self._reader_service.next_page()
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _display_page(self, image: QImage) -> None:
        self._viewer.set_page_image(image)
        self._refresh_toolbar()

    def _refresh_toolbar(self) -> None:
        document = self._reader_service.current_document
        document_title = document.title if document else "No PDF open"
        self._toolbar.update_state(
            page_label=self._reader_service.page_label(),
            can_go_previous=self._reader_service.can_go_previous(),
            can_go_next=self._reader_service.can_go_next(),
            document_title=document_title,
        )

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "PDF Reader", message)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._reader_service.close()
        super().closeEvent(event)
