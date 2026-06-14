from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
STYLE_DIR = SRC_ROOT / "ui" / "styles"

LIGHT_STYLE_PATH = STYLE_DIR / "light.qss"
