from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class StoredObject:
    key: str
    url: str
    content_type: str


class StoragePort(Protocol):
    def save_bytes(self, *, key: str, payload: bytes, content_type: str) -> StoredObject: ...
