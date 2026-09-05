from __future__ import annotations

from pathlib import Path
from typing import Callable

from .oracle import verify_o1
from .systems import DecisionProvider
from .tools import TOOLS, WorkspaceTools
from .trace import Trace, execute_action, workspace_state

OBJECTIVE = "Create artifact.txt as the canonical transformation of source.txt and independently verify it."


class Runner:
    def __init__(self, provider: DecisionProvider):
        self.provider = provider

    def run(self, variant: str, workspace: Path, tools: WorkspaceTools, trace: Trace,
            mutation_hook: Callable[[str, Path, Trace], None] | None = None,
            max_actions: int = 12) -> dict:
        history: list[dict] = []
        trace.event("run_initialized", initial_workspace_state=workspace_state(workspace),
                    authorized_actions=list(TOOLS), decision_provider=type(self.provider).__name__)

        if variant == "S0":
            actions = ["READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT"]
            trace.event("plan_created", source="deterministic", actions=actions)
            for action in actions:
                result = execute_action(tools, action, trace)
                history.append({"tool": action, "status": result.status if result else "ERROR"})
                if mutation_hook:
                    mutation_hook(action, workspace, trace)
            oracle = verify_o1(workspace)
            trace.event("verification", source="independent_oracle", result=oracle.__dict__)
            return trace.finish(workspace, oracle.status, "fixed_path_complete")

        if variant == "S1":
            plan = self.provider.plan(OBJECTIVE, TOOLS)
            trace.event("plan_created", source="one_shot_decision_provider", actions=plan)
            for action in plan:
                result = execute_action(tools, action, trace)
                history.append({"tool": action, "status": result.status if result else "ERROR"})
                if mutation_hook:
                    mutation_hook(action, workspace, trace)
            oracle = verify_o1(workspace)
            trace.event("verification", source="independent_oracle", result=oracle.__dict__)
            return trace.finish(workspace, oracle.status, "one_shot_plan_complete")

        if variant != "S2":
            raise ValueError(f"unknown variant: {variant}")

        observation = {"tool": None, "status": None}
        for _ in range(max_actions):
            decision = self.provider.decide(OBJECTIVE, observation, history)
            trace.event("decision", action=decision.action, intent=decision.intent,
                        reason=decision.reason, observation=observation)
            if decision.action is None:
                oracle = verify_o1(workspace)
                trace.event("verification", source="independent_oracle", result=oracle.__dict__)
                return trace.finish(workspace, oracle.status, "adaptive_termination")
            result = execute_action(tools, decision.action, trace)
            status = result.status if result else "ERROR"
            observation = {"tool": decision.action, "status": status,
                           "data": result.data if result else {}}
            trace.event("observation", **observation)
            history.append(observation)
            if mutation_hook:
                mutation_hook(decision.action, workspace, trace)
        return trace.finish(workspace, "BLOCKED", "action_budget_exhausted")
