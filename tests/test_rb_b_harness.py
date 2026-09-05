from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.rb_b.observer import ExternalObserver, snapshot_workspace
from experiments.rb_b.oracle import canonical_transform, verify_o1
from experiments.rb_b.runner import Runner
from experiments.rb_b.systems import ScriptedDecisionProvider
from experiments.rb_b.tools import FaultPlan, ToolResult, WorkspaceTools
from experiments.rb_b.trace import Trace


class RBBHarnessTests(unittest.TestCase):
    def workspace(self, source: str = "  MiXeD Éxample  ") -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)
        (path / "source.txt").write_text(source, encoding="utf-8")
        return path

    def run_variant(self, variant: str, experiment: str = "E1", hook=None, faults=None):
        ws = self.workspace()
        trace = Trace("test", experiment, variant, "test", 0)
        result = Runner(ScriptedDecisionProvider()).run(
            variant, ws, WorkspaceTools(ws, faults), trace, hook
        )
        return result, trace

    def test_oracle_is_byte_exact_and_independent(self):
        ws = self.workspace()
        (ws / "artifact.txt").write_bytes(canonical_transform((ws / "source.txt").read_bytes()))
        self.assertEqual(verify_o1(ws).status, "PASS")
        (ws / "artifact.txt").write_bytes(b"claimed success")
        self.assertEqual(verify_o1(ws).status, "FAIL")

    def test_missing_artifact_is_objective_failure_not_blocked(self):
        ws = self.workspace()
        self.assertEqual(verify_o1(ws).status, "FAIL")

    def test_observer_inspects_external_state_not_tool_claim(self):
        ws = self.workspace()
        result = ToolResult("SUCCESS", {"written": True})
        observation = ExternalObserver().observe(ws, "WRITE_ARTIFACT", result)
        self.assertFalse(observation.artifact_exists)
        self.assertIsNone(observation.artifact_hash)
        self.assertEqual(observation.tool_status, "SUCCESS")
        self.assertEqual(observation.tool_claim["written"], True)

    def test_e1_all_variants_pass(self):
        for variant in ("S0", "S1", "S2"):
            result, _ = self.run_variant(variant)
            self.assertEqual(result["final_outcome"], "PASS", variant)
            self.assertEqual(result["verification"]["status"], "PASS")

    def test_e2_mutation_occurs_before_observation_and_s2_repairs(self):
        def corrupt(action, ws):
            if action == "WRITE_ARTIFACT":
                p = ws / "artifact.txt"
                p.write_bytes(p.read_bytes()[:-1] + b"X")
                return {"target": "artifact.txt", "mutation": "test_corruption"}
            return {}

        s2, trace = self.run_variant("S2", "E2", corrupt)
        self.assertEqual(s2["final_outcome"], "PASS")
        kinds = [e["kind"] for e in trace.events]
        mutation_i = kinds.index("external_mutation")
        observation_i = kinds.index("observation")
        decision_i = next(i for i, e in enumerate(trace.events) if e["kind"] == "decision" and e.get("action") == "CHECK_ARTIFACT")
        self.assertLess(mutation_i, observation_i)
        self.assertLess(observation_i, decision_i)
        self.assertTrue(any(e["kind"] == "decision" and e.get("action") == "REPAIR_ARTIFACT" for e in trace.events))

    def test_e2_control_provider_is_experiment_agnostic(self):
        provider = ScriptedDecisionProvider()
        first = provider.decide("objective", {"action": "CHECK_ARTIFACT", "tool_status": "PASS"}, [])
        second = provider.decide("objective", {"action": "CHECK_ARTIFACT", "tool_status": "FAIL"}, [])
        self.assertIsNone(first.action)
        self.assertEqual(second.action, "REPAIR_ARTIFACT")

    def test_e3_tool_success_can_disagree_with_oracle(self):
        faults = FaultPlan(false_success={"WRITE_ARTIFACT"})
        result, trace = self.run_variant("S0", "E3", faults=faults)
        writes = [e for e in trace.events if e["kind"] == "tool_execution" and e["action"] == "WRITE_ARTIFACT"]
        self.assertEqual(writes[-1]["status"], "SUCCESS")
        self.assertEqual(result["verification"]["status"], "FAIL")

    def test_e4_failure_is_controlled_and_not_followed_by_check(self):
        faults = FaultPlan(execution_error={"WRITE_ARTIFACT"})
        result, trace = self.run_variant("S0", "E4-D", faults=faults)
        errors = [e for e in trace.events if e["kind"] == "tool_execution" and e["status"] == "ERROR"]
        self.assertEqual(errors[-1]["error_type"], "EXECUTION_ERROR")
        actions = [e["action"] for e in trace.events if e["kind"] == "tool_execution"]
        self.assertEqual(actions, ["READ_SOURCE", "WRITE_ARTIFACT"])
        self.assertEqual(result["verification"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
