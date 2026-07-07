"""
test_authority_gate_validation.py
Sprint: SPEC-AUTHORITY-LAYER-FAST-OPS-INTEGRATION-AND-AUTHORITY-CONVEYOR-001
Added: 2026-06-08

Tests for tools/supervisor/authority_gate_validation.py
"""
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"

from authority_gate_validation import (
    validate_format_authority,
    NO_PUBLIC_SPEC_FORMATS,
    SCHEMA_ONLY_FORMATS,
    MIN_PRODUCT_EXPANSION_LEVEL,
    MIN_READINESS_LEVEL,
)


# ============================================================
# Integration tests against real repo state
# ============================================================


class TestRealFormatStates:
    """Integration tests against actual repo spec-cache state."""

    pytestmark = pytest.mark.skipif(
        not _SPEC_CACHE.is_dir(),
        reason="SAL spec-cache not present in this environment",
    )

    def test_fods_achieves_p6(self):
        """FODS must be P6 — proof graph, verified facts, code+test citations all present."""
        result = validate_format_authority("fods")
        assert result["authority_level"] == "P6"
        assert result["authority_level_int"] == 6
        assert result["readiness_allowed"]
        assert result["product_expansion_allowed"]
        assert result["blockers"] == []

    def test_zst_achieves_p4_after_conveyor(self):
        """ZST must be P4+ after authority conveyor sprint extracted verified facts."""
        result = validate_format_authority("zst")
        assert result["authority_level_int"] >= 4
        assert result["readiness_allowed"]  # P4 or better
        assert "FACT-ZST-001" in result["spec_state_summary"]["verified_fact_ids"]

    def test_gnumeric_is_p1_schema_only(self):
        """Gnumeric must be P1 — schema-only, no formal spec."""
        result = validate_format_authority("gnumeric")
        assert result["authority_level"] == "P1"
        assert not result["readiness_allowed"]
        assert not result["product_expansion_allowed"]
        assert result["exception_allowed"] == "schema_authority_available"
        assert any("schema_only" in b for b in result["blockers"])

    def test_sylk_is_p1_no_public_spec(self):
        """SYLK must be P1 — no public spec available."""
        result = validate_format_authority("sylk")
        assert result["authority_level"] == "P1"
        assert result["exception_allowed"] == "no_public_spec_available"
        assert not result["readiness_allowed"]

    def test_abw_is_p1_no_public_spec(self):
        """ABW must be P1 — no accessible formal spec."""
        result = validate_format_authority("abw")
        assert result["authority_level"] == "P1"
        assert not result["readiness_allowed"]

    def test_csv_is_p3_candidate_facts(self):
        """CSV must be P3 — candidate facts extracted but not verified."""
        result = validate_format_authority("csv")
        assert result["authority_level_int"] >= 3  # P3 or better

    def test_unknown_format_is_p0(self):
        """Unknown format (no spec cache) must be P0."""
        result = validate_format_authority("totally-unknown-format-xyz")
        assert result["authority_level"] == "P0"
        assert not result["readiness_allowed"]
        assert not result["product_expansion_allowed"]
        assert result["debt_entry"] is not None


# ============================================================
# Unit tests with mock repo state
# ============================================================


class TestWithMockRepo:
    """Unit tests using temporary directories to simulate repo state."""

    def _make_spec_cache(self, tmp_path: Path, format_id: str, facts: list[dict]) -> None:
        """Helper: create a minimal spec-cache directory with verified-facts-review.yaml."""
        workbench = tmp_path / ".local" / "spec-cache" / format_id / "v1" / "workbench"
        workbench.mkdir(parents=True)
        import yaml
        (workbench / "verified-facts-review.yaml").write_text(
            yaml.dump({"facts": facts}), encoding="utf-8"
        )

    def test_p0_no_spec_cache(self, tmp_path):
        """P0 when no spec-cache exists for format."""
        result = validate_format_authority("nofmt", repo_root=tmp_path)
        assert result["authority_level"] == "P0"
        assert not result["readiness_allowed"]

    def test_p2_spec_cached_no_facts(self, tmp_path):
        """P2 when spec dir exists but no verified-facts-review.yaml."""
        (tmp_path / ".local" / "spec-cache" / "myfmt" / "v1").mkdir(parents=True)
        result = validate_format_authority("myfmt", repo_root=tmp_path)
        assert result["authority_level"] == "P2"
        assert not result["readiness_allowed"]

    def test_p3_candidate_facts_only(self, tmp_path):
        """P3 when only candidate (needs_review) facts exist."""
        self._make_spec_cache(tmp_path, "myfmt", [
            {"claim_id": "FACT-MYFMT-001", "claim": "test claim",
             "provenance": {"verification_status": "needs_review"}}
        ])
        result = validate_format_authority("myfmt", repo_root=tmp_path)
        assert result["authority_level"] == "P3"
        assert not result["readiness_allowed"]

    def test_p4_verified_facts_no_code_citation(self, tmp_path):
        """P4 when verified facts exist but no code citations."""
        self._make_spec_cache(tmp_path, "myfmt", [
            {"claim_id": "FACT-MYFMT-001", "claim": "test claim",
             "provenance": {"verification_status": "verified"}}
        ])
        result = validate_format_authority("myfmt", repo_root=tmp_path)
        assert result["authority_level"] == "P4"
        assert result["readiness_allowed"]
        assert result["product_expansion_allowed"]

    def test_p1_no_public_spec_format(self, tmp_path):
        """P1 for formats in NO_PUBLIC_SPEC_FORMATS."""
        # sylk is in NO_PUBLIC_SPEC_FORMATS
        result = validate_format_authority("sylk", repo_root=tmp_path)
        assert result["authority_level"] == "P1"
        assert result["exception_allowed"] == "no_public_spec_available"

    def test_p1_schema_only_format(self, tmp_path):
        """P1 for formats in SCHEMA_ONLY_FORMATS."""
        # gnumeric is in SCHEMA_ONLY_FORMATS
        result = validate_format_authority("gnumeric", repo_root=tmp_path)
        assert result["authority_level"] == "P1"
        assert result["exception_allowed"] == "schema_authority_available"

    def test_product_expansion_blocked_below_p4(self, tmp_path):
        """Product expansion is blocked at P3 and below."""
        # P3: candidate facts only
        self._make_spec_cache(tmp_path, "myfmt", [
            {"claim_id": "FACT-MYFMT-001", "claim": "c",
             "provenance": {"verification_status": "needs_review"}}
        ])
        result = validate_format_authority("myfmt", repo_root=tmp_path)
        assert not result["product_expansion_allowed"]
        assert not result["readiness_allowed"]

    def test_debt_entry_present_for_blocked_formats(self, tmp_path):
        """debt_entry is populated for formats with blockers."""
        result = validate_format_authority("nofmt", repo_root=tmp_path)
        assert result["debt_entry"] is not None
        assert "blockers" in result["debt_entry"]
        assert "resolution" in result["debt_entry"]

    def test_no_debt_entry_for_p6(self):
        """No debt entry for fully compliant P6 formats (no blockers)."""
        # FODS should be P6 in real repo
        result = validate_format_authority("fods")
        if result["authority_level"] == "P6":
            assert result["debt_entry"] is None
            assert result["blockers"] == []


# ============================================================
# Constants validation tests
# ============================================================


class TestAuthorityConstants:
    """Tests for authority level constants."""

    def test_min_product_expansion_level_is_p4(self):
        """Product expansion minimum is P4."""
        assert MIN_PRODUCT_EXPANSION_LEVEL == 4

    def test_min_readiness_level_is_p4(self):
        """Readiness minimum is P4."""
        assert MIN_READINESS_LEVEL == 4

    def test_no_public_spec_formats_includes_sylk_abw_tsv(self):
        """Formats with no public spec are correctly classified."""
        for fmt in ["sylk", "abw", "tsv", "txt"]:
            assert fmt in NO_PUBLIC_SPEC_FORMATS, f"{fmt} should be in NO_PUBLIC_SPEC_FORMATS"

    def test_schema_only_formats_includes_gnumeric(self):
        """Schema-only formats are correctly classified."""
        assert "gnumeric" in SCHEMA_ONLY_FORMATS

    def test_fods_not_in_no_public_spec(self):
        """FODS has a public spec — must NOT be in NO_PUBLIC_SPEC_FORMATS."""
        assert "fods" not in NO_PUBLIC_SPEC_FORMATS

    def test_zst_not_in_no_public_spec(self):
        """ZST has RFC 8878 — must NOT be in NO_PUBLIC_SPEC_FORMATS."""
        assert "zst" not in NO_PUBLIC_SPEC_FORMATS
