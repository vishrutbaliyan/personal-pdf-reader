from __future__ import annotations

from src.config.paths import PROGRESS_FILE_PATH
from src.models.pdf_document import PdfDocument
from src.models.reading_progress import ReadingProgress
from src.storage.json_store import JsonStore
from src.utils.time_utils import current_timestamp


class ProgressStore:
    """Persists last-read page data keyed by document_id."""

    def __init__(self, json_store: JsonStore | None = None) -> None:
        self._json_store = json_store or JsonStore(PROGRESS_FILE_PATH)

    def get_progress(self, document_id: str) -> ReadingProgress | None:
        data = self._json_store.read()
        raw_progress = data.get(document_id)

        if not isinstance(raw_progress, dict):
            return None

        try:
            progress = ReadingProgress.from_dict(raw_progress)
        except (TypeError, ValueError):
            return None

        if progress.document_id != document_id:
            return None

        return progress

    def save_progress(self, document: PdfDocument, page_index: int) -> None:
        data = self._json_store.read()
        data[document.document_id] = ReadingProgress(
            document_id=document.document_id,
            file_path=str(document.file_path),
            page_index=page_index,
            updated_at=current_timestamp(),
        ).to_dict()
        self._json_store.write(data)
