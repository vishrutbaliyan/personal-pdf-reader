from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecentBook:
    document_id: str
    file_path: str
    title: str
    last_opened_at: str

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RecentBook":
        return cls(
            document_id=str(data.get("document_id", "")),
            file_path=str(data.get("file_path", "")),
            title=str(data.get("title", "")),
            last_opened_at=str(data.get("last_opened_at", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "file_path": self.file_path,
            "title": self.title,
            "last_opened_at": self.last_opened_at,
        }