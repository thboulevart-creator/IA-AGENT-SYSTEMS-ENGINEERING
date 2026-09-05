from __future__ import annotations

import unittest

from experiments.q_llm_01.fingerprint import (
    ExperimentConfiguration,
    RuntimeConfiguration,
    canonical_json,
    compare_configurations,
    configuration_record,
    fingerprint_configuration,
)


SCHEMA = {
    "type": "object",
    "properties": {"action": {"type": "string", "enum": ["CHECK_ARTIFACT", "TERMINATE"]}},
    "required": ["action"],
    "additionalProperties": False,
}


def make_config() -> ExperimentConfiguration:
    return ExperimentConfiguration(
        runtime=RuntimeConfiguration(
            provider="openai",
            api="https://api.openai.com/v1/responses",
            requested_model="gpt-5.6-luna",
            timeout_seconds=60,
            store=False,
            max_output_tokens=64,
            structured_output_name="rb_b_action",
            structured_output_strict=True,
            structured_output_schema=SCHEMA,
            client_revision="commit-abc",
        ),
        protocol_hash="protocol-sha256-abc",
        scenario_id="S0-001",
        seed=17,
        initial_state={"artifact": "valid", "counter": 0},
        budget={"max_calls": 1, "max_tokens": 64},
        tools=("CHECK_ARTIFACT",),
        permissions={"network": False, "filesystem": False},
    )


class FingerprintContractTests(unittest.TestCase):
    def test_key_order_does_not_change_canonical_hash(self) -> None:
        self.assertEqual(
            canonical_json({"b": 2, "a": {"d": 4, "c": 3}}),
            canonical_json({"a": {"c": 3, "d": 4}, "b": 2}),
        )

    def test_same_configuration_has_same_fingerprint(self) -> None:
        self.assertEqual(fingerprint_configuration(make_config()), fingerprint_configuration(make_config()))

    def test_normal_and_perturbed_pair_share_immutable_configuration(self) -> None:
        left = make_config()
        right = make_config()
        same, differences = compare_configurations(left, right)
        self.assertTrue(same)
        self.assertEqual(differences, ())

    def test_authorized_difference_is_detected(self) -> None:
        left = make_config()
        right = make_config()
        right = ExperimentConfiguration(
            **{**right.__dict__, "seed": 18}
        )
        same, differences = compare_configurations(left, right)
        self.assertFalse(same)
        self.assertEqual(differences, ("seed",))

    def test_record_contains_fingerprint_but_no_api_secret(self) -> None:
        record = configuration_record(make_config())
        self.assertIn("configuration_fingerprint", record)
        self.assertNotIn("api_key", record)
        self.assertNotIn("OPENAI_API_KEY", str(record))


if __name__ == "__main__":
    unittest.main()
