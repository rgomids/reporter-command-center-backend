from __future__ import annotations

import os


def resolve_secret(ref: str) -> str:
    """Resolve a secret reference.

    Supported formats:
    - secretsmanager://... (AWS) → here, read from env mirror for local dev
    - literal values
    """
    if ref.startswith("secretsmanager://"):
        # local dev convention: replace path slashes by underscores and uppercase
        key = ref.replace("secretsmanager://", "").replace("/", "_").upper()
        return os.getenv(key, "")
    return ref

