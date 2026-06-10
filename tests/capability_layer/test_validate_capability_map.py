"""Unit tests for validate_capability_map.py validator functions.

Sprint: FORMAT-FACTORY-CAPABILITY-LAYER-REPAIR-AND-HARDENING-001
Tests: VAL-002 (ai_draft), VAL-003 (provenance), VAL-006 (separation),
       VAL-008 (taskcard links), VAL-009 (advisory_only)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "capability_layer"))

from validate_capability_map import (
    ValidationResult,
    _check_val002_no_draft_as_verified,
    _check_val003_verified_have_provenance,
    _check_val006_commercial_foss_separated,
    _check_val008_gap_taskcard_links,
    _check_val009_action_queue_advisory,
)


def _make_record(**overrides):
    base = {
        "capability_id": "TEST-001",
        "format": "TSV",
        "product_type": "foss_reduced",
        "capability_name": "Load",
        "current_state": "test_verified",
        "confidence_level": "high",
        "implementation_refs": ["src/python/tsv/tsv_parser.py::load"],
        "test_refs": ["tests/python/tsv/test_r125_tsv_load_tsv.py"],
        "spec_refs": [],
        "requirement_refs": [],
        "source_refs": [],
        "example_refs": [],
        "package_refs": [],
        "dogfood_refs": [],
        "evidence_refs": [],
    }
    base.update(overrides)
    return base


class TestVal002NoDraftAsVerified:

    def test_ai_draft_with_impl_refs_is_error(self):
        rec = _make_record(
            current_state="ai_draft",
            implementation_refs=["src/python/tsv/tsv_parser.py::fake"],
        )
        result = ValidationResult()
        _check_val002_no_draft_as_verified([rec], result)
        assert not result.passed, "ai_draft with implementation_refs should be an error"

    def test_ai_draft_without_refs_is_ok(self):
        rec = _make_record(
            current_state="ai_draft",
            implementation_refs=[],
        )
        result = ValidationResult()
        _check_val002_no_draft_as_verified([rec], result)
        assert result.passed

    def test_verified_state_is_ok(self):
        rec = _make_record(current_state="test_verified")
        result = ValidationResult()
        _check_val002_no_draft_as_verified([rec], result)
        assert result.passed


class TestVal003VerifiedHaveProvenance:

    def test_verified_with_refs_passes(self):
        rec = _make_record(current_state="test_verified")
        result = ValidationResult()
        _check_val003_verified_have_provenance([rec], result)
        assert result.passed

    def test_verified_no_refs_fails(self):
        rec = _make_record(
            current_state="test_verified",
            implementation_refs=[],
            test_refs=[],
            spec_refs=[],
            requirement_refs=[],
            source_refs=[],
            example_refs=[],
            package_refs=[],
            dogfood_refs=[],
            evidence_refs=[],
        )
        result = ValidationResult()
        _check_val003_verified_have_provenance([rec], result)
        assert not result.passed, "Verified state with zero refs should fail"

    def test_missing_state_skipped(self):
        rec = _make_record(
            current_state="missing",
            implementation_refs=[],
            test_refs=[],
        )
        result = ValidationResult()
        _check_val003_verified_have_provenance([rec], result)
        assert result.passed


class TestVal006CommercialFossSeparation:

    def test_commercial_record_in_commercial_map_passes(self, tmp_path):
        commercial = tmp_path / "commercial.json"
        foss = tmp_path / "foss.json"
        commercial.write_text(json.dumps({
            "capabilities": [_make_record(product_type="commercial")]
        }))
        foss.write_text(json.dumps({
            "capabilities": [_make_record(product_type="foss_reduced")]
        }))
        result = ValidationResult()
        _check_val006_commercial_foss_separated(commercial, foss, result)
        assert result.passed

    def test_foss_in_commercial_map_fails(self, tmp_path):
        commercial = tmp_path / "commercial.json"
        foss = tmp_path / "foss.json"
        commercial.write_text(json.dumps({
            "capabilities": [_make_record(product_type="foss_reduced")]
        }))
        foss.write_text(json.dumps({"capabilities": []}))
        result = ValidationResult()
        _check_val006_commercial_foss_separated(commercial, foss, result)
        assert not result.passed, "FOSS record in commercial map should fail"


class TestVal008GapTaskcardLinks:

    def test_gap_with_suggested_taskcard_passes(self, tmp_path):
        gap_file = tmp_path / "gaps.json"
        gap_file.write_text(json.dumps({
            "gaps": [{"gap_id": "GAP-001", "suggested_taskcard": "Implement load for TSV"}]
        }))
        result = ValidationResult()
        _check_val008_gap_taskcard_links(gap_file, result)
        assert result.passed

    def test_gap_without_suggested_taskcard_warns(self, tmp_path):
        gap_file = tmp_path / "gaps.json"
        gap_file.write_text(json.dumps({
            "gaps": [{"gap_id": "GAP-001", "suggested_taskcard": ""}]
        }))
        result = ValidationResult()
        _check_val008_gap_taskcard_links(gap_file, result)
        assert len(result.warnings) > 0


class TestVal009ActionQueueAdvisory:

    def test_advisory_only_passes(self, tmp_path):
        q = tmp_path / "actions.json"
        q.write_text(json.dumps({
            "actions": [{"action_id": "ACT-001", "advisory_only": True}]
        }))
        result = ValidationResult()
        _check_val009_action_queue_advisory(q, result)
        assert result.passed

    def test_missing_advisory_only_fails(self, tmp_path):
        q = tmp_path / "actions.json"
        q.write_text(json.dumps({
            "actions": [{"action_id": "ACT-001"}]
        }))
        result = ValidationResult()
        _check_val009_action_queue_advisory(q, result)
        assert not result.passed, "Missing advisory_only should be an error"
