from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AiProviderPort(ABC):
    @abstractmethod
    def reformat(self, text: str, policy: Dict[str, Any]) -> str:
        ...

    @abstractmethod
    def interpret(self, text: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def summarize(self, texts: List[str], context: str, policy: Dict[str, Any]) -> str:
        ...

    @abstractmethod
    def estimate_cost_cents(self, texts: List[str]) -> int:
        ...

