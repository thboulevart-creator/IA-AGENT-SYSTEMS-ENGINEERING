from __future__ import annotations

import unittest

from experiments.q_llm_01.adapter import LLMRequest
from experiments.q_llm_01.openai_client import (
    MAX_OUTPUT_TOKENS,
    OpenAIResponsesClient,
    _assert_runtime_evidence,
    _extract_action,
)


REQUEST = LLMRequest(
    system_instructions="Use only declared observations.",
    objective="Choose the next action.",
    tools=("CHECK_ARTIFACT",),
    observation={"external_state": {"artifact": "bad"}},
    history=(),
)


def response(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "id": "resp_test",
        "model": "gpt-5.6-luna",
        "status": "completed",
        "store": False,
        "output": [
            {
                "type": "message",
                "content": [
                    {"type": "output_text", "text": '{"action":"CHECK_ARTIFACT"}'},
                ],
            }
        ],
    }
    body.update(overrides)
    return body


class OpenAIRuntimeContractTests(unittest.TestCase):
    def test_payload_is_strict_structured_output_and_store_false(self) -> None:
        client = object.__new__(OpenAIResponsesClient)
        client.model = "gpt-5.6-luna"
        client.timeout_seconds = 60
        payload = client._build_payload(REQUEST)
        self.assertEqual(payload["store"], False)
        self.assertEqual(payload["max_output_tokens"], MAX_OUTPUT_TOKENS)
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")

    def test_completed_response_is_accepted(self) -> None:
        _assert_runtime_evidence(response(), requested_model="gpt-5.6-luna")

    def test_missing_actual_model_is_rejected(self) -> None:
        body = response()
        del body["model"]
        with self.assertRaises(RuntimeError):
            _assert_runtime_evidence(body, requested_model="gpt-5.6-luna")

    def test_model_identity_mismatch_is_rejected(self) -> None:
        with self.assertRaises(RuntimeError):
            _assert_runtime_evidence(response(model="other-model"), requested_model="gpt-5.6-luna")

    def test_store_true_is_rejected(self) -> None:
        with self.assertRaises(RuntimeError):
            _assert_runtime_evidence(response(store=True), requested_model="gpt-5.6-luna")

    def test_incomplete_response_is_rejected(self) -> None:
        with self.assertRaises(RuntimeError):
            _assert_runtime_evidence(
                response(status="incomplete", incomplete_details={"reason": "max_output_tokens"}),
                requested_model="gpt-5.6-luna",
            )

    def test_refusal_is_not_converted_into_an_action(self) -> None:
        body = response(
            output=[
                {
                    "type": "message",
                    "content": [{"type": "refusal", "refusal": "refused"}],
                }
            ]
        )
        with self.assertRaises(RuntimeError):
            _extract_action(body)

    def test_malformed_structured_output_is_rejected(self) -> None:
        body = response(
            output=[
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"wrong":"x"}'}],
                }
            ]
        )
        with self.assertRaises(ValueError):
            _extract_action(body)


if __name__ == "__main__":
    unittest.main()
