from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget


class PdfViewer(QWidget):
    """Scrollable widget that displays a rendered PDF page image."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PdfViewer")

        self._page_label = QLabel("Open a PDF to start reading")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("PdfScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_area.setWidget(self._page_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll_area)

    def set_page_image(self, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image)
        self._page_label.setPixmap(pixmap)
        self._page_label.setText("")
        self._page_label.resize(pixmap.size())

    def clear(self) -> None:
        self._page_label.clear()
        self._page_label.setText("Open a PDF to start reading")
