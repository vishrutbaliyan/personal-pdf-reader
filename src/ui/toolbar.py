from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget


class ReaderToolbar(QFrame):
    open_requested = pyqtSignal()
    previous_requested = pyqtSignal()
    next_requested = pyqtSignal()
    bookmark_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ReaderToolbar")

        self._open_button = QPushButton("Open PDF")
        self._previous_button = QPushButton("Previous")
        self._next_button = QPushButton("Next")
        self._bookmark_button = QPushButton("Add Bookmark")
        self._page_label = QLabel("Page - / -")
        self._title_label = QLabel("No PDF open")

        self._title_label.setObjectName("DocumentTitle")
        self._title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._open_button.clicked.connect(self.open_requested.emit)
        self._previous_button.clicked.connect(self.previous_requested.emit)
        self._next_button.clicked.connect(self.next_requested.emit)
        self._bookmark_button.clicked.connect(self.bookmark_requested.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        layout.addWidget(self._open_button)
        layout.addWidget(self._previous_button)
        layout.addWidget(self._next_button)
        layout.addWidget(self._bookmark_button)
        layout.addWidget(self._page_label)
        layout.addStretch(1)
        layout.addWidget(self._title_label)

        self.update_state(
            page_label="Page - / -",
            can_go_previous=False,
            can_go_next=False,
            can_add_bookmark=False,
            document_title="No PDF open",
        )

    def update_state(
        self,
        page_label: str,
        can_go_previous: bool,
        can_go_next: bool,
        can_add_bookmark: bool,
        document_title: str,
    ) -> None:
        self._page_label.setText(page_label)
        self._previous_button.setEnabled(can_go_previous)
        self._next_button.setEnabled(can_go_next)
        self._bookmark_button.setEnabled(can_add_bookmark)
        self._title_label.setText(document_title)
