from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic
from typing import Any

from .oracle import OBJECTIVE_VERSION, verify_o1
from .tools import TOOLS, ToolError, ToolResult, WorkspaceTools


def workspace_state(workspace: Path) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(workspace.iterdir()) if p.is_file()}


@dataclass
class Trace:
    run_id: str
    experiment_id: str
    system_variant: str
    scenario_id: str
    random_seed: int
    events: list[dict[str, Any]] = field(default_factory=list)
    started: float = field(default_factory=monotonic)

    def event(self, kind: str, **data: Any) -> None:
        self.events.append({"seq": len(self.events), "kind": kind, **data})

    def finish(self, workspace: Path, outcome: str, termination: str) -> dict[str, Any]:
        oracle = verify_o1(workspace)
        state = workspace_state(workspace)
        final_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        return {
            "run_id": self.run_id, "experiment_id": self.experiment_id,
            "system_variant": self.system_variant, "objective_version": OBJECTIVE_VERSION,
            "scenario_id": self.scenario_id, "random_seed": self.random_seed,
            "events": self.events, "verification": oracle.__dict__,
            "final_workspace_hash": final_hash, "final_state": state,
            "final_outcome": outcome, "termination_reason": termination,
            "elapsed_seconds": monotonic() - self.started,
        }


def execute_action(tools: WorkspaceTools, action: str, trace: Trace) -> ToolResult | None:
    trace.event("action_proposed", action=action)
    authorized = action in TOOLS
    trace.event("authorization", action=action, authorized=authorized)
    if not authorized:
        trace.event("tool_execution", action=action, status="ERROR", error_type="GOVERNANCE")
        return None
    try:
        result = tools.call(action)
        trace.event("tool_execution", action=action, status=result.status,
                    data=result.data, error_type=result.error_type,
                    workspace_state=workspace_state(tools.workspace))
        return result
    except ToolError as exc:
        trace.event("tool_execution", action=action, status="ERROR",
                    error_type=exc.kind, message=str(exc),
                    workspace_state=workspace_state(tools.workspace))
        return None
