"""Fixture-based integrity tests for certification_dashboard.py.

TC-004 (precious-wandering-lighthouse, 2026-07-13):
Verifies that the dashboard produces correct verdicts for known fixture states.
Uses tests/fixtures/certification/ subdirectories as controlled inputs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "certification"))

import certification_dashboard as cd
import run_manager as rm


FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "certification"


def _write_synthetic_manifest(runs_root: Path, fmt: str, reports_written: list) -> None:
    manifest = {
        "run_id": "cert-initial-crispy-jingling-snail",
        "format_id": fmt,
        "started_at": "2026-07-13T00:00:00+00:00",
        "source_revision": "abc123",
        "tools_run": ["synthetic"],
        "reports_written": reports_written,
        "is_synthetic": True,
    }
    dest = runs_root / "cert-initial-crispy-jingling-snail" / f"{fmt}-manifest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2))


class TestDashboardIntegrity:
    """certification_dashboard produces correct verdicts for controlled fixture inputs."""

    def test_missing_oracle_produces_incomplete_evidence(self, tmp_path, monkeypatch):
        """fixture-missing-oracle (8 reports, no oracle-alignment.json) → INCOMPLETE_EVIDENCE."""
        fixture_dir = FIXTURE_ROOT / "fixture-missing-oracle"
        assert fixture_dir.exists(), f"Fixture directory must exist: {fixture_dir}"

        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "testfmt"
        fmt_dir.mkdir(parents=True)

        for src in fixture_dir.glob("*.json"):
            (fmt_dir / src.name).write_text(src.read_text())

        runs_root = cert_root / "runs"
        reports_written = [
            f"reports/certification/testfmt/{p.name}"
            for p in fmt_dir.glob("*.json")
        ]
        _write_synthetic_manifest(runs_root, "testfmt", reports_written)

        monkeypatch.setattr(cd, "CERT_ROOT", cert_root)
        monkeypatch.setattr(cd, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(rm, "_RUNS_ROOT", runs_root)
        monkeypatch.setattr(rm, "_REPO_ROOT", tmp_path)

        result = cd.collect_format_status("testfmt", use_run_manifest=True)
        oracle_status = result["dimensions"]["oracle"]["status"]
        verdict = result["overall_verdict"]

        assert oracle_status == "MISSING_EVIDENCE", (
            f"Oracle dimension must be MISSING_EVIDENCE when oracle-alignment.json absent; "
            f"got {oracle_status}"
        )
        assert verdict in ("INCOMPLETE_EVIDENCE", "NOT_CERTIFIED"), (
            f"Overall verdict must block CERTIFIED when oracle evidence missing; "
            f"got {verdict}"
        )

    def test_complete_evidence_produces_certified(self, tmp_path, monkeypatch):
        """fixture-complete-certified (9 reports, all PASS/NOT_APPLICABLE) → CERTIFIED."""
        fixture_dir = FIXTURE_ROOT / "fixture-complete-certified"
        assert fixture_dir.exists(), f"Fixture directory must exist: {fixture_dir}"

        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "testfmt"
        fmt_dir.mkdir(parents=True)

        for src in fixture_dir.glob("*.json"):
            (fmt_dir / src.name).write_text(src.read_text())

        runs_root = cert_root / "runs"
        reports_written = [
            f"reports/certification/testfmt/{p.name}"
            for p in fmt_dir.glob("*.json")
        ]
        _write_synthetic_manifest(runs_root, "testfmt", reports_written)

        monkeypatch.setattr(cd, "CERT_ROOT", cert_root)
        monkeypatch.setattr(cd, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(rm, "_RUNS_ROOT", runs_root)
        monkeypatch.setattr(rm, "_REPO_ROOT", tmp_path)

        result = cd.collect_format_status("testfmt", use_run_manifest=True)
        verdict = result["overall_verdict"]

        assert verdict == "CERTIFIED", (
            f"Complete evidence with all PASS/NOT_APPLICABLE must yield CERTIFIED; "
            f"got {verdict}. Dimensions: {result['dimensions']}"
        )

    def test_not_applicable_does_not_prevent_certified(self, tmp_path, monkeypatch):
        """CERT-DASHBOARD-001 regression: NOT_APPLICABLE must not trigger CERTIFIED_WITH_KNOWN_GAPS.

        A format with 8 PASS + 1 NOT_APPLICABLE must receive CERTIFIED, not
        CERTIFIED_WITH_KNOWN_GAPS. This was the original bug: NOT_APPLICABLE was only
        in the "acceptable" set, so it caused the CERTIFIED_WITH_KNOWN_GAPS branch to
        fire when combined with PASS statuses.
        """
        cert_root = tmp_path / "reports" / "certification"
        fmt_dir = cert_root / "testfmt"
        fmt_dir.mkdir(parents=True)

        dimension_reports = {
            "api-contract.json": {
                "python": {"contracts": [{"name": "load"}]},
                "dotnet": {"contracts": []},
                "source_revision": "abc123",
            },
            "traceability-audit.json": {
                "pass_count": 5,
                "qname_count": 5,
                "status": "PASS",
                "source_revision": "abc123",
            },
            "stub-audit.json": {
                "material_finding_count": 0,
                "finding_count": 0,
                "source_revision": "abc123",
            },
            "exception-audit.json": {
                "uncovered_exception_count": 0,
                "exception_count": 3,
                "source_revision": "abc123",
            },
            "oracle-alignment.json": {
                "status": "PASS",
                "pass_rate": "100%",
                "source_revision": "abc123",
            },
            "assertion-quality.json": {
                "overall_avg_score": 4.0,
                "weak_assertion_count": 0,
                "source_revision": "abc123",
            },
            "roundtrip-audit.json": {
                "status": "PASS",
                "source_revision": "abc123",
            },
            "package-proof.json": {
                "status": "PASS",
                "source_revision": "abc123",
            },
            "consumer-proof.json": {
                "status": "NOT_APPLICABLE",
                "source_revision": "abc123",
            },
        }

        for filename, data in dimension_reports.items():
            (fmt_dir / filename).write_text(json.dumps(data))

        runs_root = cert_root / "runs"
        reports_written = [
            f"reports/certification/testfmt/{name}"
            for name in dimension_reports
        ]
        _write_synthetic_manifest(runs_root, "testfmt", reports_written)

        monkeypatch.setattr(cd, "CERT_ROOT", cert_root)
        monkeypatch.setattr(cd, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(rm, "_RUNS_ROOT", runs_root)
        monkeypatch.setattr(rm, "_REPO_ROOT", tmp_path)

        result = cd.collect_format_status("testfmt", use_run_manifest=True)
        verdict = result["overall_verdict"]

        assert verdict == "CERTIFIED", (
            f"8 PASS + 1 NOT_APPLICABLE must yield CERTIFIED, not CERTIFIED_WITH_KNOWN_GAPS. "
            f"Got: {verdict}. This is the CERT-DASHBOARD-001 regression test."
        )
