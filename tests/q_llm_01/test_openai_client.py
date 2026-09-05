from __future__ import annotations

import json
import unittest

from experiments.q_llm_01.openai_client import _extract_action, _render_user_input
from experiments.q_llm_01.adapter import LLMRequest


class OpenAIClientContractTests(unittest.TestCase):
    def test_extracts_structured_action(self) -> None:
        body = {
            "id": "resp_test",
            "model": "gpt-5.6-luna",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"action":"CHECK_ARTIFACT"}',
                        }
                    ],
                }
            ],
        }
        self.assertEqual(_extract_action(body), "CHECK_ARTIFACT")

    def test_terminate_maps_to_none(self) -> None:
        body = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": '{"action":"TERMINATE"}'},
                    ],
                }
            ]
        }
        self.assertIsNone(_extract_action(body))

    def test_model_input_is_deterministic_and_declared_only(self) -> None:
        request = LLMRequest(
            system_instructions="Use only declared observations.",
            objective="objective",
            tools=("READ_SOURCE", "WRITE_ARTIFACT", "CHECK_ARTIFACT"),
            observation={"action": "CHECK_ARTIFACT", "external_state": {"artifact": "bad"}},
            history=({"action": "WRITE_ARTIFACT", "tool_status": "SUCCESS"},),
        )
        rendered = _render_user_input(request)
        parsed = json.loads(rendered)
        self.assertEqual(parsed["objective"], "objective")
        self.assertEqual(parsed["available_actions"], list(request.tools))
        self.assertNotIn("experiment_id", rendered)
        self.assertNotIn("mutation_id", rendered)
        self.assertNotIn("expected_repair_action", rendered)
        self.assertNotIn("post_perturbation_ground_truth", rendered)
        self.assertNotIn("harness_state", rendered)

    def test_missing_action_is_rejected(self) -> None:
        body = {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"wrong":"CHECK_ARTIFACT"}'}],
                }
            ]
        }
        with self.assertRaises(ValueError):
            _extract_action(body)


if __name__ == "__main__":
    unittest.main()
