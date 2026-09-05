from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


# Fields that are explicitly forbidden from crossing the model information barrier.
FORBIDDEN_INPUT_KEYS = frozenset(
    {
        "experiment_id",
        "mutation_id",
        "mutation_hook",
        "perturbation",
        "perturbed",
        "expected_repair_action",
        "post_perturbation_ground_truth",
        "harness_state",
    }
)


@dataclass(frozen=True)
class LLMRequest:
    """Complete model-visible request. Harness-only metadata is intentionally absent."""

    system_instructions: str
    objective: str
    tools: tuple[str, ...]
    observation: Mapping[str, Any]
    history: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class LLMResponse:
    """Raw inference output plus normalized action; both are retained for auditability."""

    raw: Any
    action: str | None
    metadata: Mapping[str, Any]


class InferenceClient(Protocol):
    """Vendor-neutral inference boundary. Implementations perform real model calls."""

    def infer(self, request: LLMRequest) -> LLMResponse: ...


class LLMDecisionProvider:
    """RB-B DecisionProvider adapter with a strict model information boundary."""

    def __init__(
        self,
        client: InferenceClient,
        system_instructions: str,
        allowed_actions: tuple[str, ...],
    ) -> None:
        self._client = client
        self._system_instructions = system_instructions
        self._allowed_actions = allowed_actions

    def plan(self, objective: str, tools: tuple[str, ...]) -> list[str]:
        raise RuntimeError("LLMDecisionProvider does not support one-shot planning; use S2 decide().")

    def decide(
        self,
        objective: str,
        observation: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        request = LLMRequest(
            system_instructions=self._system_instructions,
            objective=objective,
            tools=self._allowed_actions,
            observation=dict(observation),
            history=tuple(dict(item) for item in history),
        )
        _assert_information_barrier(request)
        response = self._client.infer(request)
        if response.action is not None and response.action not in self._allowed_actions:
            raise ValueError(f"model proposed unauthorized action: {response.action}")
        return {
            "action": response.action,
            "raw_response": response.raw,
            "inference_metadata": dict(response.metadata),
            "model_input": {
                "objective": request.objective,
                "tools": request.tools,
                "observation": dict(request.observation),
                "history": [dict(item) for item in request.history],
            },
        }


def _assert_information_barrier(request: LLMRequest) -> None:
    """Reject harness-only keys recursively before any inference call."""

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            leaked = FORBIDDEN_INPUT_KEYS.intersection(value.keys())
            if leaked:
                raise ValueError(f"information barrier violation: {sorted(leaked)}")
            for item in value.values():
                walk(item)
        elif isinstance(value, (tuple, list)):
            for item in value:
                walk(item)

    walk(request.observation)
    walk(request.history)
