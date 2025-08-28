from __future__ import annotations

import hashlib
import hmac
from typing import Any, Dict

from app.config import settings
from app.ports.teams import TeamsPort


class MockTeamsAdapter(TeamsPort):
    async def send_message(self, external_user_id: str, content: str) -> None:
        # In real life: call MS Graph; here we noop/log
        return None

    def validate_credentials(self, tenant_id: str, app_id: str, secret_or_cert: str) -> bool:
        # Stub: any non-empty is "valid"
        return bool(app_id and secret_or_cert)

    def link_user_to_channel(self, tenant_id: str, user_id: str, channel_ref: str) -> None:
        return None

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        if not settings.teams_webhook_secret:
            return True
        digest = hmac.new(settings.teams_webhook_secret.encode(), payload, hashlib.sha256).hexdigest()
        # Constant-time compare
        return hmac.compare_digest(digest, signature)

    async def receive_response(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize: assume payload has fields 'external_user_id', 'text', 'timestamp', 'event_id'
        return {
            "external_user_id": webhook_payload.get("external_user_id", "unknown"),
            "text": webhook_payload.get("text", ""),
            "timestamp": webhook_payload.get("timestamp"),
            "event_id": webhook_payload.get("event_id"),
        }

