from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

OBJECTIVE_VERSION = "O1-v1"


def canonical_transform(data: bytes) -> bytes:
    return data.decode("utf-8").strip().lower().encode("utf-8")


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class OracleResult:
    status: str  # PASS | FAIL | BLOCKED
    expected_hash: str | None
    actual_hash: str | None
    reason: str


def verify_o1(workspace: Path) -> OracleResult:
    source = workspace / "source.txt"
    artifact = workspace / "artifact.txt"
    if not source.exists():
        return OracleResult("BLOCKED", None, sha256_file(artifact), "source.txt unavailable to oracle")
    if not artifact.exists():
        return OracleResult("FAIL", None, None, "artifact.txt missing")
    try:
        expected = canonical_transform(source.read_bytes())
        actual = artifact.read_bytes()
    except (OSError, UnicodeDecodeError) as exc:
        return OracleResult("BLOCKED", None, sha256_file(artifact), f"oracle inspection error: {exc}")
    return OracleResult(
        "PASS" if actual == expected else "FAIL",
        hashlib.sha256(expected).hexdigest(),
        hashlib.sha256(actual).hexdigest(),
        "byte-for-byte match" if actual == expected else "artifact mismatch",
    )
