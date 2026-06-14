from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
STYLE_DIR = SRC_ROOT / "ui" / "styles"

PROGRESS_FILE_PATH = DATA_DIR / "progress.json"
BOOKMARKS_FILE_PATH = DATA_DIR / "bookmarks.json"
LIGHT_STYLE_PATH = STYLE_DIR / "light.qss"
