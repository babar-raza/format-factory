"""TC-S6P4-SYS-005 (select-6 Phase 4): V230 coverage/registry drift detector.

Closes SF5: registry gate_9 bookkeeping was fully decoupled from coverage
report generation.
"""
from __future__ import annotations

import json

import yaml

from governance_validators_gate9_drift import validate_coverage_registry_drift as v230


def _write_report(tmp_path, fmt, source_digest):
    d = tmp_path / "reports" / "spec-coverage"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{fmt}-coverage-report.json").write_text(
        json.dumps({"format_id": fmt, "source_digest": source_digest,
                   "gate_9_eligible": True}),
        encoding="utf-8")


def _write_registry(tmp_path, formats):
    (tmp_path / "registry").mkdir(parents=True, exist_ok=True)
    (tmp_path / "registry" / "format-registry.yaml").write_text(
        yaml.safe_dump({"formats": formats}), encoding="utf-8")


class TestV230:
    def test_no_coverage_dir_passes(self, tmp_path):
        assert v230({}, tmp_path)["result"] == "PASS"

    def test_report_without_registry_gate9_block_warns(self, tmp_path):
        _write_report(tmp_path, "newfmt", "abc123")
        _write_registry(tmp_path, [{"format_id": "newfmt"}])
        r = v230({}, tmp_path)
        assert r["result"] == "WARN"
        assert r["blocks_sprint"] is False
        assert "newfmt" in r["summary"]

    def test_matching_digest_passes(self, tmp_path):
        _write_report(tmp_path, "newfmt", "abc123")
        _write_registry(tmp_path, [
            {"format_id": "newfmt",
             "gates": {"gate_9": {"coverage_source_digest": "abc123"}}}])
        assert v230({}, tmp_path)["result"] == "PASS"

    def test_mismatched_digest_fails(self, tmp_path):
        _write_report(tmp_path, "newfmt", "abc123-NEW")
        _write_registry(tmp_path, [
            {"format_id": "newfmt",
             "gates": {"gate_9": {"coverage_source_digest": "abc123-OLD"}}}])
        r = v230({}, tmp_path)
        assert r["result"] == "FAIL"
        assert r["blocks_sprint"] is True
        assert "STALE" in r["summary"]

    def test_report_without_source_digest_ignored(self, tmp_path):
        d = tmp_path / "reports" / "spec-coverage"
        d.mkdir(parents=True)
        (d / "legacy-coverage-report.json").write_text(
            json.dumps({"format_id": "legacy"}), encoding="utf-8")
        _write_registry(tmp_path, [{"format_id": "legacy"}])
        assert v230({}, tmp_path)["result"] == "PASS"

    def test_live_repo_no_stale_entries(self):
        """Regression proof: nothing in the real repo is STALE right now
        (WARN for un-bookkept formats is fine; FAIL would mean a real
        regression)."""
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        r = v230({}, repo)
        assert r["result"] in ("PASS", "WARN"), r["summary"]
