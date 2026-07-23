"""Canonical SAL verification-status policy.

The JSON Schema is the single status-vocabulary authority. Runtime consumers
load it instead of maintaining independent string sets that drift from stored
facts and from one another.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "sal-facts" / "sal-facts-schema.json"

PROMOTING = "PROMOTING"
CONDITIONAL = "CONDITIONAL"
NON_PROMOTING = "NON_PROMOTING"
_PROMOTION_CLASSES = frozenset({PROMOTING, CONDITIONAL, NON_PROMOTING})


@dataclass(frozen=True)
class VerificationStatusRule:
    status: str
    promotion_class: str
    meaning: str


def load_status_policy(
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, VerificationStatusRule]:
    schema: dict[str, Any] = json.loads(schema_path.read_text(encoding="utf-8"))
    definition = schema.get("$defs", {}).get("verification_status", {})
    statuses = definition.get("enum", [])
    raw_policy = definition.get("x-status-policy", {})
    if not isinstance(statuses, list) or not statuses:
        raise ValueError("SAL verification-status enum is missing or empty")
    if len(statuses) != len(set(statuses)):
        raise ValueError("SAL verification-status enum contains duplicates")
    if set(statuses) != set(raw_policy):
        raise ValueError(
            "SAL verification-status policy keys must exactly match the enum"
        )

    policy: dict[str, VerificationStatusRule] = {}
    for status in statuses:
        record = raw_policy[status]
        promotion_class = str(record.get("promotion_class", ""))
        meaning = str(record.get("meaning", "")).strip()
        if promotion_class not in _PROMOTION_CLASSES:
            raise ValueError(
                f"invalid promotion class for verification status {status!r}"
            )
        if not meaning:
            raise ValueError(f"missing meaning for verification status {status!r}")
        policy[status] = VerificationStatusRule(
            status=status,
            promotion_class=promotion_class,
            meaning=meaning,
        )
    return policy


def status_rule(
    status: str, schema_path: Path = DEFAULT_SCHEMA_PATH
) -> VerificationStatusRule:
    policy = load_status_policy(schema_path)
    try:
        return policy[status]
    except KeyError as error:
        raise ValueError(f"unknown SAL verification status: {status!r}") from error


def is_automatically_promoting(
    status: str, schema_path: Path = DEFAULT_SCHEMA_PATH
) -> bool:
    return status_rule(status, schema_path).promotion_class == PROMOTING
