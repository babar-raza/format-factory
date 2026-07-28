"""governance_validators_contract.py — @validator decorator and ValidationResult contract.

Provides machine-readable domain classification metadata for all governance validator
functions. Adding @validator to a function registers it in _VALIDATOR_REGISTRY; the
runner uses this registry as an additive source alongside existing glob-based loading.

Usage:
  from tools.supervisor.governance_validators_contract import validator, ValidationResult

  @validator(rule_id="V001", domain="structural", description="Check file size limits")
  def validate_source_architecture(context):
      ...

Registry access:
  from tools.supervisor.governance_validators_contract import _VALIDATOR_REGISTRY
  # Each entry: {"rule_id": str, "domain": str, "description": str, "fn": Callable}
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Callable, List, Optional


class ValidatorVerdict(enum.Enum):
    GOV_BLOCK = "GOV_BLOCK"
    WARNING = "WARNING"
    PASS = "PASS"


@dataclass
class ValidationResult:
    """Result returned by a governance validator function."""
    verdict: ValidatorVerdict
    rule_id: str
    message: str
    detail: Optional[str] = field(default=None)


# Module-level registry — populated by @validator decorator at import time.
# Each entry: {"rule_id": str, "domain": str, "description": str, "fn": Callable}
_VALIDATOR_REGISTRY: List[dict] = []

# Valid domain values for @validator(domain=...)
VALID_DOMAINS = frozenset({
    "structural",
    "import_direction",
    "naming",
    "evidence",
    "governance",
    "dotnet",
    "consumer_proof",
    "gate_auth",
    "layers",
    "ledger",
    "oracle",
    "output_quality",
    "path",
    "sal",
    "signal",
    "spec",
    "root_struct",
    "found_issue",
    "general",
    "control_layer",
    "format_contract",
})


VALID_DISPATCH = frozenset({"explicit", "deferred", "superseded"})


def validator(
    rule_id: str,
    domain: str,
    description: str = "",
    skill_ids: "list[str] | None" = None,
    dispatch: str = "explicit",
    deferred_reason: "str | None" = None,
) -> Callable[[Callable], Callable]:
    """Decorator that registers a governance validator in _VALIDATOR_REGISTRY.

    Args:
        rule_id: Canonical rule identifier (e.g. "V001"). Must be unique per function.
        domain: Domain classification for the validator (see VALID_DOMAINS).
        description: Human-readable description of what this validator checks.
        skill_ids: Optional list of skill IDs (from .supervisor/skill-registry.yaml) that
            must mention this validator in their command files. Used by
            validate_skill_contracts.py to detect stale skill documentation.
            Example: ["add-python-api", "add-dotnet-api"]
        dispatch: Dispatch status — "explicit" (has a call site in the runner),
            "deferred" (intentionally not wired, needs future work), or
            "superseded" (replaced by another validator, kept for reference).
            Non-"explicit" values require deferred_reason.
        deferred_reason: Required when dispatch is not "explicit". Explains why
            this validator is not wired into the sprint governance runner.

    Returns:
        The original function unchanged (decorator is metadata-only).

    Example:
        @validator(rule_id="V001", domain="structural", skill_ids=["add-python-api"])
        def validate_source_architecture(context):
            ...
    """
    if dispatch not in VALID_DISPATCH:
        raise ValueError(f"dispatch must be one of {VALID_DISPATCH}, got {dispatch!r}")
    if dispatch != "explicit" and not deferred_reason:
        raise ValueError(f"dispatch={dispatch!r} requires deferred_reason")
    def decorator(fn: Callable) -> Callable:
        _VALIDATOR_REGISTRY.append({
            "rule_id": rule_id,
            "domain": domain,
            "description": description,
            "skill_ids": skill_ids or [],
            "dispatch": dispatch,
            "deferred_reason": deferred_reason,
            "fn": fn,
        })
        return fn
    return decorator
