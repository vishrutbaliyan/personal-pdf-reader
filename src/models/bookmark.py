from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bookmark:
    document_id: str
    page_index: int
    label: str
    created_at: str

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bookmark":
        return cls(
            document_id=str(data.get("document_id", "")),
            page_index=int(data.get("page_index", 0)),
            label=str(data.get("label", "")),
            created_at=str(data.get("created_at", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "page_index": self.page_index,
            "label": self.label,
            "created_at": self.created_at,
        }
