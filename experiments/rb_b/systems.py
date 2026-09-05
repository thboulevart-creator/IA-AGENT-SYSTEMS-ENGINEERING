from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Decision:
    action: str | None
    intent: str
    reason: str


class DecisionProvider(Protocol):
    def plan(self, objective: str, tools: tuple[str, ...]) -> list[str]: ...
    def decide(self, objective: str, observation: dict[str, Any], history: list[dict[str, Any]]) -> Decision: ...


class ScriptedDecisionProvider:
    """Deterministic stand-in for a model; it tests runtime structure, not LLM quality."""

    def plan(self, objective: str, tools: tuple[str, ...]) -> list[str]:
        return ["READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT"]

    def decide(self, objective: str, observation: dict[str, Any], history: list[dict[str, Any]]) -> Decision:
        last = observation.get("tool")
        status = observation.get("status")
        if last == "CHECK_ARTIFACT" and status == "FAIL":
            return Decision("REPAIR_ARTIFACT", "repair after verified mismatch", "CHECK_ARTIFACT reported FAIL")
        if not history:
            return Decision("READ_SOURCE", "begin objective", "no prior action")
        if last == "READ_SOURCE":
            return Decision("WRITE_ARTIFACT", "create artifact", "source was observed")
        if last == "WRITE_ARTIFACT":
            return Decision("CHECK_ARTIFACT", "verify artifact", "write completed")
        if last == "REPAIR_ARTIFACT":
            return Decision("CHECK_ARTIFACT", "verify repair", "repair completed")
        if last == "CHECK_ARTIFACT" and status == "PASS":
            return Decision(None, "terminate", "verification passed")
        return Decision(None, "terminate", "no valid next action")
