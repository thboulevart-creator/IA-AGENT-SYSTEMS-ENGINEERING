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
    """Deterministic controller; it is ignorant of experiment identifiers and fault injection."""

    def plan(self, objective: str, tools: tuple[str, ...]) -> list[str]:
        return ["READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT"]

    def decide(self, objective: str, observation: dict[str, Any], history: list[dict[str, Any]]) -> Decision:
        action = observation.get("action")
        status = observation.get("tool_status")
        if action is None:
            return Decision("READ_SOURCE", "begin objective", "no prior observation")
        if status == "ERROR" or status == "MALFORMED":
            return Decision(None, "controlled termination", "tool failure is not automatically retryable")
        if action == "READ_SOURCE":
            return Decision("WRITE_ARTIFACT", "create artifact", "source observation received")
        if action == "WRITE_ARTIFACT":
            return Decision("CHECK_ARTIFACT", "verify artifact", "write execution observed")
        if action == "CHECK_ARTIFACT" and status == "FAIL":
            return Decision("REPAIR_ARTIFACT", "repair verified mismatch", "verification failure observed")
        if action == "REPAIR_ARTIFACT":
            return Decision("CHECK_ARTIFACT", "verify repair", "repair execution observed")
        if action == "CHECK_ARTIFACT" and status == "PASS":
            return Decision(None, "terminate", "verification passed")
        return Decision(None, "controlled termination", "no valid next action")
