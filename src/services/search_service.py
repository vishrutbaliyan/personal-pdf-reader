from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypeAlias

from src.models.chapter_result import ChapterResult
from src.models.pdf_document import PdfDocument
from src.models.search_result import SearchResult
from src.services.exceptions import PdfReaderError
from src.services.pdf_service import PdfService


SmartSearchItem: TypeAlias = SearchResult | ChapterResult


@dataclass
class _SearchIndexCache:
    document_id: str
    page_text: dict[int, str]
    chapters: list[ChapterResult]


class SearchService:
    """Unified smart search for page jumps, chapters, and full-text matches."""

    _CHAPTER_QUERY_RE = re.compile(r"^\s*(?:chapter|ch\.?)\s+([0-9]+|[ivxlcdm]+)\s*$", re.IGNORECASE)
    _CHAPTER_HEADING_RE = re.compile(
        r"^\s*(?:chapter|ch\.?)\s+([0-9]+|[ivxlcdm]+)\b[:.\-\s]*(.{0,90})$",
        re.IGNORECASE,
    )
    _NUMBERED_HEADING_RE = re.compile(r"^\s*([0-9]{1,3})[.)]?\s+([A-Z][^\n]{3,90})$")

    def __init__(self, pdf_service: PdfService) -> None:
        self._pdf_service = pdf_service
        self._current_document: PdfDocument | None = None
        self._cache: _SearchIndexCache | None = None

    def set_document(self, document: PdfDocument | None) -> None:
        document_id = document.document_id if document else None
        cached_document_id = self._cache.document_id if self._cache else None

        self._current_document = document
        if document_id != cached_document_id:
            self._cache = None

    def search(self, query: str) -> list[SmartSearchItem]:
        document = self._require_document()
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        page_jump = self._page_jump_result(cleaned_query, document.page_count)
        if page_jump is not None:
            return [page_jump]

        cache = self._ensure_cache(document)
        chapter_results = self._search_chapters(cleaned_query, cache.chapters)
        text_results = self._search_text(cleaned_query, cache.page_text)
        return [*chapter_results, *text_results]

    def _ensure_cache(self, document: PdfDocument) -> _SearchIndexCache:
        if self._cache is not None and self._cache.document_id == document.document_id:
            return self._cache

        page_text = self._pdf_service.extract_all_page_text()
        chapters = self._extract_chapters(document, page_text)
        self._cache = _SearchIndexCache(
            document_id=document.document_id,
            page_text=page_text,
            chapters=chapters,
        )
        return self._cache

    def _extract_chapters(self, document: PdfDocument, page_text: dict[int, str]) -> list[ChapterResult]:
        toc_chapters = self._chapters_from_toc(document.page_count)
        if toc_chapters:
            return toc_chapters

        return self._fallback_chapters_from_text(document.page_count, page_text)

    def _chapters_from_toc(self, page_count: int) -> list[ChapterResult]:
        toc_entries = self._pdf_service.get_toc()
        chapters: list[ChapterResult] = []

        for index, entry in enumerate(toc_entries):
            level, title, start_page_index = entry
            end_page_index = page_count - 1

            for next_entry in toc_entries[index + 1 :]:
                next_level, _, next_page_index = next_entry
                if next_level <= level:
                    end_page_index = max(start_page_index, next_page_index - 1)
                    break

            chapters.append(
                ChapterResult(
                    title=title,
                    start_page_index=start_page_index,
                    end_page_index=end_page_index,
                    level=level,
                )
            )

        return chapters

    def _fallback_chapters_from_text(
        self,
        page_count: int,
        page_text: dict[int, str],
    ) -> list[ChapterResult]:
        starts: list[tuple[int, str]] = []

        for page_index in range(page_count):
            for line in self._heading_candidates(page_text.get(page_index, "")):
                chapter_title = self._chapter_title_from_heading(line)
                if chapter_title:
                    starts.append((page_index, chapter_title))
                    break

        chapters: list[ChapterResult] = []
        for index, (start_page_index, title) in enumerate(starts):
            next_start = starts[index + 1][0] if index + 1 < len(starts) else page_count
            chapters.append(
                ChapterResult(
                    title=title,
                    start_page_index=start_page_index,
                    end_page_index=max(start_page_index, next_start - 1),
                )
            )

        return chapters

    def _search_chapters(self, query: str, chapters: list[ChapterResult]) -> list[ChapterResult]:
        normalized_query = self._normalize(query)
        chapter_number = self._chapter_number_from_query(query)
        matches: list[ChapterResult] = []

        for chapter in chapters:
            normalized_title = self._normalize(chapter.title)
            score = 0.0

            if chapter_number and self._chapter_number_in_title(chapter_number, chapter.title):
                score = 500.0
            elif normalized_title == normalized_query:
                score = 400.0
            elif normalized_query in normalized_title:
                score = 250.0

            if score > 0:
                matches.append(
                    ChapterResult(
                        title=chapter.title,
                        start_page_index=chapter.start_page_index,
                        end_page_index=chapter.end_page_index,
                        level=chapter.level,
                        score=score,
                    )
                )

        return sorted(matches, key=lambda item: (-item.score, item.start_page_index))

    def _search_text(self, query: str, page_text: dict[int, str]) -> list[SearchResult]:
        normalized_query = query.lower()
        results: list[SearchResult] = []

        for page_index, text in page_text.items():
            lowered_text = text.lower()
            match_count = lowered_text.count(normalized_query)
            if match_count == 0:
                continue

            heading_bonus = 25.0 if normalized_query in self._first_lines(text).lower() else 0.0
            score = match_count * 10.0 + heading_bonus
            results.append(
                SearchResult.text_match(
                    page_index=page_index,
                    match_count=match_count,
                    snippet=self._snippet(text, normalized_query),
                    score=score,
                )
            )

        return sorted(results, key=lambda item: (-item.score, item.page_index))

    def _page_jump_result(self, query: str, page_count: int) -> SearchResult | None:
        if not query.isdigit():
            return None

        page_number = int(query)
        if page_number < 1 or page_number > page_count:
            raise PdfReaderError(f"Page number must be between 1 and {page_count}.")

        return SearchResult.page_jump(page_number - 1)

    def _heading_candidates(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return [line for line in lines[:8] if len(line) <= 120]

    def _chapter_title_from_heading(self, line: str) -> str | None:
        chapter_match = self._CHAPTER_HEADING_RE.match(line)
        if chapter_match:
            suffix = chapter_match.group(2).strip()
            chapter_number = chapter_match.group(1)
            return f"Chapter {chapter_number}: {suffix}" if suffix else f"Chapter {chapter_number}"

        numbered_match = self._NUMBERED_HEADING_RE.match(line)
        if numbered_match:
            number, title = numbered_match.groups()
            return f"Chapter {number}: {title.strip()}"

        return None

    def _chapter_number_from_query(self, query: str) -> str | None:
        match = self._CHAPTER_QUERY_RE.match(query)
        return match.group(1).lower() if match else None

    def _chapter_number_in_title(self, chapter_number: str, title: str) -> bool:
        normalized_number = re.escape(chapter_number.lower())
        pattern = rf"\b(?:chapter|ch\.?)\s+{normalized_number}\b|\b{normalized_number}[.)]?\s+"
        return re.search(pattern, title.lower()) is not None

    def _snippet(self, text: str, lowered_query: str) -> str:
        lowered_text = text.lower()
        match_index = lowered_text.find(lowered_query)
        if match_index < 0:
            return ""

        start = max(0, match_index - 50)
        end = min(len(text), match_index + len(lowered_query) + 70)
        snippet = " ".join(text[start:end].split())
        return f"...{snippet}..."

    def _first_lines(self, text: str) -> str:
        return "\n".join(text.splitlines()[:8])

    def _normalize(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def _require_document(self) -> PdfDocument:
        if self._current_document is None:
            raise PdfReaderError("Open a PDF before using smart search.")
        return self._current_document
