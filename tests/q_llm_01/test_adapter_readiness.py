from __future__ import annotations

import unittest

from experiments.q_llm_01.adapter import LLMDecisionProvider, LLMRequest, LLMResponse
from experiments.rb_b.tools import TOOLS


class RecordingClient:
    def __init__(self, action: str | None = "READ_SOURCE") -> None:
        self.action = action
        self.requests: list[LLMRequest] = []

    def infer(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(
            raw={"provider": "test", "action": self.action},
            action=self.action,
            metadata={"test": True},
        )


class AdapterReadinessTests(unittest.TestCase):
    def make_provider(self, client: RecordingClient) -> LLMDecisionProvider:
        return LLMDecisionProvider(
            client,
            "Follow the objective using only declared observations.",
            TOOLS,
        )

    def test_adapter_shape_and_raw_exchange(self) -> None:
        client = RecordingClient("READ_SOURCE")
        provider = self.make_provider(client)
        decision = provider.decide("objective", {"action": None, "tool_status": None}, [])
        self.assertEqual(decision.action, "READ_SOURCE")
        self.assertIsNotNone(provider.last_exchange)
        self.assertEqual(provider.last_exchange["raw_response"]["provider"], "test")
        self.assertEqual(len(client.requests), 1)

    def test_model_input_excludes_harness_metadata(self) -> None:
        client = RecordingClient()
        provider = self.make_provider(client)
        provider.decide(
            "objective",
            {"action": "CHECK_ARTIFACT", "tool_status": "FAIL", "external_state": {"artifact": "bad"}},
            [{"action": "WRITE_ARTIFACT", "tool_status": "SUCCESS"}],
        )
        serialized = repr(client.requests[0])
        for forbidden in (
            "experiment_id",
            "mutation_id",
            "mutation_hook",
            "expected_repair_action",
            "post_perturbation_ground_truth",
            "harness_state",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_information_barrier_rejects_forbidden_observation_key(self) -> None:
        client = RecordingClient()
        provider = self.make_provider(client)
        with self.assertRaisesRegex(ValueError, "information barrier violation"):
            provider.decide("objective", {"action": "CHECK_ARTIFACT", "perturbed": True}, [])
        self.assertEqual(client.requests, [])

    def test_information_barrier_rejects_nested_history_key(self) -> None:
        client = RecordingClient()
        provider = self.make_provider(client)
        with self.assertRaisesRegex(ValueError, "information barrier violation"):
            provider.decide(
                "objective",
                {"action": "CHECK_ARTIFACT"},
                [{"external_state": {"harness_state": "secret"}}],
            )
        self.assertEqual(client.requests, [])

    def test_unauthorized_model_action_is_rejected(self) -> None:
        client = RecordingClient("NOT_A_TOOL")
        provider = self.make_provider(client)
        with self.assertRaisesRegex(ValueError, "unauthorized action"):
            provider.decide("objective", {"action": None}, [])

    def test_one_shot_planning_is_not_an_implicit_adaptation_path(self) -> None:
        client = RecordingClient()
        provider = self.make_provider(client)
        with self.assertRaisesRegex(RuntimeError, "one-shot planning"):
            provider.plan("objective", TOOLS)
        self.assertEqual(client.requests, [])


if __name__ == "__main__":
    unittest.main()
