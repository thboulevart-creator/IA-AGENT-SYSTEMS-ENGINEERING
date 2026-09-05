from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic
from typing import Any

from .oracle import OBJECTIVE_VERSION, verify_o1
from .observer import ExternalObservation, snapshot_workspace
from .tools import TOOLS, ToolError, ToolResult, WorkspaceTools


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

    def finish(self, workspace: Path, termination: str) -> dict[str, Any]:
        oracle = verify_o1(workspace)
        state = snapshot_workspace(workspace)
        final_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        return {
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "system_variant": self.system_variant,
            "objective_version": OBJECTIVE_VERSION,
            "scenario_id": self.scenario_id,
            "random_seed": self.random_seed,
            "events": self.events,
            "verification": oracle.__dict__,
            "final_workspace_hash": final_hash,
            "final_state": state,
            "final_outcome": oracle.status,
            "termination_reason": termination,
            "elapsed_seconds": monotonic() - self.started,
        }


def execute_action(tools: WorkspaceTools, action: str, trace: Trace) -> ToolResult:
    trace.event("action_proposed", action=action)
    authorized = action in TOOLS
    trace.event("authorization", action=action, authorized=authorized)
    if not authorized:
        result = ToolResult("ERROR", {}, "GOVERNANCE")
        trace.event("tool_execution", action=action, status=result.status,
                    error_type=result.error_type,
                    workspace_state=snapshot_workspace(tools.workspace))
        return result
    try:
        result = tools.call(action)
        trace.event("tool_execution", action=action, status=result.status,
                    data=result.data, error_type=result.error_type,
                    workspace_state=snapshot_workspace(tools.workspace))
        return result
    except ToolError as exc:
        result = ToolResult("ERROR", {}, exc.kind)
        trace.event("tool_execution", action=action, status=result.status,
                    error_type=result.error_type, message=str(exc),
                    workspace_state=snapshot_workspace(tools.workspace))
        return result


def record_external_observation(trace: Trace, observation: ExternalObservation) -> None:
    trace.event(
        "observation",
        action=observation.action,
        tool_status=observation.tool_status,
        tool_claim=observation.tool_claim,
        external_state=observation.external_state,
        artifact_exists=observation.artifact_exists,
        artifact_hash=observation.artifact_hash,
    )
