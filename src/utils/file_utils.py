from __future__ import annotations

from pathlib import Path


def is_pdf_file(file_path: Path) -> bool:
    return file_path.is_file() and file_path.suffix.lower() == ".pdf"


def display_file_name(file_path: Path) -> str:
    return file_path.stem or file_path.name
