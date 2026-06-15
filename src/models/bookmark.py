from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Bookmark:
    bookmark_id: str
    document_id: str
    page_index: int
    label: str
    created_at: str
    pinned: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bookmark":
        return cls(
            bookmark_id=str(data.get("bookmark_id") or _legacy_bookmark_id(data)),
            document_id=str(data.get("document_id", "")),
            page_index=int(data.get("page_index", 0)),
            label=str(data.get("label", "")),
            created_at=str(data.get("created_at", "")),
            pinned=bool(data.get("pinned", False)),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "bookmark_id": self.bookmark_id,
            "document_id": self.document_id,
            "page_index": self.page_index,
            "label": self.label,
            "created_at": self.created_at,
            "pinned": self.pinned,
        }


def _legacy_bookmark_id(data: dict[str, object]) -> str:
    fingerprint = "|".join(
        [
            str(data.get("document_id", "")),
            str(data.get("page_index", "")),
            str(data.get("label", "")),
            str(data.get("created_at", "")),
        ]
    )
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
