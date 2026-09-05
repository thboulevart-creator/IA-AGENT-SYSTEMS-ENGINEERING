from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

VARIANTS = ("S0", "S1", "S2")
EXPECTED_ACTIONS = ["READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT"]


def audit_file(path: Path, variant: str) -> list[str]:
    errors: list[str] = []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 20:
        errors.append(f"{variant}: expected 20 records, got {len(rows)}")
    if len({r.get('run_id') for r in rows}) != len(rows):
        errors.append(f"{variant}: duplicate run_id")
    scenarios = Counter(str(r.get("scenario_id")) for r in rows)
    if scenarios != Counter({str(i): 4 for i in range(5)}):
        errors.append(f"{variant}: scenario distribution {dict(scenarios)}")
    seeds = [r.get("random_seed") for r in rows]
    if seeds != list(range(20)):
        errors.append(f"{variant}: seed schedule {seeds}")
    for index, record in enumerate(rows):
        prefix = f"{variant}[{index}]"
        if record.get("experiment_id") != "E1":
            errors.append(f"{prefix}: wrong experiment_id")
        if record.get("system_variant") != variant:
            errors.append(f"{prefix}: wrong system_variant")
        if record.get("final_outcome") != "PASS":
            errors.append(f"{prefix}: final_outcome={record.get('final_outcome')}")
        if record.get("verification", {}).get("status") != "PASS":
            errors.append(f"{prefix}: verification={record.get('verification', {}).get('status')}")
        if record.get("termination_reason") not in {"fixed_or_one_shot_complete", "adaptive_termination"}:
            errors.append(f"{prefix}: termination={record.get('termination_reason')}")
        events = record.get("events", [])
        kinds = [e.get("kind") for e in events]
        executed = [e.get("action") for e in events if e.get("kind") == "tool_execution" and e.get("status") in {"SUCCESS", "PASS"}]
        if executed != EXPECTED_ACTIONS:
            errors.append(f"{prefix}: executed actions={executed}")
        if any(e.get("kind") == "external_mutation" for e in events):
            errors.append(f"{prefix}: unexpected external mutation")
        if any(e.get("action") == "REPAIR_ARTIFACT" for e in events):
            errors.append(f"{prefix}: unexpected repair action")
        observation_indices = [i for i, k in enumerate(kinds) if k == "observation"]
        execution_indices = [i for i, k in enumerate(kinds) if k == "tool_execution"]
        if len(execution_indices) != 3 or len(observation_indices) != 3:
            errors.append(f"{prefix}: execution/observation counts invalid")
        elif any(obs <= exe for exe, obs in zip(execution_indices, observation_indices)):
            errors.append(f"{prefix}: observation does not follow execution")
        if not record.get("final_state", {}).get("artifact.txt"):
            errors.append(f"{prefix}: final artifact absent from state snapshot")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the formal E1 dataset and behavioral traces")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.output_dir / "manifest.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest != {
        "experiment": "E1",
        "objective_version": manifest.get("objective_version"),
        "runs_per_variant": 20,
        "variants": ["S0", "S1", "S2"],
        "scenario_count": 5,
        "schedule": "scenario_id = run_index mod 5; seed = run_index",
    }:
        errors.append("manifest structure/count mismatch")
    for variant in VARIANTS:
        errors.extend(audit_file(args.output_dir / f"e1-{variant.lower()}.jsonl", variant))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("PASS: formal E1 dataset = 20 runs x S0/S1/S2; trace audit clean")


if __name__ == "__main__":
    main()
