from __future__ import annotations

import argparse
import json
import tempfile
import uuid
from pathlib import Path

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
VARIANTS = ("S0", "S1", "S2")
FORMAL_RUNS = 20


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


def run_one(
    experiment: str,
    variant: str,
    scenario_id: int,
    seed: int,
    *,
    perturb: bool = False,
) -> dict:
    with tempfile.TemporaryDirectory(prefix="rb-b-") as tmp:
        workspace = Path(tmp)
        (workspace / "source.txt").write_text(SCENARIOS[scenario_id], encoding="utf-8")
        trace = Trace(str(uuid.uuid4()), experiment, variant, str(scenario_id), seed)
        tools = WorkspaceTools(workspace, make_fault(experiment))
        hook = corrupt_after_write if perturb else None
        result = Runner(ScriptedDecisionProvider()).run(variant, workspace, tools, trace, hook)
        result["condition"] = "perturbed" if perturb else "normal"
        result["objective_version"] = OBJECTIVE_VERSION
        result["initial_workspace_state"] = trace.events[0]["initial_workspace_state"]
        return result


def run_formal_e1(output_dir: Path, runs_per_variant: int = FORMAL_RUNS) -> None:
    if runs_per_variant != FORMAL_RUNS:
        raise ValueError("formal E1 requires exactly 20 runs per variant")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "experiment": "E1",
        "objective_version": OBJECTIVE_VERSION,
        "runs_per_variant": FORMAL_RUNS,
        "variants": list(VARIANTS),
        "scenario_count": len(SCENARIOS),
        "schedule": "scenario_id = run_index mod 5; seed = run_index",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for variant in VARIANTS:
        output = output_dir / f"e1-{variant.lower()}.jsonl"
        if output.exists():
            output.unlink()
        with output.open("w", encoding="utf-8") as fh:
            for i in range(runs_per_variant):
                record = run_one("E1", variant, i % len(SCENARIOS), i)
                fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                print(json.dumps({"variant": variant, "run": i + 1, "run_id": record["run_id"],
                                  "outcome": record["final_outcome"],
                                  "verification": record["verification"]["status"]}, ensure_ascii=False))


def run_formal_e2(output_dir: Path, runs_per_variant: int = FORMAL_RUNS) -> None:
    if runs_per_variant != FORMAL_RUNS:
        raise ValueError("formal E2 requires exactly 20 paired runs per variant")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "experiment": "E2",
        "objective_version": OBJECTIVE_VERSION,
        "runs_per_variant": FORMAL_RUNS,
        "paired_runs_per_variant": FORMAL_RUNS,
        "variants": list(VARIANTS),
        "scenario_count": len(SCENARIOS),
        "schedule": "scenario_id = run_index mod 5; seed = run_index; normal and perturbed share the same pair key",
        "perturbation": "deterministic byte corruption after WRITE_ARTIFACT and before the next decision",
        "controller": "ScriptedDecisionProvider",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for variant in VARIANTS:
        output = output_dir / f"e2-{variant.lower()}.jsonl"
        if output.exists():
            output.unlink()
        with output.open("w", encoding="utf-8") as fh:
            for i in range(runs_per_variant):
                scenario_id = i % len(SCENARIOS)
                normal = run_one("E2", variant, scenario_id, i, perturb=False)
                perturbed = run_one("E2", variant, scenario_id, i, perturb=True)
                fh.write(json.dumps(normal, ensure_ascii=False, sort_keys=True) + "\n")
                fh.write(json.dumps(perturbed, ensure_ascii=False, sort_keys=True) + "\n")
                print(json.dumps({
                    "variant": variant,
                    "pair": i + 1,
                    "normal_outcome": normal["final_outcome"],
                    "perturbed_outcome": perturbed["final_outcome"],
                }, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="RB-B minimal experimental harness")
    parser.add_argument("--experiment", default="E1", choices=["E1", "E2", "E3", "E4-A", "E4-B", "E4-C", "E4-D"])
    parser.add_argument("--variant", default="S0", choices=["S0", "S1", "S2"])
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("experiments/rb_b/results.jsonl"))
    parser.add_argument("--formal-e1", action="store_true", help="execute the controlled E1 dataset: 20 runs for S0, S1 and S2")
    parser.add_argument("--formal-e2", action="store_true", help="execute the controlled E2 paired dataset: 20 normal/perturbed pairs for S0, S1 and S2")
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/rb_b/formal-e1"))
    parser.add_argument("--e2-output-dir", type=Path, default=Path("experiments/rb_b/formal-e2"))
    args = parser.parse_args()

    if args.formal_e1 and args.formal_e2:
        raise ValueError("formal E1 and formal E2 are mutually exclusive")
    if args.formal_e1:
        run_formal_e1(args.output_dir, FORMAL_RUNS)
        return
    if args.formal_e2:
        run_formal_e2(args.e2_output_dir, FORMAL_RUNS)
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as fh:
        for i in range(args.runs):
            record = run_one(args.experiment, args.variant, i % len(SCENARIOS), i)
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            print(json.dumps({"run_id": record["run_id"], "outcome": record["final_outcome"],
                              "verification": record["verification"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
