from __future__ import annotations

import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any

from .harness import SCENARIOS, VARIANTS
from .systems import ScriptedDecisionProvider


def _events(record: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [event for event in record.get("events", []) if event.get("kind") == kind]


def _first_observation(record: dict[str, Any], action: str) -> dict[str, Any] | None:
    matches = [event for event in _events(record, "observation") if event.get("action") == action]
    return matches[0] if matches else None


def _source_bytes(scenario_id: int) -> bytes:
    return SCENARIOS[int(scenario_id)].encode("utf-8")


def _independent_transform(source: bytes) -> bytes:
    return source.decode("utf-8").strip().lower().encode("utf-8")


def _expected_hash(scenario_id: int) -> str:
    return hashlib.sha256(_independent_transform(_source_bytes(scenario_id))).hexdigest()


def _action_sequence(record: dict[str, Any]) -> list[str]:
    return [event["action"] for event in _events(record, "action_proposed")]


def _first_action_divergence(normal: list[str], perturbed: list[str]) -> int | None:
    for index, (left, right) in enumerate(zip(normal, perturbed)):
        if left != right:
            return index
    if len(normal) != len(perturbed):
        return min(len(normal), len(perturbed))
    return None


def _provider_leakage_check() -> str | None:
    source = inspect.getsource(ScriptedDecisionProvider)
    forbidden = ("experiment_id", "mutation_hook", "perturb", "mutated")
    for token in forbidden:
        if token in source:
            return f"provider leakage token present: {token}"
    signature = inspect.signature(ScriptedDecisionProvider.decide)
    if tuple(signature.parameters) != ("self", "objective", "observation", "history"):
        return "provider decide interface exposes unexpected condition inputs"
    return None


def _final_state_artifact_hash(record: dict[str, Any]) -> str | None:
    state = record.get("final_state", {})
    return state.get("artifact.txt") if isinstance(state, dict) else None


def _audit_pair(normal: dict[str, Any], perturbed: dict[str, Any], variant: str) -> list[str]:
    failures: list[str] = []
    if normal.get("condition") != "normal" or perturbed.get("condition") != "perturbed":
        failures.append("pair mismatch")
    pair_fields = ("scenario_id", "random_seed", "objective_version", "initial_workspace_state")
    if any(normal.get(field) != perturbed.get(field) for field in pair_fields):
        failures.append("initial state mismatch")

    normal_write = _first_observation(normal, "WRITE_ARTIFACT")
    pert_write = _first_observation(perturbed, "WRITE_ARTIFACT")
    if not normal_write or not pert_write:
        failures.append("trace incomplete")
        return failures

    expected_hash = _expected_hash(int(normal["scenario_id"]))
    if normal_write.get("artifact_hash") != expected_hash:
        failures.append("pre-mutation objective not proven")
    if pert_write.get("artifact_hash") == expected_hash:
        failures.append("mutation ineffective")

    mutations = _events(perturbed, "external_mutation")
    if len(mutations) != 1:
        failures.append("mutation placement invalid")
    else:
        mutation_seq = mutations[0]["seq"]
        write_exec = [e for e in _events(perturbed, "tool_execution") if e.get("action") == "WRITE_ARTIFACT"]
        write_obs = [e for e in _events(perturbed, "observation") if e.get("action") == "WRITE_ARTIFACT"]
        if not write_exec or not write_obs or not (write_exec[0]["seq"] < mutation_seq < write_obs[0]["seq"]):
            failures.append("mutation placement invalid")

    normal_check = _first_observation(normal, "CHECK_ARTIFACT")
    pert_check = _first_observation(perturbed, "CHECK_ARTIFACT")
    if not normal_check or not pert_check:
        failures.append("trace incomplete")
    else:
        if normal_check.get("tool_status") != "PASS" or normal_check.get("artifact_hash") != expected_hash:
            failures.append("final oracle contradiction")
        if pert_check.get("tool_status") != "FAIL" or pert_check.get("artifact_hash") == expected_hash:
            failures.append("observation contradiction")

    normal_actions = _action_sequence(normal)
    pert_actions = _action_sequence(perturbed)
    divergence = _first_action_divergence(normal_actions, pert_actions)
    if variant == "S2":
        if divergence is None:
            failures.append("unexplained first divergence")
        else:
            if normal_actions[:divergence] != pert_actions[:divergence]:
                failures.append("unexplained first divergence")
            if divergence == 0 or normal_actions[divergence - 1] != "CHECK_ARTIFACT" or pert_actions[divergence] != "REPAIR_ARTIFACT":
                failures.append("unexplained first divergence")
            causal_decisions = [
                d for d in _events(perturbed, "decision")
                if d.get("observation", {}).get("action") == "CHECK_ARTIFACT"
            ]
            if not causal_decisions:
                failures.append("repair without causal observation")
            else:
                causal = causal_decisions[0]
                embedded = causal.get("observation", {})
                if embedded.get("tool_status") != pert_check.get("tool_status") or embedded.get("artifact_hash") != pert_check.get("artifact_hash"):
                    failures.append("observation contradiction")
                if embedded.get("tool_status") != "FAIL" or causal.get("action") != "REPAIR_ARTIFACT":
                    failures.append("repair without causal observation")
        if perturbed.get("verification", {}).get("status") != "PASS" or _final_state_artifact_hash(perturbed) != expected_hash:
            failures.append("final oracle contradiction")
    else:
        if divergence is not None:
            failures.append("unexplained first divergence")
        if perturbed.get("verification", {}).get("status") != "FAIL" or _final_state_artifact_hash(perturbed) == expected_hash:
            failures.append("final oracle contradiction")

    if normal.get("verification", {}).get("status") != "PASS" or _final_state_artifact_hash(normal) != expected_hash:
        failures.append("final oracle contradiction")
    return failures


def audit(output_dir: Path) -> dict[str, Any]:
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("paired_runs_per_variant") != 20:
        return {"status": "BLOCKED", "reason": "formal E2 sample size is not exactly 20 paired runs per variant"}
    leakage = _provider_leakage_check()
    if leakage:
        return {"status": "FAIL", "reason": leakage}

    summary: dict[str, Any] = {"status": "PASS", "experiment": "E2", "variants": {}}
    all_failures: list[dict[str, Any]] = []
    for variant in VARIANTS:
        path = output_dir / f"e2-{variant.lower()}.jsonl"
        if not path.exists():
            all_failures.append({"variant": variant, "reason": "missing formal dataset"})
            continue
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(records) != 40:
            all_failures.append({"variant": variant, "reason": "wrong record count"})
            continue
        normal = {(r["scenario_id"], r["random_seed"]): r for r in records if r.get("condition") == "normal"}
        perturbed = {(r["scenario_id"], r["random_seed"]): r for r in records if r.get("condition") == "perturbed"}
        if set(normal) != set(perturbed) or len(normal) != 20:
            all_failures.append({"variant": variant, "reason": "pair mismatch"})
            continue
        failures = []
        for key in sorted(normal):
            pair_failures = _audit_pair(normal[key], perturbed[key], variant)
            if pair_failures:
                failures.append({"pair": {"scenario_id": key[0], "seed": key[1]}, "failures": pair_failures})
        summary["variants"][variant] = {
            "pairs": 20,
            "normal_pass": sum(r.get("verification", {}).get("status") == "PASS" for r in normal.values()),
            "perturbed_pass": sum(r.get("verification", {}).get("status") == "PASS" for r in perturbed.values()),
            "pair_failures": len(failures),
            "failures": failures,
        }
        if failures:
            all_failures.extend({"variant": variant, **item} for item in failures)

    if all_failures:
        summary["status"] = "FAIL"
        summary["failures"] = all_failures
    return summary


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m experiments.rb_b.audit_formal_e2 OUTPUT_DIR")
    result = audit(Path(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
