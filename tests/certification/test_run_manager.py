"""Tests for run_manager.py — atomic certification run concept.

TC-002 (precious-wandering-lighthouse, 2026-07-13)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "certification"))

import run_manager as rm


class TestGenerateRunId:
    """generate_run_id() produces unique IDs per call."""

    def test_produces_string(self):
        rid = rm.generate_run_id()
        assert isinstance(rid, str)

    def test_starts_with_cert_run_prefix(self):
        rid = rm.generate_run_id()
        assert rid.startswith("cert-run-")

    def test_two_calls_produce_different_ids(self):
        rid1 = rm.generate_run_id()
        rid2 = rm.generate_run_id()
        assert rid1 != rid2


class TestWriteRunManifest:
    """write_run_manifest writes correct JSON to expected path."""

    def test_writes_json_to_expected_path(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rm, "_RUNS_ROOT", tmp_path / "runs")
        rid = "cert-run-test-001"
        dest = rm.write_run_manifest(
            run_id=rid,
            format_id="csv",
            source_revision="abc123",
            tools_run=["stub_detector"],
            reports_written=["reports/certification/csv/stub-audit.json"],
        )
        assert dest.exists()
        data = json.loads(dest.read_text())
        assert data["run_id"] == rid
        assert data["format_id"] == "csv"
        assert data["source_revision"] == "abc123"
        assert "stub_detector" in data["tools_run"]
        assert data["is_synthetic"] is False

    def test_creates_parent_directories(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rm, "_RUNS_ROOT", tmp_path / "deep" / "nested" / "runs")
        dest = rm.write_run_manifest("rid", "fods", "rev", [], [])
        assert dest.exists()


class TestGetLatestRunManifest:
    """get_latest_run_manifest returns correct result in various states."""

    def test_returns_none_when_no_runs_exist(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rm, "_RUNS_ROOT", tmp_path / "empty")
        result = rm.get_latest_run_manifest("csv")
        assert result is None

    def test_returns_none_when_runs_dir_absent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rm, "_RUNS_ROOT", tmp_path / "nonexistent")
        assert rm.get_latest_run_manifest("csv") is None

    def test_returns_most_recent_complete_run(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rm, "_RUNS_ROOT", tmp_path / "runs")
        monkeypatch.setattr(rm, "_REPO_ROOT", tmp_path)

        # Create an evidence file
        ev = tmp_path / "reports" / "certification" / "csv" / "stub-audit.json"
        ev.parent.mkdir(parents=True)
        ev.write_text("{}")

        # Write two manifests — second is more recent (sorts later)
        rm.write_run_manifest("cert-run-20260101T000000-aaa", "csv", "rev1", [], [])
        rm.write_run_manifest("cert-run-20260102T000000-bbb", "csv", "rev2", [],
                              ["reports/certification/csv/stub-audit.json"])

        result = rm.get_latest_run_manifest("csv")
        assert result is not None
        assert result["run_id"] == "cert-run-20260102T000000-bbb"


class TestCreateSyntheticInitialManifest:
    """create_synthetic_initial_manifest groups existing reports correctly."""

    def test_creates_synthetic_manifest(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rm, "_RUNS_ROOT", tmp_path / "runs")
        monkeypatch.setattr(rm, "_CERT_ROOT", tmp_path / "cert")

        # Create a fake report
        fmt_dir = tmp_path / "cert" / "csv"
        fmt_dir.mkdir(parents=True)
        (fmt_dir / "stub-audit.json").write_text("{}")

        dest = rm.create_synthetic_initial_manifest("csv")
        assert dest.exists()
        data = json.loads(dest.read_text())
        assert data["is_synthetic"] is True
        assert data["source_revision"] == "pre-run-model"
        assert any("stub-audit.json" in r for r in data["reports_written"])
