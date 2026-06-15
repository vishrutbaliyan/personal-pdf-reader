from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget


class NavigationControls(QFrame):
    previous_requested = pyqtSignal()
    next_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("NavigationControls")
        self.setFixedWidth(116)

        self._next_button = QPushButton("Next >")
        self._previous_button = QPushButton("Previous <")

        self._next_button.clicked.connect(self.next_requested.emit)
        self._previous_button.clicked.connect(self.previous_requested.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        layout.addStretch(1)
        layout.addWidget(self._next_button)
        layout.addWidget(self._previous_button)
        layout.addStretch(1)

        self.update_state(can_go_previous=False, can_go_next=False)

    def update_state(self, can_go_previous: bool, can_go_next: bool) -> None:
        self._previous_button.setEnabled(can_go_previous)
        self._next_button.setEnabled(can_go_next)
