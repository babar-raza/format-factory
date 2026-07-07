"""
test_fast_format_authority_r126.py
Sprint: SPEC-AUTHORITY-LAYER-FAST-OPS-INTEGRATION-AND-AUTHORITY-CONVEYOR-001
Added: 2026-06-08

Tests for Lane 4: fast-format authority extraction results.

Verifies that ZST and CSV spec-cache workbench files have the expected
verified facts / candidate facts from the authority conveyor sprint.
"""
import sys
from pathlib import Path

import pytest

# Repo root discovery
_REPO_ROOT = None
_candidate = Path(__file__).resolve()
for _p in [_candidate, *_candidate.parents]:
    if (_p / ".git").exists():
        _REPO_ROOT = _p
        break
if _REPO_ROOT is None:
    _REPO_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

try:
    import yaml as _yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"
pytestmark = pytest.mark.skipif(
    not _SPEC_CACHE.is_dir(),
    reason="SAL spec-cache not present in this environment",
)


def _load_facts(format_id: str) -> list[dict]:
    """Load facts from spec-cache verified-facts-review.yaml for a format."""
    spec_dir = _REPO_ROOT / ".local" / "spec-cache" / format_id.lower()
    if not spec_dir.exists():
        return []
    facts = []
    for ff in spec_dir.rglob("verified-facts-review.yaml"):
        if _YAML_AVAILABLE:
            data = _yaml.safe_load(ff.read_text(encoding="utf-8")) or {}
        else:
            data = {}
        facts.extend(data.get("facts", []))
    return facts


def _facts_by_status(facts: list[dict], status: str) -> list[dict]:
    return [f for f in facts if f.get("provenance", {}).get("verification_status") == status]


# ============================================================
# ZST facts — Lane 4 deliverable
# ============================================================


class TestZstFactExtraction:
    """Verify ZST Lane 4 output: 2 verified facts from RFC 8878."""

    def test_zst_spec_cache_exists(self):
        """ZST spec-cache directory must exist."""
        spec_dir = _REPO_ROOT / ".local" / "spec-cache" / "zst"
        assert spec_dir.exists(), "ZST spec-cache directory not found"

    def test_zst_has_verified_facts_file(self):
        """ZST workbench must have a verified-facts-review.yaml."""
        spec_dir = _REPO_ROOT / ".local" / "spec-cache" / "zst"
        files = list(spec_dir.rglob("verified-facts-review.yaml"))
        assert len(files) >= 1, "No verified-facts-review.yaml found under ZST spec-cache"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_has_at_least_two_facts(self):
        """ZST must have at least 2 facts extracted (Lane 4 target)."""
        facts = _load_facts("zst")
        assert len(facts) >= 2, f"Expected at least 2 ZST facts, found {len(facts)}"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_fact_001_present(self):
        """FACT-ZST-001 (magic number) must be present."""
        facts = _load_facts("zst")
        ids = [f.get("claim_id") for f in facts]
        assert "FACT-ZST-001" in ids, f"FACT-ZST-001 not found. Available: {ids}"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_fact_002_present(self):
        """FACT-ZST-002 (skippable frame magic) must be present."""
        facts = _load_facts("zst")
        ids = [f.get("claim_id") for f in facts]
        assert "FACT-ZST-002" in ids, f"FACT-ZST-002 not found. Available: {ids}"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_fact_001_is_verified(self):
        """FACT-ZST-001 must have verification_status=verified."""
        facts = _load_facts("zst")
        fact = next((f for f in facts if f.get("claim_id") == "FACT-ZST-001"), None)
        assert fact is not None
        status = fact.get("provenance", {}).get("verification_status")
        assert status == "verified", f"FACT-ZST-001 status={status!r}, expected 'verified'"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_fact_002_is_verified(self):
        """FACT-ZST-002 must have verification_status=verified."""
        facts = _load_facts("zst")
        fact = next((f for f in facts if f.get("claim_id") == "FACT-ZST-002"), None)
        assert fact is not None
        status = fact.get("provenance", {}).get("verification_status")
        assert status == "verified", f"FACT-ZST-002 status={status!r}, expected 'verified'"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_facts_use_tier1_extraction(self):
        """ZST verified facts must use tier1_direct_citation extraction."""
        facts = _load_facts("zst")
        verified = _facts_by_status(facts, "verified")
        assert len(verified) >= 1, "No verified ZST facts"
        for f in verified:
            method = f.get("provenance", {}).get("extraction_method")
            assert method in ("tier1_direct_citation", "tier1_section"), (
                f"{f['claim_id']}: extraction_method={method!r} is not tier1"
            )

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_facts_validated_by_deterministic_method(self):
        """ZST verified facts must be validated by a deterministic method."""
        from validate_spec_fact_refs import _INDEPENDENT_VERIFICATION_METHODS
        facts = _load_facts("zst")
        verified = _facts_by_status(facts, "verified")
        assert len(verified) >= 1
        for f in verified:
            validator = f.get("provenance", {}).get("validated_by")
            assert validator in _INDEPENDENT_VERIFICATION_METHODS, (
                f"{f['claim_id']}: validated_by={validator!r} not in independent methods"
            )

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_fact_001_mentions_magic_number(self):
        """FACT-ZST-001 claim must mention the Zstandard magic number."""
        facts = _load_facts("zst")
        fact = next((f for f in facts if f.get("claim_id") == "FACT-ZST-001"), None)
        assert fact is not None
        claim = fact.get("claim", "")
        # Magic number 0xFD2FB528 in hex or decimal
        assert "0xFD2FB528" in claim or "FD2FB528" in claim, (
            f"FACT-ZST-001 claim does not mention magic number 0xFD2FB528: {claim!r}"
        )

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_zst_fact_002_mentions_skippable_range(self):
        """FACT-ZST-002 claim must mention skippable frame magic range."""
        facts = _load_facts("zst")
        fact = next((f for f in facts if f.get("claim_id") == "FACT-ZST-002"), None)
        assert fact is not None
        claim = fact.get("claim", "")
        assert "skippable" in claim.lower() or "0x184D2A5" in claim or "184D2A5" in claim, (
            f"FACT-ZST-002 claim does not mention skippable frame: {claim!r}"
        )


# ============================================================
# CSV facts — Lane 4 deliverable (candidate only, blocker documented)
# ============================================================


class TestCsvFactExtraction:
    """Verify CSV Lane 4 output: candidate facts with documented blocker."""

    def test_csv_spec_cache_exists(self):
        """CSV spec-cache directory must exist."""
        spec_dir = _REPO_ROOT / ".local" / "spec-cache" / "csv"
        assert spec_dir.exists(), "CSV spec-cache directory not found"

    def test_csv_has_verified_facts_file(self):
        """CSV workbench must have a verified-facts-review.yaml."""
        spec_dir = _REPO_ROOT / ".local" / "spec-cache" / "csv"
        files = list(spec_dir.rglob("verified-facts-review.yaml"))
        assert len(files) >= 1, "No verified-facts-review.yaml found under CSV spec-cache"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_csv_has_candidate_facts(self):
        """CSV must have at least 1 candidate (needs_review) fact."""
        facts = _load_facts("csv")
        candidates = _facts_by_status(facts, "needs_review")
        assert len(candidates) >= 1, f"Expected candidate CSV facts, found none. Total facts: {len(facts)}"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_csv_fact_001_present(self):
        """FACT-CSV-001 (MIME type) must be present."""
        facts = _load_facts("csv")
        ids = [f.get("claim_id") for f in facts]
        assert "FACT-CSV-001" in ids, f"FACT-CSV-001 not found. Available: {ids}"

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_csv_fact_001_is_candidate_not_verified(self):
        """FACT-CSV-001 must be needs_review (RFC text not cached yet)."""
        facts = _load_facts("csv")
        fact = next((f for f in facts if f.get("claim_id") == "FACT-CSV-001"), None)
        assert fact is not None
        status = fact.get("provenance", {}).get("verification_status")
        assert status == "needs_review", (
            f"FACT-CSV-001 is {status!r} — expected 'needs_review' since RFC not cached"
        )

    @pytest.mark.skipif(not _YAML_AVAILABLE, reason="yaml not installed")
    def test_csv_fact_has_documented_blocker(self):
        """CSV candidate facts must document the verification blocker."""
        facts = _load_facts("csv")
        fact = next((f for f in facts if f.get("claim_id") == "FACT-CSV-001"), None)
        assert fact is not None
        prov = fact.get("provenance", {})
        # blocker field or spec_text_cached=false
        has_blocker = bool(prov.get("blocker")) or (fact.get("spec_text_cached") is False)
        assert has_blocker, "FACT-CSV-001 has no documented blocker for unverified status"


# ============================================================
# Authority gate integration — ZST advances to P4 after conveyor
# ============================================================


class TestAuthorityGateAfterConveyor:
    """Verify that the authority gate tool correctly upgrades ZST to P4+ after fact extraction."""

    def test_zst_is_p4_or_better(self):
        """ZST must be P4+ in authority gate after verified facts were extracted."""
        from authority_gate_validation import validate_format_authority
        result = validate_format_authority("zst")
        assert result["authority_level_int"] >= 4, (
            f"ZST should be P4+ after verified facts; got {result['authority_level']}: {result['blockers']}"
        )

    def test_zst_readiness_allowed_after_conveyor(self):
        """ZST readiness must be allowed at P4+."""
        from authority_gate_validation import validate_format_authority
        result = validate_format_authority("zst")
        assert result["readiness_allowed"], (
            f"ZST readiness not allowed: {result['authority_level']} — {result['blockers']}"
        )

    def test_csv_is_p3_candidate_facts_only(self):
        """CSV must be P3 — candidate facts only, not verified."""
        from authority_gate_validation import validate_format_authority
        result = validate_format_authority("csv")
        # P3 or possibly P2 if workbench file not found, but not higher than P3
        assert result["authority_level_int"] >= 2, "CSV should at least be P2 (spec cached)"
        # Not yet P4 — RFC text not verified
        # This test asserts the current state is accurate (P3 candidate or P2)
        assert result["authority_level_int"] <= 3, (
            f"CSV should be P3 or lower (unverified facts); got {result['authority_level']}"
        )

    def test_fods_retains_p6_after_conveyor(self):
        """FODS P6 must not be degraded by the conveyor sprint."""
        from authority_gate_validation import validate_format_authority
        result = validate_format_authority("fods")
        assert result["authority_level_int"] >= 6, (
            f"FODS should remain P6; got {result['authority_level']}: {result['blockers']}"
        )
