from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.recent_book import RecentBook


FILE_PATH_ROLE = Qt.ItemDataRole.UserRole


class RecentBooksPanel(QFrame):
    book_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("RecentBooksPanel")

        self._heading = QLabel("Recent Books")
        self._heading.setObjectName("PanelHeading")

        self._list = QListWidget()
        self._list.itemClicked.connect(self._handle_item_clicked)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(self._heading)
        layout.addWidget(self._list)

        self.set_recent_books([])

    def set_recent_books(self, books: list[RecentBook]) -> None:
        self._list.clear()

        if not books:
            item = QListWidgetItem("No recent books")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(item)
            return

        for book in books:
            item = QListWidgetItem(book.title)
            item.setData(FILE_PATH_ROLE, book.file_path)
            item.setToolTip(book.file_path)
            self._list.addItem(item)

    def _handle_item_clicked(self, item: QListWidgetItem) -> None:
        file_path = item.data(FILE_PATH_ROLE)

        if isinstance(file_path, str):
            self.book_selected.emit(file_path)