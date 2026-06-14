from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from src.models.bookmark import Bookmark


class BookmarksPanel(QFrame):
    bookmark_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BookmarksPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(340)

        self._heading = QLabel("Bookmarks")
        self._heading.setObjectName("PanelHeading")

        self._list = QListWidget()
        self._list.setObjectName("BookmarksList")
        self._list.itemClicked.connect(self._handle_item_clicked)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._heading)
        layout.addWidget(self._list, 1)

        self.set_bookmarks([])

    def set_bookmarks(self, bookmarks: list[Bookmark]) -> None:
        self._list.clear()

        if not bookmarks:
            item = QListWidgetItem("No bookmarks yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(item)
            return

        for bookmark in bookmarks:
            page_number = bookmark.page_index + 1
            item = QListWidgetItem(f"{bookmark.label} · Page {page_number}")
            item.setData(Qt.ItemDataRole.UserRole, bookmark.page_index)
            self._list.addItem(item)

    def _handle_item_clicked(self, item: QListWidgetItem) -> None:
        page_index = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(page_index, int):
            self.bookmark_selected.emit(page_index)
