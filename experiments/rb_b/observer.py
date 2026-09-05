from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .tools import ToolResult


def snapshot_workspace(workspace: Path) -> dict[str, str]:
    return {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(workspace.iterdir())
        if p.is_file()
    }


@dataclass(frozen=True)
class ExternalObservation:
    action: str
    tool_status: str
    tool_claim: dict[str, Any]
    external_state: dict[str, str]
    artifact_exists: bool
    artifact_hash: str | None


class ExternalObserver:
    """Observes the workspace through its own read path; it does not trust tool claims."""

    def observe(self, workspace: Path, action: str, result: ToolResult | None) -> ExternalObservation:
        state = snapshot_workspace(workspace)
        artifact = workspace / "artifact.txt"
        return ExternalObservation(
            action=action,
            tool_status=result.status if result else "ERROR",
            tool_claim=dict(result.data) if result else {},
            external_state=state,
            artifact_exists=artifact.exists(),
            artifact_hash=state.get("artifact.txt"),
        )
