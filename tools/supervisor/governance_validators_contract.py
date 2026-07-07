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
})


def validator(
    rule_id: str,
    domain: str,
    description: str = "",
    skill_ids: "list[str] | None" = None,
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

    Returns:
        The original function unchanged (decorator is metadata-only).

    Example:
        @validator(rule_id="V001", domain="structural", skill_ids=["add-python-api"])
        def validate_source_architecture(context):
            ...
    """
    def decorator(fn: Callable) -> Callable:
        _VALIDATOR_REGISTRY.append({
            "rule_id": rule_id,
            "domain": domain,
            "description": description,
            "skill_ids": skill_ids or [],
            "fn": fn,
        })
        return fn
    return decorator
