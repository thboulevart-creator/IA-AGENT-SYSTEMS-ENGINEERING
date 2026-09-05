from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .oracle import canonical_transform

TOOLS = ("READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT", "REPAIR_ARTIFACT")


@dataclass
class FaultPlan:
    unavailable: set[str] = field(default_factory=set)
    timeout: set[str] = field(default_factory=set)
    malformed: set[str] = field(default_factory=set)
    execution_error: set[str] = field(default_factory=set)
    false_success: set[str] = field(default_factory=set)


class ToolError(RuntimeError):
    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


@dataclass
class ToolResult:
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    error_type: str | None = None


class WorkspaceTools:
    def __init__(self, workspace: Path, faults: FaultPlan | None = None):
        self.workspace = workspace
        self.faults = faults or FaultPlan()

    def call(self, name: str) -> ToolResult:
        if name not in TOOLS:
            raise ToolError("GOVERNANCE", f"unauthorized tool: {name}")
        if name in self.faults.unavailable:
            raise ToolError("UNAVAILABLE", f"tool unavailable: {name}")
        if name in self.faults.timeout:
            raise ToolError("TIMEOUT", f"tool timeout: {name}")
        if name in self.faults.malformed:
            return ToolResult("MALFORMED", {"malformed": True}, "MALFORMED_RESPONSE")
        if name in self.faults.execution_error:
            raise ToolError("EXECUTION_ERROR", f"deterministic execution error: {name}")

        if name == "READ_SOURCE":
            data = (self.workspace / "source.txt").read_bytes()
            return ToolResult("SUCCESS", {"bytes": data, "sha256": __import__("hashlib").sha256(data).hexdigest()})

        if name == "WRITE_ARTIFACT":
            source = (self.workspace / "source.txt").read_bytes()
            if name not in self.faults.false_success:
                (self.workspace / "artifact.txt").write_bytes(canonical_transform(source))
            return ToolResult("SUCCESS", {"written": name not in self.faults.false_success})

        if name == "CHECK_ARTIFACT":
            source = self.workspace / "source.txt"
            artifact = self.workspace / "artifact.txt"
            if not source.exists() or not artifact.exists():
                return ToolResult("FAIL", {"match": False, "reason": "missing file"})
            expected = canonical_transform(source.read_bytes())
            actual = artifact.read_bytes()
            return ToolResult("PASS" if actual == expected else "FAIL", {"match": actual == expected})

        source = (self.workspace / "source.txt").read_bytes()
        (self.workspace / "artifact.txt").write_bytes(canonical_transform(source))
        return ToolResult("SUCCESS", {"repaired": True})
