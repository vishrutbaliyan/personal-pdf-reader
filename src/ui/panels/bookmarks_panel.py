from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.bookmark import Bookmark


PAGE_ROLE = Qt.ItemDataRole.UserRole
BOOKMARK_ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
PINNED_ROLE = Qt.ItemDataRole.UserRole.value + 2
LABEL_ROLE = Qt.ItemDataRole.UserRole.value + 3


class BookmarksPanel(QFrame):
    bookmark_selected = pyqtSignal(int)
    rename_requested = pyqtSignal(str, str)
    delete_requested = pyqtSignal(str)
    pin_toggled_requested = pyqtSignal(str, bool)

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
        self._list.currentItemChanged.connect(self._handle_current_item_changed)

        self._rename_button = QPushButton("Rename")
        self._delete_button = QPushButton("Delete")
        self._pin_button = QPushButton("Pin")

        self._rename_button.clicked.connect(self._emit_rename_requested)
        self._delete_button.clicked.connect(self._emit_delete_requested)
        self._pin_button.clicked.connect(self._emit_pin_toggled_requested)

        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        actions_layout.addWidget(self._rename_button)
        actions_layout.addWidget(self._delete_button)
        actions_layout.addWidget(self._pin_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._heading)
        layout.addWidget(self._list, 1)
        layout.addLayout(actions_layout)

        self.set_bookmarks([])

    def set_bookmarks(self, bookmarks: list[Bookmark]) -> None:
        self._list.clear()

        if not bookmarks:
            item = QListWidgetItem("No bookmarks yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(item)
            self._refresh_action_buttons()
            return

        for bookmark in bookmarks:
            page_number = bookmark.page_index + 1
            pin_prefix = "[Pinned] " if bookmark.pinned else ""
            item = QListWidgetItem(f"{pin_prefix}{bookmark.label} - Page {page_number}")
            item.setData(PAGE_ROLE, bookmark.page_index)
            item.setData(BOOKMARK_ID_ROLE, bookmark.bookmark_id)
            item.setData(PINNED_ROLE, bookmark.pinned)
            item.setData(LABEL_ROLE, bookmark.label)
            self._list.addItem(item)

        self._refresh_action_buttons()

    def _handle_item_clicked(self, item: QListWidgetItem) -> None:
        page_index = item.data(PAGE_ROLE)
        if isinstance(page_index, int):
            self.bookmark_selected.emit(page_index)

    def _handle_current_item_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        self._refresh_action_buttons()

    def _emit_rename_requested(self) -> None:
        item = self._list.currentItem()
        bookmark_id = self._selected_bookmark_id()
        if item is not None and bookmark_id:
            label = item.data(LABEL_ROLE)
            self.rename_requested.emit(bookmark_id, label if isinstance(label, str) else "")

    def _emit_delete_requested(self) -> None:
        bookmark_id = self._selected_bookmark_id()
        if bookmark_id:
            self.delete_requested.emit(bookmark_id)

    def _emit_pin_toggled_requested(self) -> None:
        item = self._list.currentItem()
        bookmark_id = self._selected_bookmark_id()
        if item is None or bookmark_id is None:
            return

        pinned = bool(item.data(PINNED_ROLE))
        self.pin_toggled_requested.emit(bookmark_id, not pinned)

    def _selected_bookmark_id(self) -> str | None:
        item = self._list.currentItem()
        if item is None:
            return None

        bookmark_id = item.data(BOOKMARK_ID_ROLE)
        return bookmark_id if isinstance(bookmark_id, str) else None

    def _refresh_action_buttons(self) -> None:
        item = self._list.currentItem()
        bookmark_id = self._selected_bookmark_id()
        has_selection = bookmark_id is not None

        self._rename_button.setEnabled(has_selection)
        self._delete_button.setEnabled(has_selection)
        self._pin_button.setEnabled(has_selection)

        pinned = bool(item.data(PINNED_ROLE)) if item is not None else False
        self._pin_button.setText("Unpin" if pinned else "Pin")
