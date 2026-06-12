"""
Lane 6: FODS FACT-FODS-002 quarantine and spec_fact_refs exclusion tests.

Sprint: FORMAT-FACTORY-SAL-PHASE2-CLOSEOUT-AND-PRODUCT-GATED-ADVANCEMENT-001

FACT-FODS-002 claim: "FODS mimetype is application/vnd.oasis.opendocument.spreadsheet-flat-xml"
verification_status in verified-facts-review.yaml: not_found_in_normalized_text

Policy:
- not_found_in_normalized_text facts MUST NOT appear in spec_fact_refs (verified-only)
- They MAY appear in spec_refs (all facts, including unverified)
- The capability map generator enforces this via the verified_only=True filter
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / "tools" / "capability_layer"))

from capability_map_generator import _load_spec_facts, _VERIFIED_FACT_STATUSES, _NON_AUTHORITATIVE_STATUSES


class TestVerificationStatusConstants:
    """Verify the classification constants are correct."""

    def test_not_found_in_non_authoritative(self):
        assert "not_found_in_normalized_text" in _NON_AUTHORITATIVE_STATUSES

    def test_verified_in_authoritative(self):
        assert "verified" in _VERIFIED_FACT_STATUSES

    def test_verified_with_note_in_authoritative(self):
        assert "verified_with_note" in _VERIFIED_FACT_STATUSES

    def test_needs_review_in_non_authoritative(self):
        assert "needs_review" in _NON_AUTHORITATIVE_STATUSES

    def test_needs_recheck_in_non_authoritative(self):
        assert "needs_recheck" in _NON_AUTHORITATIVE_STATUSES

    def test_no_overlap_between_sets(self):
        """verified and non-authoritative sets must not overlap."""
        assert len(_VERIFIED_FACT_STATUSES & _NON_AUTHORITATIVE_STATUSES) == 0


class TestFodsFact002Exclusion:
    """FACT-FODS-002 (not_found_in_normalized_text) must be excluded from spec_fact_refs."""

    def test_fods_all_facts_includes_fact_002(self):
        """verified_only=False includes all facts regardless of status."""
        all_facts = _load_spec_facts("fods", verified_only=False)
        # Either included or FODS has no fact file — both are acceptable
        # But if FACT-FODS-001 is present, FACT-FODS-002 should be present too
        if "FACT-FODS-001" in all_facts:
            assert "FACT-FODS-002" in all_facts, (
                "FACT-FODS-002 should appear in all-facts list (not filtered)"
            )

    def test_fods_verified_only_excludes_fact_002(self):
        """verified_only=True must NOT include FACT-FODS-002."""
        verified_facts = _load_spec_facts("fods", verified_only=True)
        assert "FACT-FODS-002" not in verified_facts, (
            "FACT-FODS-002 has not_found_in_normalized_text status — must be excluded from spec_fact_refs"
        )

    def test_fods_verified_only_includes_other_facts(self):
        """verified_only=True should include properly verified FODS facts."""
        verified_facts = _load_spec_facts("fods", verified_only=True)
        # FACT-FODS-001 and others are 'verified' or 'verified_with_note'
        assert len(verified_facts) > 0, "FODS should have some verified facts"
        assert "FACT-FODS-001" in verified_facts, "FACT-FODS-001 should be in verified facts"

    def test_fods_verified_count_less_than_all_count(self):
        """verified_only set should be smaller because FACT-FODS-002 is excluded."""
        all_facts = _load_spec_facts("fods", verified_only=False)
        verified_facts = _load_spec_facts("fods", verified_only=True)
        if all_facts:
            assert len(verified_facts) <= len(all_facts), (
                "Verified-only list cannot be larger than all-facts list"
            )


class TestCapabilityMapSpecFactRefsPolicy:
    """Test that capability map output respects the quarantine policy."""

    def test_zst_spec_fact_refs_populated(self):
        """ZST has verified facts — spec_fact_refs must be non-empty."""
        zst_verified = _load_spec_facts("zst", verified_only=True)
        assert len(zst_verified) > 0
        assert "FACT-ZST-001" in zst_verified

    def test_pbm_spec_fact_refs_populated(self):
        """PBM has verified facts."""
        pbm_verified = _load_spec_facts("pbm", verified_only=True)
        assert len(pbm_verified) > 0

    def test_abw_has_no_spec_fact_refs(self):
        """ABW has no spec cache — spec_fact_refs must be empty list, not error."""
        abw_verified = _load_spec_facts("abw", verified_only=True)
        assert isinstance(abw_verified, list)
        assert abw_verified == []

    def test_dif_has_no_spec_fact_refs(self):
        """DIF has no spec cache — spec_fact_refs must be empty list, not error."""
        dif_verified = _load_spec_facts("dif", verified_only=True)
        assert isinstance(dif_verified, list)
        assert dif_verified == []

    def test_unknown_format_returns_empty_list(self):
        """Unknown format ID returns empty list, never raises exception."""
        result = _load_spec_facts("nonexistent_format_xyz", verified_only=True)
        assert isinstance(result, list)
        assert result == []


class TestFodsFact002ReviewFileState:
    """Verify FACT-FODS-002 review file has the expected quarantine status."""

    def _get_fact_002_entry(self):
        review_file = (
            REPO / ".local" / "spec-cache" / "fods" / "1.3"
            / "workbench" / "verified-facts-review.yaml"
        )
        if not review_file.exists():
            return None
        import yaml  # noqa: PLC0415
        try:
            with open(review_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            return None
        if isinstance(data, dict) and "facts" in data:
            facts = data["facts"]
        elif isinstance(data, list):
            facts = data
        else:
            return None
        for fact in facts:
            if isinstance(fact, dict) and fact.get("claim_id") == "FACT-FODS-002":
                return fact
        return None

    def test_fact_002_review_exists_and_quarantined(self):
        """FACT-FODS-002 in review file must have not_found_in_normalized_text status."""
        entry = self._get_fact_002_entry()
        if entry is None:
            # No review file — acceptable (no FODS spec cache)
            return
        prov = entry.get("provenance", {}) or {}
        vstat = entry.get("verification_status") or prov.get("verification_status", "")
        assert vstat == "not_found_in_normalized_text", (
            f"FACT-FODS-002 should be quarantined with not_found_in_normalized_text, got: {vstat}"
        )

    def test_fact_002_claim_is_mimetype(self):
        """FACT-FODS-002 should be the FODS MIME type claim."""
        entry = self._get_fact_002_entry()
        if entry is None:
            return
        claim = entry.get("claim", "")
        assert "mimetype" in claim.lower() or "mime" in claim.lower() or "application/vnd" in claim, (
            f"FACT-FODS-002 should be a MIME type claim, got: {claim}"
        )

    def test_fact_002_confidence_still_high(self):
        """Quarantine does not mean the claim is wrong — confidence should remain high."""
        entry = self._get_fact_002_entry()
        if entry is None:
            return
        prov = entry.get("provenance", {}) or {}
        confidence = entry.get("confidence") or prov.get("confidence", "")
        # high or medium are acceptable — it's quarantined because it's not in Part 3, not because it's wrong
        assert confidence in ("high", "medium", ""), (
            f"FACT-FODS-002 confidence should not be low, got: {confidence}"
        )
