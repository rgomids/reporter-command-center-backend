from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class TeamsPort(ABC):
    @abstractmethod
    async def send_message(self, external_user_id: str, content: str) -> None:
        ...

    @abstractmethod
    def validate_credentials(self, tenant_id: str, app_id: str, secret_or_cert: str) -> bool:
        ...

    @abstractmethod
    def link_user_to_channel(self, tenant_id: str, user_id: str, channel_ref: str) -> None:
        ...

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        ...

    @abstractmethod
    async def receive_response(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize webhook payload to internal structure with dedupe id."""

