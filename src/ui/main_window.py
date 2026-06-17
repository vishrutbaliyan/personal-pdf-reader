from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QCloseEvent, QImage
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from src.config.app_config import (
    APP_NAME,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    SUPPORTED_FILE_FILTER,
)
from src.config.paths import LIGHT_STYLE_PATH
from src.services.bookmark_service import BookmarkService
from src.services.exceptions import PdfReaderError
from src.services.pdf_service import PdfService
from src.services.reader_service import ReaderService
from src.services.search_service import SearchService
from src.ui.navigation_controls import NavigationControls
from src.ui.panels.bookmarks_panel import BookmarksPanel
from src.ui.panels.search_results_panel import SearchResultsPanel
from src.ui.pdf_viewer import PdfViewer
from src.ui.toolbar import ReaderToolbar
from src.services.recent_books_service import RecentBooksService
from src.ui.panels.recent_books_panel import RecentBooksPanel


class MainWindow(QMainWindow):
    """Main shell for the reader UI. Reading behavior is delegated to ReaderService."""

    def __init__(self) -> None:
        super().__init__()
        self._pdf_service = PdfService()
        self._reader_service = ReaderService(self._pdf_service)
        self._bookmark_service = BookmarkService()
        self._search_service = SearchService(self._pdf_service)
        self._recent_books_service=RecentBooksService()

        self._toolbar = ReaderToolbar()
        self._viewer = PdfViewer()
        self._navigation_controls = NavigationControls()
        self._bookmarks_panel = BookmarksPanel()
        self._search_results_panel = SearchResultsPanel()
        self._recent_books_panel=RecentBooksPanel()


        self._setup_window()
        self._connect_signals()
        self._load_stylesheet()
        self._refresh_toolbar()
        self._refresh_navigation_controls()
        self._refresh_recent_books()

    def _setup_window(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._toolbar)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._viewer, 1)
        content_layout.addWidget(self._navigation_controls)
        content_layout.addWidget(self._build_right_sidebar())

        layout.addWidget(content_widget, 1)

        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        self._toolbar.open_requested.connect(self._open_pdf)
        self._toolbar.bookmark_requested.connect(self._add_bookmark)
        self._toolbar.zoom_in_requested.connect(self._zoom_in)
        self._toolbar.zoom_out_requested.connect(self._zoom_out)
        self._toolbar.reset_zoom_requested.connect(self._reset_zoom)
        self._toolbar.smart_search_requested.connect(self._run_smart_search)
        self._toolbar.search_text_changed.connect(self._handle_search_text_changed)
        self._navigation_controls.previous_requested.connect(self._show_previous_page)
        self._navigation_controls.next_requested.connect(self._show_next_page)
        self._bookmarks_panel.bookmark_selected.connect(self._jump_to_bookmark)
        self._bookmarks_panel.rename_requested.connect(self._rename_bookmark)
        self._bookmarks_panel.delete_requested.connect(self._delete_bookmark)
        self._bookmarks_panel.pin_toggled_requested.connect(self._toggle_bookmark_pin)
        self._search_results_panel.page_selected.connect(self._jump_to_search_result)
        self._recent_books_panel.book_selected.connect(self._open_recent_book)

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
            document=self._reader_service.current_document
            if document is not None:
                self._recent_books_service.record_opened_book(document)
            self._search_service.set_document(self._reader_service.current_document)
            self._display_page(image)
            self._refresh_bookmarks()
            self._refresh_recent_books()
            self._toolbar.clear_search()
            self._search_results_panel.clear_results()
        except PdfReaderError as exc:
            self._show_error(str(exc))


    def _open_recent_book(self, file_path: str) -> None:
        print("OPENING:", file_path)

        try:
            image = self._reader_service.open_document(Path(file_path))

            document = self._reader_service.current_document
            if document is not None:
                self._recent_books_service.record_opened_book(document)

            self._search_service.set_document(document)
            self._display_page(image)
            self._refresh_bookmarks()
            self._refresh_recent_books()

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

    def _zoom_in(self) -> None:
        try:
            image = self._reader_service.zoom_in()
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _zoom_out(self) -> None:
        try:
            image = self._reader_service.zoom_out()
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _reset_zoom(self) -> None:
        try:
            image = self._reader_service.reset_zoom()
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _add_bookmark(self) -> None:
        try:
            self._bookmark_service.add_bookmark(
                self._reader_service.current_document,
                self._reader_service.current_page_index,
            )
            self._refresh_bookmarks()
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _jump_to_bookmark(self, page_index: int) -> None:
        try:
            image = self._reader_service.go_to_page(page_index)
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _rename_bookmark(self, bookmark_id: str, current_label: str) -> None:
        new_label, accepted = QInputDialog.getText(
            self,
            "Rename Bookmark",
            "Bookmark label:",
            text=current_label,
        )
        if not accepted:
            return

        try:
            self._bookmark_service.rename_bookmark(
                self._reader_service.current_document,
                bookmark_id,
                new_label,
            )
            self._refresh_bookmarks()
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _delete_bookmark(self, bookmark_id: str) -> None:
        response = QMessageBox.question(
            self,
            "Delete Bookmark",
            "Delete the selected bookmark?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if response != QMessageBox.StandardButton.Yes:
            return

        try:
            self._bookmark_service.delete_bookmark(self._reader_service.current_document, bookmark_id)
            self._refresh_bookmarks()
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _toggle_bookmark_pin(self, bookmark_id: str, pinned: bool) -> None:
        try:
            self._bookmark_service.set_bookmark_pinned(
                self._reader_service.current_document,
                bookmark_id,
                pinned,
            )
            self._refresh_bookmarks()
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _run_smart_search(self, query: str) -> None:
        try:
            results = self._search_service.search(query)
            self._search_results_panel.set_results(results)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _handle_search_text_changed(self, text: str) -> None:
        if not text.strip():
            self._search_results_panel.clear_results()

    def _jump_to_search_result(self, page_index: int) -> None:
        try:
            image = self._reader_service.go_to_page(page_index)
            self._display_page(image)
        except PdfReaderError as exc:
            self._show_error(str(exc))

    def _display_page(self, image: QImage) -> None:
        self._viewer.set_page_image(image)
        self._refresh_toolbar()
        self._refresh_navigation_controls()

    def _refresh_toolbar(self) -> None:
        document = self._reader_service.current_document
        document_title = document.title if document else "No PDF open"
        self._toolbar.update_state(
            page_label=self._reader_service.page_label(),
            can_add_bookmark=document is not None,
            can_search=document is not None,
            can_zoom=document is not None,
            zoom_label=self._reader_service.zoom_label(),
            document_title=document_title,
        )

    def _refresh_navigation_controls(self) -> None:
        self._navigation_controls.update_state(
            can_go_previous=self._reader_service.can_go_previous(),
            can_go_next=self._reader_service.can_go_next(),
        )

    def _refresh_bookmarks(self) -> None:
        bookmarks = self._bookmark_service.get_bookmarks(self._reader_service.current_document)
        self._bookmarks_panel.set_bookmarks(bookmarks)

    #def _refresh_recent_books(self) -> None:
     #       books=self._recent_books_service.get_recent_books()
      #      self._recent_books_panel.set_recent_books(books)
    def _refresh_recent_books(self) -> None:
        books = self._recent_books_service.get_recent_books()
        print("BOOKS FOUND:", len(books))
        print(books)
        self._recent_books_panel.set_recent_books(books)


    def _build_right_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("RightSidebar")
        sidebar.setMinimumWidth(300)
        sidebar.setMaximumWidth(380)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._recent_books_panel,1)
        layout.addWidget(self._bookmarks_panel, 1)
        layout.addWidget(self._search_results_panel, 1)
       

        return sidebar

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "PDF Reader", message)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._reader_service.close()
        super().closeEvent(event)

        
