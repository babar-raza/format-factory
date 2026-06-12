"""
test_replay_lineage.py -- Lane R9-7 Tests (CONWAY-R9)

Tests for replay_lineage.py.

COVERAGE:
  - build_lineage_entry: structure, hash chaining, governance, genesis detection
  - validate_lineage_chain: empty, single genesis, consistent chain, broken chain
  - detect_fingerprint_drift: no prior, matching, mismatch detection
  - build_live_lineage_entry: smoke test with live replay_fingerprint
  - _lineage_hash determinism
  - Governance invariants

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from replay_lineage import (
    _stable_hash,
    _lineage_hash,
    build_lineage_entry,
    validate_lineage_chain,
    detect_fingerprint_drift,
    build_live_lineage_entry,
    LINEAGE_CONSISTENT,
    LINEAGE_MISMATCH,
    LINEAGE_GENESIS,
    LINEAGE_CHAIN_BROKEN,
    LINEAGE_EMPTY,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _genesis_entry(fmt="fods", sprint_id="SPRINT-001", fingerprint="fp_abc123"):
    return build_lineage_entry(fmt=fmt, sprint_id=sprint_id, fingerprint=fingerprint)


def _second_entry(prior, fmt="fods", sprint_id="SPRINT-002", fingerprint="fp_def456"):
    return build_lineage_entry(fmt=fmt, sprint_id=sprint_id, fingerprint=fingerprint, prior_entry=prior)


# ---------------------------------------------------------------------------
# _stable_hash and _lineage_hash
# ---------------------------------------------------------------------------

class TestHashes:
    def test_stable_hash_deterministic(self):
        assert _stable_hash("test") == _stable_hash("test")

    def test_stable_hash_length_16(self):
        assert len(_stable_hash("test")) == 16

    def test_lineage_hash_deterministic(self):
        h1 = _lineage_hash("fp1", "fp2", "SPRINT-001")
        h2 = _lineage_hash("fp1", "fp2", "SPRINT-001")
        assert h1 == h2

    def test_lineage_hash_genesis_vs_non_genesis_differ(self):
        h_genesis = _lineage_hash(None, "fp2", "SPRINT-001")
        h_non_genesis = _lineage_hash("fp1", "fp2", "SPRINT-001")
        assert h_genesis != h_non_genesis

    def test_lineage_hash_changes_with_sprint(self):
        h1 = _lineage_hash("fp1", "fp2", "SPRINT-001")
        h2 = _lineage_hash("fp1", "fp2", "SPRINT-002")
        assert h1 != h2

    def test_lineage_hash_changes_with_fingerprint(self):
        h1 = _lineage_hash("fp1", "fp2", "SPRINT-001")
        h2 = _lineage_hash("fp1", "fp3", "SPRINT-001")
        assert h1 != h2


# ---------------------------------------------------------------------------
# build_lineage_entry
# ---------------------------------------------------------------------------

class TestBuildLineageEntry:
    def test_required_keys_present(self):
        entry = _genesis_entry()
        for key in ["entry_id", "format_id", "sprint_id", "fingerprint",
                    "prior_fingerprint", "prior_lineage_hash", "lineage_hash",
                    "entry_index", "is_genesis", "created_date", "governance"]:
            assert key in entry, f"Missing key: {key}"

    def test_genesis_has_no_prior(self):
        entry = _genesis_entry()
        assert entry["prior_fingerprint"] is None
        assert entry["prior_lineage_hash"] is None
        assert entry["is_genesis"] is True
        assert entry["entry_index"] == 0

    def test_second_entry_links_to_genesis(self):
        gen = _genesis_entry()
        entry = _second_entry(gen)
        assert entry["prior_fingerprint"] == gen["fingerprint"]
        assert entry["prior_lineage_hash"] == gen["lineage_hash"]
        assert entry["is_genesis"] is False
        assert entry["entry_index"] == 1

    def test_entry_index_increments(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e3 = build_lineage_entry("fods", "SPRINT-003", "fp_ghi789", prior_entry=e2)
        assert gen["entry_index"] == 0
        assert e2["entry_index"] == 1
        assert e3["entry_index"] == 2

    def test_format_id_recorded(self):
        entry = _genesis_entry(fmt="fodt")
        assert entry["format_id"] == "fodt"

    def test_sprint_id_recorded(self):
        entry = _genesis_entry(sprint_id="CONWAY-R9-TEST")
        assert entry["sprint_id"] == "CONWAY-R9-TEST"

    def test_fingerprint_recorded(self):
        entry = _genesis_entry(fingerprint="fp_xyz999")
        assert entry["fingerprint"] == "fp_xyz999"

    def test_lineage_hash_is_consistent(self):
        """lineage_hash must equal _lineage_hash(prior_fp, fp, sprint_id)."""
        gen = _genesis_entry(fingerprint="fp_abc")
        expected = _lineage_hash(None, "fp_abc", "SPRINT-001")
        assert gen["lineage_hash"] == expected

    def test_second_entry_lineage_hash_consistent(self):
        gen = _genesis_entry(fingerprint="fp_abc")
        e2 = _second_entry(gen, fingerprint="fp_def")
        expected = _lineage_hash("fp_abc", "fp_def", "SPRINT-002")
        assert e2["lineage_hash"] == expected

    def test_governance_flags_correct(self):
        entry = _genesis_entry()
        gov = entry["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["autonomous_execution_allowed"] is False
        assert gov["gate_self_approval_allowed"] is False
        assert gov["dry_run_only"] is True

    def test_entry_id_is_hex(self):
        entry = _genesis_entry()
        int(entry["entry_id"], 16)

    def test_created_date_is_date_string(self):
        import re
        entry = _genesis_entry()
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", entry["created_date"])

    def test_determinism_same_inputs(self):
        e1 = _genesis_entry()
        e2 = _genesis_entry()
        assert e1["lineage_hash"] == e2["lineage_hash"]
        assert e1["entry_id"] == e2["entry_id"]

    def test_cross_format_different_entry_ids(self):
        ef = _genesis_entry(fmt="fods")
        et = _genesis_entry(fmt="fodt")
        assert ef["entry_id"] != et["entry_id"]


# ---------------------------------------------------------------------------
# validate_lineage_chain
# ---------------------------------------------------------------------------

class TestValidateLineageChain:
    def test_empty_chain_is_consistent(self):
        result = validate_lineage_chain([])
        assert result["status"] == LINEAGE_EMPTY
        assert result["is_consistent"] is True
        assert result["entry_count"] == 0

    def test_single_genesis_is_valid(self):
        gen = _genesis_entry()
        result = validate_lineage_chain([gen])
        assert result["status"] == LINEAGE_GENESIS
        assert result["is_consistent"] is True

    def test_single_non_genesis_is_broken(self):
        entry = {
            "entry_id": "abc", "format_id": "fods", "sprint_id": "S1",
            "fingerprint": "fp1", "prior_fingerprint": "fp0",
            "prior_lineage_hash": "lh0", "lineage_hash": "lh1",
            "entry_index": 0, "is_genesis": False, "created_date": "2026-05-14",
        }
        result = validate_lineage_chain([entry])
        assert result["status"] == LINEAGE_CHAIN_BROKEN
        assert result["is_consistent"] is False

    def test_valid_two_entry_chain(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        result = validate_lineage_chain([gen, e2])
        assert result["status"] == LINEAGE_CONSISTENT
        assert result["is_consistent"] is True
        assert result["violations"] == []

    def test_valid_three_entry_chain(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e3 = build_lineage_entry("fods", "SPRINT-003", "fp_ghi789", prior_entry=e2)
        result = validate_lineage_chain([gen, e2, e3])
        assert result["status"] == LINEAGE_CONSISTENT
        assert result["is_consistent"] is True

    def test_broken_prior_fingerprint(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e2["prior_fingerprint"] = "TAMPERED"
        result = validate_lineage_chain([gen, e2])
        assert result["status"] == LINEAGE_CHAIN_BROKEN
        assert any("prior_fingerprint" in v for v in result["violations"])

    def test_broken_prior_lineage_hash(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e2["prior_lineage_hash"] = "TAMPERED"
        result = validate_lineage_chain([gen, e2])
        assert result["status"] == LINEAGE_CHAIN_BROKEN

    def test_broken_lineage_hash_detected(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e2["lineage_hash"] = "TAMPERED_HASH"
        result = validate_lineage_chain([gen, e2])
        assert result["status"] == LINEAGE_CHAIN_BROKEN
        assert any("lineage_hash mismatch" in v for v in result["violations"])

    def test_wrong_entry_index_detected(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e2["entry_index"] = 99  # wrong
        result = validate_lineage_chain([gen, e2])
        assert result["status"] == LINEAGE_CHAIN_BROKEN

    def test_non_genesis_marked_as_genesis_detected(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        e2["is_genesis"] = True  # wrong
        result = validate_lineage_chain([gen, e2])
        assert result["status"] == LINEAGE_CHAIN_BROKEN

    def test_entry_count_correct(self):
        gen = _genesis_entry()
        e2 = _second_entry(gen)
        result = validate_lineage_chain([gen, e2])
        assert result["entry_count"] == 2


# ---------------------------------------------------------------------------
# detect_fingerprint_drift
# ---------------------------------------------------------------------------

class TestDetectFingerprintDrift:
    def test_no_prior_is_genesis(self):
        result = detect_fingerprint_drift("fods", "fp_new", [])
        assert result["drift_detected"] is False
        assert result["drift_status"] == LINEAGE_GENESIS

    def test_matching_fingerprint_no_drift(self):
        gen = _genesis_entry(fingerprint="fp_same")
        result = detect_fingerprint_drift("fods", "fp_same", [gen])
        assert result["drift_detected"] is False
        assert result["drift_status"] == LINEAGE_CONSISTENT

    def test_different_fingerprint_drift_detected(self):
        gen = _genesis_entry(fingerprint="fp_old")
        result = detect_fingerprint_drift("fods", "fp_new", [gen])
        assert result["drift_detected"] is True
        assert result["drift_status"] == LINEAGE_MISMATCH

    def test_prior_fingerprint_in_result(self):
        gen = _genesis_entry(fingerprint="fp_old")
        result = detect_fingerprint_drift("fods", "fp_new", [gen])
        assert result["prior_fingerprint"] == "fp_old"
        assert result["current_fingerprint"] == "fp_new"

    def test_explanation_non_empty(self):
        result = detect_fingerprint_drift("fods", "fp_new", [])
        assert len(result["explanation"]) > 0

    def test_drift_explanation_mentions_human_review(self):
        gen = _genesis_entry(fingerprint="fp_old")
        result = detect_fingerprint_drift("fods", "fp_new", [gen])
        assert "human" in result["explanation"].lower() or "review" in result["explanation"].lower()

    def test_last_entry_is_used_for_comparison(self):
        gen = _genesis_entry(fingerprint="fp_gen")
        e2 = _second_entry(gen, fingerprint="fp_last")
        # current matches last entry, not genesis
        result = detect_fingerprint_drift("fods", "fp_last", [gen, e2])
        assert result["drift_detected"] is False

    def test_format_id_in_result(self):
        result = detect_fingerprint_drift("fods", "fp_new", [])
        assert result["format_id"] == "fods"


# ---------------------------------------------------------------------------
# build_live_lineage_entry (smoke test)
# ---------------------------------------------------------------------------

class TestBuildLiveLineageEntry:
    def test_returns_dict(self):
        result = build_live_lineage_entry("fods", "CONWAY-R9-TEST")
        assert isinstance(result, dict)

    def test_format_id_correct(self):
        result = build_live_lineage_entry("fods", "CONWAY-R9-TEST")
        if "error" not in result:
            assert result["format_id"] == "fods"

    def test_sprint_id_recorded(self):
        result = build_live_lineage_entry("fods", "CONWAY-R9-TEST")
        assert result["sprint_id"] == "CONWAY-R9-TEST"

    def test_genesis_when_no_prior(self):
        result = build_live_lineage_entry("fods", "CONWAY-R9-TEST")
        if "error" not in result:
            assert result["is_genesis"] is True
            assert result["entry_index"] == 0

    def test_governance_flags_present(self):
        result = build_live_lineage_entry("fods", "CONWAY-R9-TEST")
        if "error" not in result:
            gov = result["governance"]
            assert gov["commercial_product_ready"] is False
            assert gov["autonomous_execution_allowed"] is False

    def test_fods_and_fodt_different_entry_ids(self):
        r_fods = build_live_lineage_entry("fods", "CONWAY-R9-TEST")
        r_fodt = build_live_lineage_entry("fodt", "CONWAY-R9-TEST")
        if "error" not in r_fods and "error" not in r_fodt:
            assert r_fods["entry_id"] != r_fodt["entry_id"]


# ---------------------------------------------------------------------------
# Full chain integrity (integration)
# ---------------------------------------------------------------------------

class TestChainIntegrity:
    def test_chain_validates_after_three_entries(self):
        e0 = build_lineage_entry("fods", "S1", "fp_001")
        e1 = build_lineage_entry("fods", "S2", "fp_002", prior_entry=e0)
        e2 = build_lineage_entry("fods", "S3", "fp_003", prior_entry=e1)
        result = validate_lineage_chain([e0, e1, e2])
        assert result["is_consistent"] is True

    def test_tampered_middle_entry_breaks_chain(self):
        e0 = build_lineage_entry("fods", "S1", "fp_001")
        e1 = build_lineage_entry("fods", "S2", "fp_002", prior_entry=e0)
        e2 = build_lineage_entry("fods", "S3", "fp_003", prior_entry=e1)
        e1["fingerprint"] = "TAMPERED"  # tamper middle
        result = validate_lineage_chain([e0, e1, e2])
        assert result["is_consistent"] is False

    def test_cross_format_chains_independent(self):
        """FODS and FODT lineage chains must be independently valid."""
        fods_0 = build_lineage_entry("fods", "S1", "fp_fods_001")
        fods_1 = build_lineage_entry("fods", "S2", "fp_fods_002", prior_entry=fods_0)
        fodt_0 = build_lineage_entry("fodt", "S1", "fp_fodt_001")
        fodt_1 = build_lineage_entry("fodt", "S2", "fp_fodt_002", prior_entry=fodt_0)

        r_fods = validate_lineage_chain([fods_0, fods_1])
        r_fodt = validate_lineage_chain([fodt_0, fodt_1])

        assert r_fods["is_consistent"] is True
        assert r_fodt["is_consistent"] is True
        # Cross-isolation: FODS lineage hashes != FODT
        assert fods_0["lineage_hash"] != fodt_0["lineage_hash"]
