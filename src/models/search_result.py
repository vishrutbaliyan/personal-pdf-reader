from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    result_type: str
    title: str
    page_index: int
    subtitle: str = ""
    score: float = 0.0
    match_count: int = 0

    @classmethod
    def page_jump(cls, page_index: int) -> "SearchResult":
        page_number = page_index + 1
        return cls(
            result_type="page_jump",
            title=f"Go to Page {page_number}",
            page_index=page_index,
            subtitle="Direct page jump",
            score=1000.0,
        )

    @classmethod
    def text_match(
        cls,
        page_index: int,
        match_count: int,
        snippet: str,
        score: float,
    ) -> "SearchResult":
        page_number = page_index + 1
        return cls(
            result_type="text",
            title=f"Page {page_number}",
            page_index=page_index,
            subtitle=snippet,
            score=score,
            match_count=match_count,
        )
