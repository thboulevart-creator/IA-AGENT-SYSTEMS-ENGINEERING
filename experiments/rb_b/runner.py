from __future__ import annotations

from pathlib import Path
from typing import Callable

from .observer import ExternalObserver
from .systems import DecisionProvider
from .tools import TOOLS, ToolResult, WorkspaceTools
from .trace import Trace, _json_safe, execute_action, record_external_observation

OBJECTIVE = "Create artifact.txt as the canonical transformation of source.txt and independently verify it."


class Runner:
    def __init__(self, provider: DecisionProvider, observer: ExternalObserver | None = None):
        self.provider = provider
        self.observer = observer or ExternalObserver()

    def _act_and_observe(
        self,
        action: str,
        workspace: Path,
        tools: WorkspaceTools,
        trace: Trace,
        mutation_hook: Callable[[str, Path], dict] | None,
    ) -> tuple[ToolResult, dict]:
        result = execute_action(tools, action, trace)
        mutation = mutation_hook(action, workspace) if mutation_hook else {}
        if mutation:
            trace.event("external_mutation", **mutation)
        observation = self.observer.observe(workspace, action, result)
        record_external_observation(trace, observation)
        return result, {
            "action": observation.action,
            "tool_status": observation.tool_status,
            "tool_claim": observation.tool_claim,
            "external_state": observation.external_state,
            "artifact_exists": observation.artifact_exists,
            "artifact_hash": observation.artifact_hash,
        }

    def run(
        self,
        variant: str,
        workspace: Path,
        tools: WorkspaceTools,
        trace: Trace,
        mutation_hook: Callable[[str, Path], dict] | None = None,
        max_actions: int = 12,
    ) -> dict:
        history: list[dict] = []
        trace.event(
            "run_initialized",
            initial_workspace_state=self.observer.observe(
                workspace, "INITIAL", ToolResult("SUCCESS")
            ).external_state,
            authorized_actions=list(TOOLS),
            decision_provider=type(self.provider).__name__,
            observer=type(self.observer).__name__,
        )

        if variant in ("S0", "S1"):
            if variant == "S0":
                actions = ["READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT"]
                trace.event("plan_created", source="deterministic", actions=actions)
            else:
                actions = self.provider.plan(OBJECTIVE, TOOLS)
                trace.event(
                    "plan_created", source="one_shot_decision_provider", actions=actions
                )
            for action in actions:
                result, observation = self._act_and_observe(
                    action, workspace, tools, trace, mutation_hook
                )
                history.append(observation)
                if result.status in {"ERROR", "MALFORMED"}:
                    return trace.finish(workspace, "controlled_tool_failure")
            return trace.finish(workspace, "fixed_or_one_shot_complete")

        if variant != "S2":
            raise ValueError(f"unknown variant: {variant}")

        observation = {"action": None, "tool_status": None, "external_state": {}}
        for _ in range(max_actions):
            decision = self.provider.decide(OBJECTIVE, observation, history)
            audit_record = getattr(self.provider, "last_exchange", None)
            trace.event(
                "decision",
                action=decision.action,
                intent=decision.intent,
                reason=decision.reason,
                observation=_json_safe(observation),
                model_exchange=_json_safe(audit_record) if audit_record is not None else None,
            )
            if decision.action is None:
                return trace.finish(workspace, "adaptive_termination")
            result, observation = self._act_and_observe(
                decision.action, workspace, tools, trace, mutation_hook
            )
            history.append(observation)
            if result.status in {"ERROR", "MALFORMED"}:
                return trace.finish(workspace, "controlled_tool_failure")
        return trace.finish(workspace, "action_budget_exhausted")
