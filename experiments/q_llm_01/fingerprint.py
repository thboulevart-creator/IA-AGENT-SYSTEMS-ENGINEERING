from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Iterator


FINGERPRINT_ALGORITHM = "sha256"
FINGERPRINT_SCHEMA_VERSION = "q-llm-01-config-v1"


class FrozenMap(Mapping[str, Any]):
    """Recursively immutable mapping used to prevent post-fingerprint mutation."""

    __slots__ = ("_data",)

    def __init__(self, value: Mapping[str, Any]) -> None:
        if any(not isinstance(key, str) for key in value):
            raise TypeError("configuration mapping keys must be strings")
        self._data = {key: _freeze(item) for key, item in value.items()}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


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

    def __post_init__(self) -> None:
        object.__setattr__(self, "structured_output_schema", FrozenMap(self.structured_output_schema))


@dataclass(frozen=True)
class ExperimentConfiguration:
    """Experiment identity excluding condition-specific observations/mutations."""

    runtime: RuntimeConfiguration
    protocol_hash: str
    prompt_template_hash: str
    scenario_id: str
    seed: int
    initial_state: Mapping[str, Any]
    budget: Mapping[str, Any]
    tools: tuple[str, ...]
    permissions: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "initial_state", FrozenMap(self.initial_state))
        object.__setattr__(self, "budget", FrozenMap(self.budget))
        object.__setattr__(self, "permissions", FrozenMap(self.permissions))
        object.__setattr__(self, "tools", tuple(self.tools))
        for name in ("protocol_hash", "prompt_template_hash", "scenario_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if not self.runtime.client_revision or self.runtime.client_revision == "UNPINNED":
            raise ValueError("client_revision must be pinned to a concrete revision")


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


def sha256_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("sha256_text expects a string")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint_configuration(config: ExperimentConfiguration) -> str:
    payload = {
        "fingerprint_schema_version": FINGERPRINT_SCHEMA_VERSION,
        "algorithm": FINGERPRINT_ALGORITHM,
        "configuration": _configuration_payload(config),
    }
    return sha256_hex(payload)


def configuration_record(config: ExperimentConfiguration) -> dict[str, Any]:
    """Return auditable identity material without secrets or condition-specific state."""

    payload = _configuration_payload(config)
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

    left_data = _normalize(_configuration_payload(left))
    right_data = _normalize(_configuration_payload(right))
    differences: list[str] = []
    _diff(left_data, right_data, "", differences)
    return not differences, tuple(differences)


def _configuration_payload(config: ExperimentConfiguration) -> dict[str, Any]:
    return {
        "runtime": {
            "provider": config.runtime.provider,
            "api": config.runtime.api,
            "requested_model": config.runtime.requested_model,
            "timeout_seconds": config.runtime.timeout_seconds,
            "store": config.runtime.store,
            "max_output_tokens": config.runtime.max_output_tokens,
            "structured_output_name": config.runtime.structured_output_name,
            "structured_output_strict": config.runtime.structured_output_strict,
            "structured_output_schema": config.runtime.structured_output_schema,
            "client_revision": config.runtime.client_revision,
        },
        "protocol_hash": config.protocol_hash,
        "prompt_template_hash": config.prompt_template_hash,
        "scenario_id": config.scenario_id,
        "seed": config.seed,
        "initial_state": config.initial_state,
        "budget": config.budget,
        "tools": config.tools,
        "permissions": config.permissions,
    }


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return FrozenMap(value)
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported value in immutable configuration: {type(value).__name__}")


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
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
