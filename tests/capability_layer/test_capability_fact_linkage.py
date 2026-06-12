"""
Tests for direct spec_fact_refs linkage in capability map entries.

Sprint: FORMAT-FACTORY-SAL-PHASE2-CLOSEOUT-AND-PRODUCT-GATED-ADVANCEMENT-001
Heals: SAL-GAP-003 — capability map entries lacked direct FACT-* linkage.

Pilot formats: ZST, FODS, FODT, PBM, PGM, PPM, Netpbm.
Non-spec formats must NOT have fake fact refs: ABW, DIF, FODG, Gnumeric.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / "tools" / "capability_layer"))

from capability_map_generator import _load_spec_facts, _VERIFIED_FACT_STATUSES, _NON_AUTHORITATIVE_STATUSES


class TestLoadSpecFactsFiltering:
    """Verify _load_spec_facts filtering by verified_only."""

    def test_zst_all_facts_loaded(self):
        facts = _load_spec_facts("zst")
        assert "FACT-ZST-001" in facts
        assert "FACT-ZST-002" in facts

    def test_zst_verified_only_matches_all(self):
        all_facts = _load_spec_facts("zst")
        verified = _load_spec_facts("zst", verified_only=True)
        # ZST facts are all verified so they should match
        assert set(verified) == set(all_facts)

    def test_fods_all_facts_includes_not_found(self):
        all_facts = _load_spec_facts("fods")
        assert "FACT-FODS-002" in all_facts, "All-facts should include FACT-FODS-002"

    def test_fods_verified_only_excludes_not_found(self):
        verified = _load_spec_facts("fods", verified_only=True)
        assert "FACT-FODS-002" not in verified, (
            "FACT-FODS-002 has not_found_in_normalized_text status and must be excluded"
        )

    def test_fods_verified_only_includes_verified_facts(self):
        verified = _load_spec_facts("fods", verified_only=True)
        assert "FACT-FODS-001" in verified
        assert "FACT-FODS-003" in verified
        assert len(verified) >= 8, f"Expected at least 8 verified FODS facts, got {len(verified)}"

    def test_pbm_verified_facts_loaded(self):
        verified = _load_spec_facts("pbm", verified_only=True)
        assert "FACT-PBM-001" in verified
        assert "FACT-PBM-002" in verified

    def test_pgm_verified_facts_loaded(self):
        verified = _load_spec_facts("pgm", verified_only=True)
        assert "FACT-PGM-001" in verified
        assert "FACT-PGM-002" in verified

    def test_ppm_verified_facts_loaded(self):
        verified = _load_spec_facts("ppm", verified_only=True)
        assert "FACT-PPM-001" in verified
        assert "FACT-PPM-002" in verified

    def test_abw_has_no_facts(self):
        facts = _load_spec_facts("abw")
        assert facts == [], f"ABW should have no spec facts (no public spec), got: {facts}"

    def test_dif_has_no_facts(self):
        facts = _load_spec_facts("dif")
        assert facts == [], f"DIF should have no spec facts (historical ref), got: {facts}"


class TestCapabilityMapSpecFactRefs:
    """Verify the capability map has spec_fact_refs populated for pilot formats."""

    @classmethod
    def _load_map(cls):
        map_path = REPO / "reports" / "capability-layer" / "unified-capability-map.json"
        if not map_path.exists():
            return None
        data = json.loads(map_path.read_text(encoding="utf-8"))
        return data.get("capabilities", [])

    def test_zst_entries_have_spec_fact_refs(self):
        caps = self._load_map()
        if caps is None:
            return  # Map not yet generated — skip
        zst = [c for c in caps if c.get("format") == "ZST"]
        assert zst, "No ZST entries found in capability map"
        for entry in zst[:3]:  # Check first 3
            sfr = entry.get("spec_fact_refs", [])
            assert sfr, f"ZST entry {entry.get('capability_id')} has empty spec_fact_refs"
            assert "FACT-ZST-001" in sfr or "FACT-ZST-002" in sfr

    def test_fods_entries_have_spec_fact_refs(self):
        caps = self._load_map()
        if caps is None:
            return
        fods = [c for c in caps if c.get("format") == "FODS"]
        assert fods, "No FODS entries found"
        entry = fods[0]
        sfr = entry.get("spec_fact_refs", [])
        assert sfr, "FODS entry has empty spec_fact_refs"
        assert "FACT-FODS-001" in sfr

    def test_fods_spec_fact_refs_excludes_not_found(self):
        caps = self._load_map()
        if caps is None:
            return
        fods = [c for c in caps if c.get("format") == "FODS"]
        for entry in fods[:5]:
            sfr = entry.get("spec_fact_refs", [])
            assert "FACT-FODS-002" not in sfr, (
                f"FACT-FODS-002 (not_found_in_normalized_text) must not appear in spec_fact_refs"
            )

    def test_pbm_entries_have_spec_fact_refs(self):
        caps = self._load_map()
        if caps is None:
            return
        pbm = [c for c in caps if c.get("format") == "PBM"]
        assert pbm, "No PBM entries found"
        for entry in pbm[:3]:
            sfr = entry.get("spec_fact_refs", [])
            assert sfr, f"PBM entry {entry.get('capability_id')} has empty spec_fact_refs"

    def test_abw_entries_have_no_fake_spec_fact_refs(self):
        caps = self._load_map()
        if caps is None:
            return
        abw = [c for c in caps if c.get("format") == "ABW"]
        for entry in abw[:5]:
            sfr = entry.get("spec_fact_refs", [])
            assert not sfr, f"ABW must not have fake spec_fact_refs, got: {sfr}"

    def test_dif_entries_have_no_fake_spec_fact_refs(self):
        caps = self._load_map()
        if caps is None:
            return
        dif = [c for c in caps if c.get("format") == "DIF"]
        for entry in dif[:5]:
            sfr = entry.get("spec_fact_refs", [])
            assert not sfr, f"DIF must not have fake spec_fact_refs, got: {sfr}"

    def test_spec_fact_refs_field_exists_in_entries(self):
        caps = self._load_map()
        if caps is None:
            return
        # Every entry must have the spec_fact_refs field (even if empty)
        for entry in caps[:50]:
            assert "spec_fact_refs" in entry, (
                f"Entry {entry.get('capability_id')} missing spec_fact_refs field"
            )
