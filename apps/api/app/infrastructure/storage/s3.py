from __future__ import annotations

from app.infrastructure.storage.types import StoredObject


class S3CompatibleStorage:
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

    def save_bytes(self, *, key: str, payload: bytes, content_type: str) -> StoredObject:
        # TODO: Connect a real S3-compatible client and upload payload bytes.
        raise NotImplementedError(
            f"S3 storage upload is not implemented yet for bucket '{self.bucket_name}'. "
            "Use STORAGE_MODE=local until the production adapter is connected."
        )
