"""TC-S6P4-SYS-002 (select-6 Phase 4): hardened compute_feature_coverage.py.

Closes SF2: IMPLEMENTED status now requires a named, currently-passing test
cited in --confirmed, not a bare self-asserted feature_id. Covers the exact
failure class this audit found (D2/D3): a keyword match plus an unverified
"confirmed" claim used to be sufficient; it no longer is.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SAL_DIR = Path(__file__).resolve().parents[2] / "tools" / "specification-authority-layer"
if str(_SAL_DIR) not in sys.path:
    sys.path.insert(0, str(_SAL_DIR))

from compute_feature_coverage import (  # noqa: E402
    _classify_confirmed_entry,
    _test_id_exists,
    compute_coverage,
)


def _manifest(feature_ids):
    return {"features": [
        {"feature_id": fid, "name": fid, "requirement_level": "mandatory",
         "evidence_keywords": [fid.lower().replace("-", "_")]}
        for fid in feature_ids
    ]}


class TestClassifyConfirmedEntry:
    def test_legacy_bare_string_rejected(self):
        ok, note = _classify_confirmed_entry("F1", "F1", {}, skip_execution=False)
        assert ok is False
        assert "legacy" in note

    def test_legacy_bool_true_rejected(self):
        ok, note = _classify_confirmed_entry("F1", True, {}, skip_execution=False)
        assert ok is False

    def test_malformed_entry_rejected(self):
        ok, note = _classify_confirmed_entry("F1", {"not_test_ids": []}, {},
                                             skip_execution=False)
        assert ok is False
        assert "malformed" in note

    def test_passing_test_grants_implemented(self):
        entry = {"test_ids": ["tests/x.py::test_a"]}
        cache = {"tests/x.py::test_a": "PASS"}
        ok, note = _classify_confirmed_entry("F1", entry, cache, skip_execution=False)
        assert ok is True
        assert "verified by passing test" in note

    def test_failing_test_denies_implemented(self):
        entry = {"test_ids": ["tests/x.py::test_a"]}
        cache = {"tests/x.py::test_a": "FAIL"}
        ok, note = _classify_confirmed_entry("F1", entry, cache, skip_execution=False)
        assert ok is False
        assert "FAIL" in note

    def test_not_collected_test_denies_implemented(self):
        entry = {"test_ids": ["tests/x.py::test_ghost"]}
        cache = {}
        ok, note = _classify_confirmed_entry("F1", entry, cache, skip_execution=False)
        assert ok is False
        assert "NOT_COLLECTED" in note

    def test_one_of_multiple_failing_denies_implemented(self):
        entry = {"test_ids": ["tests/x.py::test_a", "tests/x.py::test_b"]}
        cache = {"tests/x.py::test_a": "PASS", "tests/x.py::test_b": "FAIL"}
        ok, _ = _classify_confirmed_entry("F1", entry, cache, skip_execution=False)
        assert ok is False

    def test_skip_execution_never_grants_implemented(self):
        entry = {"test_ids": ["tests/x.py::test_a"]}
        ok, note = _classify_confirmed_entry("F1", entry, {}, skip_execution=True)
        assert ok is False
        assert "skipped" in note


class TestTestIdExists:
    def test_real_function_found(self, tmp_path):
        f = tmp_path / "test_x.py"
        f.write_text("def test_real():\n    assert True\n", encoding="utf-8")
        import compute_feature_coverage as m
        old_root = m.REPO_ROOT
        m.REPO_ROOT = tmp_path
        try:
            assert _test_id_exists(f"{f.name}::test_real") is True
            assert _test_id_exists(f"{f.name}::test_ghost") is False
        finally:
            m.REPO_ROOT = old_root

    def test_class_method_found(self, tmp_path):
        f = tmp_path / "test_y.py"
        f.write_text("class TestC:\n    def test_m(self):\n        pass\n",
                     encoding="utf-8")
        import compute_feature_coverage as m
        old_root = m.REPO_ROOT
        m.REPO_ROOT = tmp_path
        try:
            assert _test_id_exists(f"{f.name}::TestC::test_m") is True
            assert _test_id_exists(f"{f.name}::TestC::test_ghost") is False
            assert _test_id_exists(f"{f.name}::TestGhost::test_m") is False
        finally:
            m.REPO_ROOT = old_root

    def test_missing_file_is_false(self):
        assert _test_id_exists("tests/does_not_exist.py::test_x") is False

    def test_malformed_id_is_false(self):
        assert _test_id_exists("no_double_colon_here") is False


class TestComputeCoverageIntegration:
    """End-to-end proof the v2 pipeline downgrades unverified claims and
    accepts real ones -- run against a scratch source tree, no repo mutation."""

    def test_legacy_confirmed_list_downgrades_to_partial(self, tmp_path, monkeypatch):
        import compute_feature_coverage as m
        monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
        src = tmp_path / "src" / "python" / "stub"
        src.mkdir(parents=True)
        (src / "codec.py").write_text(
            "def do_thing():\n    return 1\n", encoding="utf-8")
        manifest = {"features": [
            {"feature_id": "FACT-STUB-001", "name": "Does the thing",
             "requirement_level": "mandatory", "evidence_keywords": ["do_thing"]}]}
        # Legacy bare-list style: {"FACT-STUB-001": "FACT-STUB-001"} mirrors
        # what main() constructs from a JSON list.
        report = compute_coverage("stub", manifest,
                                  confirmed={"FACT-STUB-001": "FACT-STUB-001"},
                                  deferred_reasons={})
        assert report["items"][0]["status"] == "PARTIAL"
        assert report["gate_9_eligible"] is False
        assert "source_digest" in report and report["source_digest"]

    def test_missing_feature_has_no_evidence(self, tmp_path, monkeypatch):
        import compute_feature_coverage as m
        monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
        src = tmp_path / "src" / "python" / "stub"
        src.mkdir(parents=True)
        (src / "codec.py").write_text("x = 1\n", encoding="utf-8")
        manifest = {"features": [
            {"feature_id": "FACT-STUB-002", "name": "Never implemented",
             "requirement_level": "mandatory", "evidence_keywords": ["nonexistent_fn"]}]}
        report = compute_coverage("stub", manifest, confirmed={}, deferred_reasons={})
        assert report["items"][0]["status"] == "MISSING"

    def test_deferred_reason_makes_partial_eligible(self, tmp_path, monkeypatch):
        import compute_feature_coverage as m
        monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
        src = tmp_path / "src" / "python" / "stub"
        src.mkdir(parents=True)
        (src / "codec.py").write_text("def do_thing():\n    pass\n", encoding="utf-8")
        manifest = {"features": [
            {"feature_id": "FACT-STUB-003", "name": "Deferred thing",
             "requirement_level": "optional", "evidence_keywords": ["do_thing"]}]}
        report = compute_coverage("stub", manifest, confirmed={},
                                  deferred_reasons={"FACT-STUB-003": "out of scope"})
        assert report["items"][0]["status"] == "PARTIAL"
        assert report["gate_9_eligible"] is True


class TestRealRepoReplayProof:
    """The replay-fixture proof required by TC-S6P4-SYS-002: the hardened
    tool, run against a FROZEN snapshot of mtlx's pre-hardening LEGACY
    confirmed list (as it read before TC-S6P4-PROD-004 migrated
    reports/spec-coverage/mtlx-confirmed.json to the v2 test_ids schema),
    must downgrade its previously-IMPLEMENTED claims -- proving it would
    have caught D2/D3.

    TC-S6P4-FINAL-001d (select-6 Phase 4 final re-audit, 2026-07-16): the
    original version of this test read the LIVE mtlx-confirmed.json file.
    That file has since been legitimately migrated to the v2 schema by this
    very audit's own PROD-004 fix, which made the test's premise false and
    caused it to fail for the wrong reason (proof of a fix succeeding,
    misread as a regression). A replay proof must pin its input to a frozen
    snapshot of the PRE-fix state, not re-read live repo state that the fix
    itself legitimately changes -- otherwise the proof self-destructs the
    moment the very defect it was designed to catch gets fixed."""

    # Frozen 2026-07-15 snapshot: the legacy bare-list format
    # reports/spec-coverage/mtlx-confirmed.json used to hold, before
    # TC-S6P4-PROD-004 migrated it to the v2 {"test_ids": [...]} schema.
    _FROZEN_LEGACY_MTLX_CONFIRMED = [
        "FACT-MTLX-101",
        "FACT-MTLX-102",
        "FACT-MTLX-103",
        "FACT-MTLX-104",
        "FACT-MTLX-110",
    ]

    def test_mtlx_legacy_confirmed_no_longer_grants_implemented(self):
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        manifest = json.loads(
            (repo / "reports/spec-coverage/manifests/mtlx-feature-manifest.json")
            .read_text(encoding="utf-8"))
        confirmed = {fid: fid for fid in self._FROZEN_LEGACY_MTLX_CONFIRMED}
        report = compute_coverage("mtlx", manifest, confirmed, {})
        assert all(item["status"] != "IMPLEMENTED" for item in report["items"]), (
            "hardened tool must not grant IMPLEMENTED from a bare-list legacy claim")

    def test_mtlx_current_v2_confirmed_grants_implemented_with_real_tests(self):
        """Companion proof: the CURRENT (post-PROD-004) v2-schema
        mtlx-confirmed.json, which cites real passing test_ids, must still
        be able to grant IMPLEMENTED -- the hardened tool rejects bare
        claims, not all claims."""
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        confirmed_path = repo / "reports/spec-coverage/mtlx-confirmed.json"
        if not confirmed_path.exists():
            pytest.skip("mtlx-confirmed.json not present in this checkout")
        raw = json.loads(confirmed_path.read_text(encoding="utf-8"))
        if not (isinstance(raw, dict) and all(isinstance(v, dict) for v in raw.values())):
            pytest.skip("mtlx-confirmed.json is not in the v2 test_ids schema in this checkout")
        manifest = json.loads(
            (repo / "reports/spec-coverage/manifests/mtlx-feature-manifest.json")
            .read_text(encoding="utf-8"))
        report = compute_coverage("mtlx", manifest, raw, {})
        implemented = [i["feature_id"] for i in report["items"] if i["status"] == "IMPLEMENTED"]
        assert implemented, (
            "expected at least one real v2-schema entry to grant IMPLEMENTED via a genuinely "
            "passing cited test")
