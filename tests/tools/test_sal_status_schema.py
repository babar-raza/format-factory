"""Regression controls for the canonical SAL verification-status policy."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from tools.spec.sal_status import (
    CONDITIONAL,
    NON_PROMOTING,
    PROMOTING,
    is_automatically_promoting,
    load_status_policy,
    status_rule,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "sal-facts" / "sal-facts-schema.json"


def _combined_with_status(status: str) -> dict:
    return {
        "generated_at": "2026-07-23T00:00:00Z",
        "generator": "test",
        "formats_processed": 1,
        "spec_facts_total": 1,
        "workbench_verified_fact_total": 0,
        "results": [
            {
                "format_id": "test",
                "spec_facts": [
                    {
                        "qname": "FACT-TEST-001",
                        "claim": "A test fact with a governed status.",
                        "verification_status": status,
                    }
                ],
            }
        ],
    }


def test_status_policy_is_closed_and_semantically_classified() -> None:
    policy = load_status_policy()
    assert policy["verified"].promotion_class == PROMOTING
    assert policy["verified_with_note"].promotion_class == CONDITIONAL
    assert policy["workbench_verified"].promotion_class == CONDITIONAL
    assert policy["structural_derivation"].promotion_class == NON_PROMOTING
    assert is_automatically_promoting("verified")
    assert not is_automatically_promoting("structural_derivation")


def test_every_status_in_committed_stores_is_schema_recognized() -> None:
    policy = load_status_policy()
    observed: set[str] = set()
    for path in sorted((REPO_ROOT / "shared" / "sal-facts").glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        observed.update(
            str(fact["verification_status"])
            for fact in document.get("facts", [])
            if fact.get("verification_status")
        )
    assert observed
    assert observed <= set(policy)


def test_schema_accepts_each_governed_status_and_rejects_unknown() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for status in load_status_policy():
        assert not list(validator.iter_errors(_combined_with_status(status)))

    errors = list(
        validator.iter_errors(_combined_with_status("looks_verified_enough"))
    )
    assert errors


def test_policy_keys_must_cover_enum_exactly(tmp_path: Path) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    broken = copy.deepcopy(schema)
    del broken["$defs"]["verification_status"]["x-status-policy"]["verified"]
    path = tmp_path / "broken-schema.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly match"):
        load_status_policy(path)


def test_unknown_status_never_defaults_to_promoting() -> None:
    with pytest.raises(ValueError, match="unknown SAL verification status"):
        status_rule("unknown")


def test_extended_legacy_alias_requires_canonical_sal_identity() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    document = _combined_with_status("verified")
    fact = document["results"][0]["spec_facts"][0]
    fact["qname"] = "FACT-ZST-EX-0001"
    assert list(validator.iter_errors(document))

    fact["fact_id"] = "SAL-ZST-00016"
    assert not list(validator.iter_errors(document))


def test_current_derived_combined_database_is_schema_valid() -> None:
    combined_path = REPO_ROOT / ".local" / "spec-cache" / "sal-facts-latest.json"
    if not combined_path.is_file():
        pytest.skip("derived combined SAL database is absent")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    document = json.loads(combined_path.read_text(encoding="utf-8"))
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(document))
    assert not errors, errors[:5]
