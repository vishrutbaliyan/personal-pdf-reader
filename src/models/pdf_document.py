from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PdfDocument:
    document_id: str
    file_path: Path
    title: str
    page_count: int
