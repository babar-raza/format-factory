"""Tests for strict adoption compliance enforcement.

Regression tests for: R100 failure where 4 non-exempt items, 0 transcripts,
0 skill_ids → still compliant=true.

These tests verify that the STRICT ENFORCEMENT rules are applied correctly.
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
from validate_adoption_compliance import (
    validate_adoption,
    COMPLIANCE_PASS,
    COMPLIANCE_PASS_WITH_EXEMPTIONS,
    COMPLIANCE_FAIL_MISSING_TRANSCRIPTS,
    COMPLIANCE_FAIL_MISSING_LEDGER,
)


def _make_declaration(items: list) -> dict:
    return {
        "run_id": "test-run",
        "sprint_id": "TEST-SPRINT",
        "planned_work_items": items,
    }


def _make_non_exempt_item(item_id: str, title: str, **kwargs) -> dict:
    return {"item_id": item_id, "title": title, **kwargs}


def _make_src_item(item_id: str, title: str, **kwargs) -> dict:
    return {
        "item_id": item_id,
        "title": title,
        "product_track": "commercial_dotnet",
        **kwargs,
    }


class TestStrictZeroTranscriptsZeroSkillIds:
    """R100 regression: 4 non-exempt items, 0 transcripts, 0 skill_ids must FAIL."""

    def test_r100_like_4_non_exempt_0_transcripts_0_skill_ids_fails(self):
        """R100-like fixture: 4 non-exempt items with no transcripts or skill_ids."""
        items = [
            _make_non_exempt_item("AUDIT-002", "Phase 2: Independent proof-backed POC audit"),
            _make_non_exempt_item("AUDIT-003", "Phase 3: Host runner reality reconciliation"),
            _make_non_exempt_item("AUDIT-004", "Phase 4: Run all tests and capture raw logs"),
            _make_non_exempt_item("AUDIT-005", "Phase 5: Gate 11 readiness packet"),
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is False, f"Expected fail but got: {result['summary']}"
        assert result["compliance_classification"] == COMPLIANCE_FAIL_MISSING_TRANSCRIPTS
        assert result["strict_fail"] is True

    def test_single_non_exempt_0_transcript_0_skill_fails(self):
        """Even a single non-exempt item with no transcript fails."""
        items = [_make_non_exempt_item("ITEM-001", "Run some product work")]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is False
        assert result["strict_fail"] is True

    def test_all_exempt_passes(self):
        """When all non-exempt items are zero because all items are exempt, pass."""
        items = [
            {"item_id": "W0-PREFLIGHT", "title": "Preflight"},
            {"item_id": "W9-FINAL", "title": "Final closeout"},
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is True
        assert result["non_exempt_items"] == 0

    def test_no_items_passes(self):
        """Empty declaration passes (no items to check)."""
        result = validate_adoption(_make_declaration([]))
        assert result["compliant"] is True


class TestExemptionReason:
    """Items with explicit exemption_reason can pass without transcripts."""

    def test_audit_only_item_with_exemption_passes(self):
        """Audit item with explicit exemption_reason passes."""
        items = [
            _make_non_exempt_item(
                "AUDIT-001",
                "Phase 2: Independent audit",
                exemption_reason="Audit-only sprint. No source code changed. Transcripts not applicable.",
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is True
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS

    def test_all_non_exempt_have_exemption_passes(self):
        """All non-exempt items with exemptions pass."""
        items = [
            _make_non_exempt_item(
                "AUDIT-002",
                "Phase 2: Audit",
                exemption_reason="No src changes this sprint.",
            ),
            _make_non_exempt_item(
                "AUDIT-003",
                "Phase 3: Review",
                exemption_reason="No src changes this sprint.",
            ),
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is True
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS

    def test_partial_exemptions_fails(self):
        """Only some non-exempt items have exemptions — fails."""
        items = [
            _make_non_exempt_item(
                "AUDIT-001",
                "Phase 1",
                exemption_reason="No src changes.",
            ),
            _make_non_exempt_item("AUDIT-002", "Phase 2"),  # no exemption
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is False
        assert result["strict_fail"] is True


class TestSourceChangingItemsRequireTranscript:
    """Source-changing items always require transcript + skill_id + ledger."""

    def test_src_item_without_transcript_fails(self):
        """Source-changing item without transcript fails."""
        items = [_make_src_item("SRC-001", "Add new capability to FODS")]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is False
        assert result["compliance_classification"] == COMPLIANCE_FAIL_MISSING_TRANSCRIPTS

    def test_src_item_without_ledger_fails(self):
        """Source-changing item without ledger entry fails."""
        items = [
            _make_src_item(
                "SRC-001",
                "Add new capability to FODS",
                skill_id="add-dotnet-api",
                evidence_paths=["reports/transcript.json"],
            )
        ]
        result = validate_adoption(_make_declaration(items))
        # transcript path doesn't match "transcript" + .json pattern properly
        # but ledger is also missing, so FAIL
        assert result["compliant"] is False

    def test_src_item_with_all_required_passes(self):
        """Source-changing item with transcript, skill_id, ledger passes."""
        items = [
            _make_src_item(
                "SRC-001",
                "Add new capability to FODS",
                skill_id="add-dotnet-api",
                ledger_entry_id="R120-FODS-001",
                evidence_paths=["reports/run/transcript.json"],
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is True
        assert result["compliance_classification"] == COMPLIANCE_PASS

    def test_src_item_with_fallback_transcript_passes(self):
        """Source-changing item with fallback_transcript + skill_id + ledger passes."""
        items = [
            _make_src_item(
                "SRC-001",
                "Add new FODS feature",
                fallback_skill_id="add-dotnet-api",
                ledger_entry_id="R120-FODS-001",
                fallback_transcript="Governed skill execution via add-dotnet-api skill. Changes made to FodsDocument.cs.",
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is True

    def test_src_item_with_explicit_exemption_passes(self):
        """Source-changing item with explicit exemption_reason can pass."""
        items = [
            _make_src_item(
                "SRC-001",
                "Add FODS feature",
                exemption_reason="Skill was pre-approved; transcript captured in lane ledger.",
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliant"] is True
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS


class TestProcessOverheadExemptions:
    """Process overhead items (W0-, W9-, W10-, preflight, etc.) are always exempt."""

    def test_w0_prefix_exempt(self):
        items = [{"item_id": "W0-PREFLIGHT", "title": "Preflight setup"}]
        result = validate_adoption(_make_declaration(items))
        assert result["exempt_items"] == 1
        assert result["compliant"] is True

    def test_w9_prefix_exempt(self):
        items = [{"item_id": "W9-FINAL-CLOSEOUT", "title": "Final closeout"}]
        result = validate_adoption(_make_declaration(items))
        assert result["exempt_items"] == 1

    def test_w10_prefix_exempt(self):
        items = [{"item_id": "W10-EVIDENCE", "title": "Evidence package"}]
        result = validate_adoption(_make_declaration(items))
        assert result["exempt_items"] == 1

    def test_preflight_title_exempt(self):
        items = [{"item_id": "PHASE-0", "title": "Phase 0: Preflight and setup"}]
        result = validate_adoption(_make_declaration(items))
        assert result["exempt_items"] == 1

    def test_closeout_title_exempt(self):
        items = [{"item_id": "CLOSE-1", "title": "Sprint closeout and evidence"}]
        result = validate_adoption(_make_declaration(items))
        assert result["exempt_items"] == 1


class TestComplianceClassification:
    """Test that compliance_classification field is set correctly."""

    def test_pass_classification(self):
        items = [
            _make_src_item(
                "SRC-001",
                "Add feature",
                skill_id="add-dotnet-api",
                ledger_entry_id="R120-001",
                evidence_paths=["reports/run/transcript.json"],
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliance_classification"] == COMPLIANCE_PASS

    def test_pass_with_exemptions_classification(self):
        items = [
            _make_non_exempt_item(
                "AUDIT-001",
                "Run audit",
                exemption_reason="No src changes.",
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliance_classification"] == COMPLIANCE_PASS_WITH_EXEMPTIONS

    def test_fail_missing_transcripts_classification(self):
        items = [_make_src_item("SRC-001", "Add feature without transcript")]
        result = validate_adoption(_make_declaration(items))
        assert result["compliance_classification"] == COMPLIANCE_FAIL_MISSING_TRANSCRIPTS

    def test_fail_missing_ledger_classification(self):
        items = [
            _make_src_item(
                "SRC-001",
                "Add feature with transcript but no ledger",
                skill_id="add-dotnet-api",
                evidence_paths=["reports/run/transcript.json"],
            )
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["compliance_classification"] == COMPLIANCE_FAIL_MISSING_LEDGER


class TestNonExemptSummaryFields:
    """Test that summary fields are correctly populated."""

    def test_non_exempt_count_correct(self):
        items = [
            {"item_id": "W0-PRE", "title": "Preflight"},  # exempt
            _make_non_exempt_item("ITEM-001", "Work item 1"),  # non-exempt
            _make_non_exempt_item("ITEM-002", "Work item 2"),  # non-exempt
        ]
        result = validate_adoption(_make_declaration(items))
        assert result["exempt_items"] == 1
        assert result["non_exempt_items"] == 2

    def test_with_transcript_count(self):
        items = [
            _make_src_item(
                "SRC-001",
                "Work",
                skill_id="add-dotnet-api",
                ledger_entry_id="R-001",
                evidence_paths=["reports/transcript.json"],
            ),
            _make_src_item("SRC-002", "Work without transcript"),
        ]
        result = validate_adoption(_make_declaration(items))
        # First item has "transcript" in path + .json extension = has_transcript=True
        assert result["items_with_transcript"] == 1
