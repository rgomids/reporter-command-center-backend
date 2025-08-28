from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.adapters.ai.dummy import DummyAiProvider
from app.infra.repos import ResponseRepository
from app.config import settings


@dataclass
class ProcessingPolicies:
    normalize_case: bool = True
    summary_limit: int = 280


class ProcessingService:
    def __init__(self, session: Session) -> None:
        self.ai = DummyAiProvider()
        self.responses = ResponseRepository(session)

    def treat(self, text: str, org_policy: Dict[str, Any], user_override: str | None) -> str:
        policy = {"normalize_case": True, **org_policy}
        reformatted = self.ai.reformat(text, policy)
        interpreted = self.ai.interpret(reformatted, policy)
        # For MVP, treated text is reformatted + basic markers
        treated = reformatted
        if user_override:
            treated = f"[{user_override}] {treated}"
        return treated

    def summarize_day(self, texts: List[str], context: str, policy: Dict[str, Any]) -> str:
        estimated = self.ai.estimate_cost_cents(texts)
        if estimated > settings.ai_max_cost_per_day_cents:
            # Enforce simple cost cap per call/day
            return "[Limite de custo de IA excedido. Resumo não gerado.]"
        return self.ai.summarize(texts, context, policy)
