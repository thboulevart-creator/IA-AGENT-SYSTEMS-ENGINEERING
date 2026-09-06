from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.rb_b.audit_formal_e2 import _audit_pair
from experiments.rb_b.harness import run_one


class E2FalsificationTests(unittest.TestCase):
    def _pair(self, variant: str = "S2") -> tuple[dict, dict]:
        normal = run_one("E2", variant, 0, 0, perturb=False)
        perturbed = run_one("E2", variant, 0, 0, perturb=True)
        return normal, perturbed

    def test_tampered_observation_cannot_pass(self) -> None:
        normal, perturbed = self._pair()
        for event in perturbed["events"]:
            if event.get("kind") == "decision" and event.get("observation", {}).get("action") == "CHECK_ARTIFACT":
                event["observation"]["tool_status"] = "PASS"
                break
        failures = _audit_pair(normal, perturbed, "S2")
        self.assertIn("observation contradiction", failures)
        self.assertIn("repair without causal observation", failures)

    def test_missing_mutation_cannot_pass(self) -> None:
        normal, perturbed = self._pair()
        perturbed["events"] = [e for e in perturbed["events"] if e.get("kind") != "external_mutation"]
        failures = _audit_pair(normal, perturbed, "S2")
        self.assertIn("mutation placement invalid", failures)

    def test_preplanned_repair_is_not_causal_adaptation(self) -> None:
        normal, perturbed = self._pair()
        # Force the normal trace to contain the same repair branch as the perturbed trace.
        perturbed_actions = [e for e in perturbed["events"] if e.get("kind") == "action_proposed"]
        for event in perturbed_actions:
            if event.get("action") == "REPAIR_ARTIFACT":
                normal["events"].insert(-1, dict(event))
                break
        failures = _audit_pair(normal, perturbed, "S2")
        self.assertIn("unexplained first divergence", failures)

    def test_unequal_pair_seed_is_rejected(self) -> None:
        normal, perturbed = self._pair()
        perturbed["random_seed"] = 999
        failures = _audit_pair(normal, perturbed, "S2")
        self.assertIn("initial state mismatch", failures)

    def test_tool_claim_alone_cannot_define_observation(self) -> None:
        normal, perturbed = self._pair()
        for event in perturbed["events"]:
            if event.get("kind") == "observation" and event.get("action") == "CHECK_ARTIFACT":
                event["tool_claim"] = {"match": True}
                break
        failures = _audit_pair(normal, perturbed, "S2")
        self.assertEqual([], [f for f in failures if f == "observation contradiction"])
        self.assertEqual([], [f for f in failures if f == "repair without causal observation"])


if __name__ == "__main__":
    unittest.main()
