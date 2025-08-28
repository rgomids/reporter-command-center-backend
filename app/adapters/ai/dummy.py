from __future__ import annotations

from typing import List, Dict, Any
from app.ports.ai import AiProviderPort


class DummyAiProvider(AiProviderPort):
    def reformat(self, text: str, policy: Dict[str, Any]) -> str:
        text = text.strip()
        if policy.get("normalize_case"):
            text = text.capitalize()
        return text

    def interpret(self, text: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        return {"length": len(text), "keywords": text.split()[:3]}

    def summarize(self, texts: List[str], context: str, policy: Dict[str, Any]) -> str:
        joined = " ".join(t.strip() for t in texts if t)
        limit = int(policy.get("summary_limit", 280))
        base = (context + " ").strip() + joined
        return base[:limit]

    def estimate_cost_cents(self, texts: List[str]) -> int:
        tokens = sum(max(1, len(t) // 4) for t in texts)
        return int(tokens * 0.01)  # 1 cent per 100 tokens aprox

