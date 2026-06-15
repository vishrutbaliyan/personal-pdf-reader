from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChapterResult:
    title: str
    start_page_index: int
    end_page_index: int
    level: int = 1
    score: float = 0.0

    def page_range_label(self) -> str:
        start_page = self.start_page_index + 1
        end_page = self.end_page_index + 1
        return f"Pages {start_page}-{end_page}"
