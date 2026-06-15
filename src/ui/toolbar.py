from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QWidget


class ReaderToolbar(QFrame):
    open_requested = pyqtSignal()
    bookmark_requested = pyqtSignal()
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()
    reset_zoom_requested = pyqtSignal()
    smart_search_requested = pyqtSignal(str)
    search_text_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ReaderToolbar")

        self._open_button = QPushButton("Open PDF")
        self._bookmark_button = QPushButton("Add Bookmark")
        self._search_input = QLineEdit()
        self._search_button = QPushButton("Search")
        self._clear_search_button = QPushButton("Clear")
        self._zoom_out_button = QPushButton("-")
        self._reset_zoom_button = QPushButton("100%")
        self._zoom_in_button = QPushButton("+")
        self._page_label = QLabel("Page - / -")
        self._title_label = QLabel("No PDF open")

        self._title_label.setObjectName("DocumentTitle")
        self._title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._search_input.setObjectName("SmartSearchInput")
        self._search_input.setPlaceholderText("Page, chapter, or text...")
        self._search_input.setMinimumWidth(240)

        self._open_button.clicked.connect(self.open_requested.emit)
        self._bookmark_button.clicked.connect(self.bookmark_requested.emit)
        self._search_button.clicked.connect(self._emit_search_requested)
        self._search_input.returnPressed.connect(self._emit_search_requested)
        self._search_input.textChanged.connect(self._handle_search_text_changed)
        self._clear_search_button.clicked.connect(self.clear_search)
        self._zoom_out_button.clicked.connect(self.zoom_out_requested.emit)
        self._reset_zoom_button.clicked.connect(self.reset_zoom_requested.emit)
        self._zoom_in_button.clicked.connect(self.zoom_in_requested.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        layout.addWidget(self._open_button)
        layout.addWidget(self._bookmark_button)
        layout.addWidget(self._search_input)
        layout.addWidget(self._search_button)
        layout.addWidget(self._clear_search_button)
        layout.addWidget(self._zoom_out_button)
        layout.addWidget(self._reset_zoom_button)
        layout.addWidget(self._zoom_in_button)
        layout.addWidget(self._page_label)
        layout.addStretch(1)
        layout.addWidget(self._title_label)

        self.update_state(
            page_label="Page - / -",
            can_add_bookmark=False,
            can_search=False,
            can_zoom=False,
            zoom_label="100%",
            document_title="No PDF open",
        )

    def update_state(
        self,
        page_label: str,
        can_add_bookmark: bool,
        can_search: bool,
        can_zoom: bool,
        zoom_label: str,
        document_title: str,
    ) -> None:
        self._page_label.setText(page_label)
        self._bookmark_button.setEnabled(can_add_bookmark)
        self._search_input.setEnabled(can_search)
        self._search_button.setEnabled(can_search)
        self._clear_search_button.setEnabled(can_search and bool(self._search_input.text().strip()))
        self._zoom_out_button.setEnabled(can_zoom)
        self._reset_zoom_button.setEnabled(can_zoom)
        self._zoom_in_button.setEnabled(can_zoom)
        self._reset_zoom_button.setToolTip(f"Reset zoom from {zoom_label} to 100%")
        self._title_label.setText(document_title)

    def _emit_search_requested(self) -> None:
        self.smart_search_requested.emit(self._search_input.text())

    def clear_search(self) -> None:
        self._search_input.clear()

    def _handle_search_text_changed(self, text: str) -> None:
        self._clear_search_button.setEnabled(self._search_input.isEnabled() and bool(text.strip()))
        self.search_text_changed.emit(text)
