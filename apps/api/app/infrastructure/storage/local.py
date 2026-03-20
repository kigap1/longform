from __future__ import annotations

from pathlib import Path, PurePosixPath

from app.infrastructure.storage.types import StoredObject


class LocalStorage:
    def __init__(self, root: str) -> None:
        self.root = Path(root).expanduser().resolve()

    def save_bytes(self, *, key: str, payload: bytes, content_type: str) -> StoredObject:
        normalized_key = PurePosixPath(key)
        if normalized_key.is_absolute() or ".." in normalized_key.parts:
            raise ValueError(f"Invalid storage key: {key}")

        target = self.root.joinpath(*normalized_key.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

        return StoredObject(
            key=normalized_key.as_posix(),
            url=str(target),
            content_type=content_type,
        )
