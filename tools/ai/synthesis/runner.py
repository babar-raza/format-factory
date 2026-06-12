"""Synthesis task runner — controlled GPT-OSS synthesis with authority lifecycle.

All outputs start as ai_draft. Citations required for citation tasks.
Contradiction checking against verified-facts.yaml when available.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.ai.schemas.models import (
    AITaskContract,
    ArtifactAuthorityStateValue,
)


class SynthesisResult:
    """Result of a synthesis task execution."""

    def __init__(
        self,
        task_id: str,
        authority_state: ArtifactAuthorityStateValue = ArtifactAuthorityStateValue.ai_draft,
    ):
        self.task_id = task_id
        self.authority_state = authority_state
        self.raw_output: str = ""
        self.structured_output: dict[str, Any] = {}
        self.citations: list[dict[str, str]] = []
        self.citation_verified: bool = False
        self.contradiction_check_status: str = "not_checked"
        self.schema_valid: bool = False
        self.errors: list[str] = []
        self.output_hash: str = ""
        self.timestamp: str = datetime.now(timezone.utc).isoformat()

    @property
    def is_valid(self) -> bool:
        return self.schema_valid and len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "authority_state": self.authority_state.value,
            "raw_output": self.raw_output,
            "structured_output": self.structured_output,
            "citations": self.citations,
            "citation_verified": self.citation_verified,
            "contradiction_check_status": self.contradiction_check_status,
            "schema_valid": self.schema_valid,
            "errors": self.errors,
            "output_hash": self.output_hash,
            "timestamp": self.timestamp,
        }


def validate_task_contract(contract: AITaskContract) -> list[str]:
    """Validate a task contract before synthesis execution."""
    errors: list[str] = []
    if not contract.task_id:
        errors.append("task_id is required")
    if not contract.task_type:
        errors.append("task_type is required")
    if not contract.role:
        errors.append("role is required")
    return errors


def validate_structured_output(output: Any, schema: dict[str, Any] | None) -> tuple[bool, list[str]]:
    """Validate structured output against a schema definition."""
    if schema is None:
        return True, []
    errors: list[str] = []
    if not isinstance(output, dict):
        return False, ["output must be a JSON object"]
    required_fields = schema.get("required_fields", [])
    for field in required_fields:
        if field not in output:
            errors.append(f"missing required field: {field}")
    return len(errors) == 0, errors


def verify_citations(
    citations: list[dict[str, str]],
    source_snippets: dict[str, str] | None = None,
) -> tuple[bool, list[str]]:
    """Verify citations against local source snippets.

    Each citation must have 'source' and 'text' keys.
    If source_snippets is provided, verify each citation text appears in its source.
    """
    if not citations:
        return False, ["no citations provided"]
    errors: list[str] = []
    for i, cit in enumerate(citations):
        if "source" not in cit:
            errors.append(f"citation[{i}]: missing 'source'")
        if "text" not in cit:
            errors.append(f"citation[{i}]: missing 'text'")
        if source_snippets and cit.get("source") in source_snippets:
            if cit.get("text", "") not in source_snippets[cit["source"]]:
                errors.append(f"citation[{i}]: text not found in source '{cit['source']}'")
    return len(errors) == 0, errors


def check_contradictions(
    output: dict[str, Any],
    verified_facts_path: Path | None = None,
) -> str:
    """Check output for contradictions against verified facts.

    Returns status string.
    """
    if verified_facts_path is None or not verified_facts_path.exists():
        return "blocked_missing_verified_facts"

    try:
        import yaml
        with open(verified_facts_path) as f:
            facts = yaml.safe_load(f) or {}
    except Exception:
        return "blocked_invalid_verified_facts"

    fact_items = facts.get("facts", [])
    if not fact_items:
        return "blocked_empty_verified_facts"

    output_str = json.dumps(output, default=str).lower()
    contradictions: list[str] = []
    for fact in fact_items:
        assertion = fact.get("assertion", "").lower()
        negation = fact.get("negation", "").lower()
        if negation and negation in output_str:
            contradictions.append(f"contradiction with fact: {fact.get('id', 'unknown')}")

    if contradictions:
        return f"contradictions_found:{len(contradictions)}"
    return "no_contradictions"


def run_synthesis(
    contract: AITaskContract,
    raw_output: str,
    output_schema: dict[str, Any] | None = None,
    source_snippets: dict[str, str] | None = None,
    verified_facts_path: Path | None = None,
) -> SynthesisResult:
    """Run synthesis validation pipeline on raw LLM output.

    This does NOT call the LLM. It validates already-received output
    through the authority lifecycle pipeline.
    """
    result = SynthesisResult(task_id=contract.task_id)
    result.raw_output = raw_output
    result.output_hash = hashlib.sha256(raw_output.encode()).hexdigest()[:16]

    # Contract validation
    contract_errors = validate_task_contract(contract)
    if contract_errors:
        result.errors.extend(contract_errors)
        return result

    # Parse structured output
    try:
        result.structured_output = json.loads(raw_output)
    except (json.JSONDecodeError, TypeError):
        result.errors.append("malformed_json_output")
        return result

    # Schema validation
    valid, schema_errors = validate_structured_output(result.structured_output, output_schema)
    result.schema_valid = valid
    if schema_errors:
        result.errors.extend(schema_errors)
        return result

    # Citation verification (if required)
    if contract.require_citation:
        citations = result.structured_output.get("citations", [])
        result.citations = citations
        verified, cit_errors = verify_citations(citations, source_snippets)
        result.citation_verified = verified
        if cit_errors:
            result.errors.extend(cit_errors)

    # Contradiction check (if required)
    if contract.require_contradiction_check:
        result.contradiction_check_status = check_contradictions(
            result.structured_output, verified_facts_path
        )

    # Authority state: stays at ai_draft — never auto-escalated
    result.authority_state = ArtifactAuthorityStateValue.ai_draft

    return result
