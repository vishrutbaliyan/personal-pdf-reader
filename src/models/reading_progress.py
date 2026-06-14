from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadingProgress:
    document_id: str
    file_path: str
    page_index: int
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReadingProgress":
        return cls(
            document_id=str(data.get("document_id", "")),
            file_path=str(data.get("file_path", "")),
            page_index=int(data.get("page_index", 0)),
            updated_at=str(data.get("updated_at", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "file_path": self.file_path,
            "page_index": self.page_index,
            "updated_at": self.updated_at,
        }
