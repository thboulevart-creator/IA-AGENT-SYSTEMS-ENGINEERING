from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping


FINGERPRINT_ALGORITHM = "sha256"
FINGERPRINT_SCHEMA_VERSION = "q-llm-01-config-v1"


@dataclass(frozen=True)
class RuntimeConfiguration:
    """Immutable configuration that must match across a normal/perturbed pair."""

    provider: str
    api: str
    requested_model: str
    timeout_seconds: int
    store: bool
    max_output_tokens: int
    structured_output_name: str
    structured_output_strict: bool
    structured_output_schema: Mapping[str, Any]
    client_revision: str


@dataclass(frozen=True)
class ExperimentConfiguration:
    """Experiment identity excluding condition-specific observations/mutations."""

    runtime: RuntimeConfiguration
    protocol_hash: str
    scenario_id: str
    seed: int
    initial_state: Mapping[str, Any]
    budget: Mapping[str, Any]
    tools: tuple[str, ...]
    permissions: Mapping[str, Any]


def canonical_json(value: Any) -> str:
    """Return one canonical JSON representation for hashing and comparison."""

    normalized = _normalize(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def fingerprint_configuration(config: ExperimentConfiguration) -> str:
    payload = {
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "algorithm": FINGERPRINT_ALGORITHM,
        "configuration": asdict(config),
    }
    return sha256_hex(payload)


def configuration_record(config: ExperimentConfiguration) -> dict[str, Any]:
    """Return auditable identity material without secrets or condition-specific state."""

    payload = asdict(config)
    return {
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "configuration": payload,
        "configuration_fingerprint": fingerprint_configuration(config),
    }


def compare_configurations(
    left: ExperimentConfiguration,
    right: ExperimentConfiguration,
) -> tuple[bool, tuple[str, ...]]:
    """Compare immutable configuration and report canonical field paths that differ."""

    left_data = _normalize(asdict(left))
    right_data = _normalize(asdict(right))
    differences: list[str] = []
    _diff(left_data, right_data, "", differences)
    return not differences, tuple(differences)


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"unsupported value in canonical configuration: {type(value).__name__}")


def _diff(left: Any, right: Any, path: str, out: list[str]) -> None:
    if type(left) is not type(right):
        out.append(path or "$")
        return
    if isinstance(left, dict):
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}" if path else key
            if key not in left or key not in right:
                out.append(child)
            else:
                _diff(left[key], right[key], child, out)
        return
    if isinstance(left, list):
        if len(left) != len(right):
            out.append(path or "$")
        for index, (l_item, r_item) in enumerate(zip(left, right)):
            _diff(l_item, r_item, f"{path}[{index}]", out)
        return
    if left != right:
        out.append(path or "$")
