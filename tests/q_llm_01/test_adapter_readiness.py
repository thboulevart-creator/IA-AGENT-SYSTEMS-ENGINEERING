from __future__ import annotations

import pytest

from experiments.q_llm_01.adapter import LLMDecisionProvider, LLMRequest, LLMResponse
from experiments.rb_b.tools import TOOLS


class RecordingClient:
    def __init__(self, action: str | None = "READ_SOURCE") -> None:
        self.action = action
        self.requests: list[LLMRequest] = []

    def infer(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(raw={"provider": "test", "action": self.action}, action=self.action, metadata={"test": True})


def make_provider(client: RecordingClient) -> LLMDecisionProvider:
    return LLMDecisionProvider(client, "Follow the objective using only declared observations.", TOOLS)


def test_adapter_conforms_to_decision_provider_shape_and_preserves_raw_exchange() -> None:
    client = RecordingClient("READ_SOURCE")
    provider = make_provider(client)

    decision = provider.decide("objective", {"action": None, "tool_status": None}, [])

    assert decision.action == "READ_SOURCE"
    assert provider.last_exchange is not None
    assert provider.last_exchange["raw_response"]["provider"] == "test"
    assert len(client.requests) == 1


def test_model_input_excludes_harness_metadata() -> None:
    client = RecordingClient()
    provider = make_provider(client)

    provider.decide(
        "objective",
        {"action": "CHECK_ARTIFACT", "tool_status": "FAIL", "external_state": {"artifact": "bad"}},
        [{"action": "WRITE_ARTIFACT", "tool_status": "SUCCESS"}],
    )

    request = client.requests[0]
    serialized = repr(request)
    for forbidden in (
        "experiment_id",
        "mutation_id",
        "mutation_hook",
        "expected_repair_action",
        "post_perturbation_ground_truth",
        "harness_state",
    ):
        assert forbidden not in serialized


def test_information_barrier_rejects_forbidden_observation_key() -> None:
    client = RecordingClient()
    provider = make_provider(client)

    with pytest.raises(ValueError, match="information barrier violation"):
        provider.decide("objective", {"action": "CHECK_ARTIFACT", "perturbed": True}, [])

    assert client.requests == []


def test_information_barrier_rejects_nested_forbidden_history_key() -> None:
    client = RecordingClient()
    provider = make_provider(client)

    with pytest.raises(ValueError, match="information barrier violation"):
        provider.decide(
            "objective",
            {"action": "CHECK_ARTIFACT"},
            [{"external_state": {"harness_state": "secret"}}],
        )

    assert client.requests == []


def test_unauthorized_model_action_is_rejected() -> None:
    client = RecordingClient("NOT_A_TOOL")
    provider = make_provider(client)

    with pytest.raises(ValueError, match="unauthorized action"):
        provider.decide("objective", {"action": None}, [])


def test_one_shot_planning_is_not_an_implicit_llm_adaptation_path() -> None:
    client = RecordingClient()
    provider = make_provider(client)

    with pytest.raises(RuntimeError, match="one-shot planning"):
        provider.plan("objective", TOOLS)

    assert client.requests == []
