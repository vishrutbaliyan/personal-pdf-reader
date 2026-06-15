from __future__ import annotations

from typing import TypeAlias

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from src.models.chapter_result import ChapterResult
from src.models.search_result import SearchResult


SearchPanelItem: TypeAlias = SearchResult | ChapterResult


class SearchResultsPanel(QFrame):
    page_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SearchResultsPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(340)

        self._heading = QLabel("Search Results")
        self._heading.setObjectName("PanelHeading")

        self._tree = QTreeWidget()
        self._tree.setObjectName("SearchResultsTree")
        self._tree.setHeaderLabels(["Result", "Details"])
        self._tree.itemClicked.connect(self._handle_item_clicked)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._heading)
        layout.addWidget(self._tree, 1)

        self.set_results([])

    def set_results(self, results: list[SearchPanelItem]) -> None:
        self._tree.clear()

        if not results:
            self._add_empty_state()
            return

        page_jump_results = [
            result for result in results if isinstance(result, SearchResult) and result.result_type == "page_jump"
        ]
        chapter_results = [result for result in results if isinstance(result, ChapterResult)]
        text_results = [
            result for result in results if isinstance(result, SearchResult) and result.result_type == "text"
        ]

        if page_jump_results:
            group = self._add_group("Page Jump")
            for result in page_jump_results:
                self._add_search_result(group, result)

        if chapter_results:
            group = self._add_group("Chapter Results")
            for chapter in chapter_results:
                self._add_chapter_result(group, chapter)

        if text_results:
            group = self._add_group("Text Matches")
            for result in text_results:
                self._add_search_result(group, result)

        self._tree.expandAll()

    def clear_results(self) -> None:
        self.set_results([])

    def _add_empty_state(self) -> None:
        item = QTreeWidgetItem(["No search results", ""])
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        self._tree.addTopLevelItem(item)

    def _add_group(self, label: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem([label, ""])
        item.setFirstColumnSpanned(True)
        self._tree.addTopLevelItem(item)
        return item

    def _add_search_result(self, parent: QTreeWidgetItem, result: SearchResult) -> None:
        item = QTreeWidgetItem([result.title, result.subtitle])
        item.setData(0, Qt.ItemDataRole.UserRole, result.page_index)
        parent.addChild(item)

    def _add_chapter_result(self, parent: QTreeWidgetItem, chapter: ChapterResult) -> None:
        chapter_item = QTreeWidgetItem([chapter.title, chapter.page_range_label()])
        chapter_item.setData(0, Qt.ItemDataRole.UserRole, chapter.start_page_index)
        parent.addChild(chapter_item)

        for page_index in range(chapter.start_page_index, chapter.end_page_index + 1):
            page_number = page_index + 1
            page_item = QTreeWidgetItem([f"Page {page_number}", "Chapter page"])
            page_item.setData(0, Qt.ItemDataRole.UserRole, page_index)
            chapter_item.addChild(page_item)

    def _handle_item_clicked(self, item: QTreeWidgetItem) -> None:
        page_index = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(page_index, int):
            self.page_selected.emit(page_index)
