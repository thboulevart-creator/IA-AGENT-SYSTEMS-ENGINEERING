from __future__ import annotations

import argparse
import json
import tempfile
import uuid
from pathlib import Path

from .observer import snapshot_workspace
from .oracle import OBJECTIVE_VERSION
from .runner import Runner
from .systems import ScriptedDecisionProvider
from .tools import FaultPlan, WorkspaceTools
from .trace import Trace

SCENARIOS = {
    0: "  HELLO World!  ",
    1: "MiXeD Case\nwith whitespace\n",
    2: "UTF-8: Éléphant — CAFÉ  ",
    3: "repeat repeat REPEAT",
    4: "line one\nLINE TWO\n",
}


def corrupt_after_write(action: str, workspace: Path) -> dict:
    if action != "WRITE_ARTIFACT":
        return {}
    artifact = workspace / "artifact.txt"
    data = artifact.read_bytes() if artifact.exists() else b"x"
    if data:
        artifact.write_bytes(data[:-1] + (b"X" if data[-1:] != b"X" else b"Y"))
    else:
        artifact.write_bytes(b"X")
    return {"target": "artifact.txt", "mutation": "deterministic_corruption"}


def make_fault(experiment: str) -> FaultPlan:
    faults = FaultPlan()
    if experiment == "E3":
        faults.false_success.add("WRITE_ARTIFACT")
    elif experiment == "E4-A":
        faults.unavailable.add("WRITE_ARTIFACT")
    elif experiment == "E4-B":
        faults.timeout.add("WRITE_ARTIFACT")
    elif experiment == "E4-C":
        faults.malformed.add("WRITE_ARTIFACT")
    elif experiment == "E4-D":
        faults.execution_error.add("WRITE_ARTIFACT")
    return faults


def run_one(experiment: str, variant: str, scenario_id: int, seed: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="rb-b-") as tmp:
        workspace = Path(tmp)
        (workspace / "source.txt").write_text(SCENARIOS[scenario_id], encoding="utf-8")
        trace = Trace(str(uuid.uuid4()), experiment, variant, str(scenario_id), seed)
        tools = WorkspaceTools(workspace, make_fault(experiment))
        hook = corrupt_after_write if experiment == "E2" else None
        result = Runner(ScriptedDecisionProvider()).run(variant, workspace, tools, trace, hook)
        result["objective_version"] = OBJECTIVE_VERSION
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="RB-B minimal experimental harness")
    parser.add_argument("--experiment", default="E1", choices=["E1", "E2", "E3", "E4-A", "E4-B", "E4-C", "E4-D"])
    parser.add_argument("--variant", default="S0", choices=["S0", "S1", "S2"])
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("experiments/rb_b/results.jsonl"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as fh:
        for i in range(args.runs):
            record = run_one(args.experiment, args.variant, i % len(SCENARIOS), i)
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            print(json.dumps({"run_id": record["run_id"], "outcome": record["final_outcome"],
                              "verification": record["verification"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
