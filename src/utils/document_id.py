from __future__ import annotations

import hashlib
from pathlib import Path


def build_document_id(file_path: Path) -> str:
    """Build a stable ID from the resolved PDF path."""
    normalized_path = str(file_path.resolve()).lower()
    return hashlib.sha256(normalized_path.encode("utf-8")).hexdigest()
