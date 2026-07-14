"""Inject-and-verify behavioral tests for certification tools.

TC-004 (precious-wandering-lighthouse, 2026-07-13):
Proves tools detect real problems, not just "zero findings on clean source."
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "certification"))

import stub_detector as sd
import assertion_quality_scorer as aqs


FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "certification"


class TestStubDetectorCatchesStubs:
    """stub_detector.scan_path() detects material stubs in injected source."""

    def test_detects_pass_function(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sd, "REPO_ROOT", tmp_path)
        src = tmp_path / "stub_mod.py"
        src.write_text("def stub_fn(): pass\n")
        result = sd.scan_path(tmp_path)
        assert result["material_finding_count"] >= 1, (
            f"Expected >= 1 material finding for 'def stub_fn(): pass'; "
            f"got {result['material_finding_count']}"
        )

    def test_detects_raise_not_implemented(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sd, "REPO_ROOT", tmp_path)
        src = tmp_path / "stub_raise.py"
        src.write_text("def stub_fn():\n    raise NotImplementedError\n")
        result = sd.scan_path(tmp_path)
        assert result["material_finding_count"] >= 1, (
            f"Expected >= 1 material finding for raise NotImplementedError; "
            f"got {result['material_finding_count']}"
        )

    def test_clean_source_returns_zero(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sd, "REPO_ROOT", tmp_path)
        src = tmp_path / "real_mod.py"
        src.write_text("def real_fn():\n    return 42\n")
        result = sd.scan_path(tmp_path)
        assert result["material_finding_count"] == 0, (
            f"Expected 0 material findings for clean source; "
            f"got {result['material_finding_count']}"
        )

    def test_fixture_with_material_stub_detected(self):
        fixture_dir = FIXTURE_ROOT / "fixture-with-material-stub"
        result = sd.scan_path(fixture_dir)
        assert result["material_finding_count"] >= 1, (
            f"fixture-with-material-stub must produce >= 1 material finding; "
            f"got {result['material_finding_count']}"
        )


class TestAssertionScorerCatchesWeakAssertions:
    """assertion_quality_scorer detects assert True as weak (score 1)."""

    def test_detects_assert_true(self, tmp_path, monkeypatch):
        monkeypatch.setattr(aqs, "REPO_ROOT", tmp_path)
        test_file = tmp_path / "test_weak.py"
        test_file.write_text("def test_foo():\n    assert True\n")
        result = aqs.score_test_directory(tmp_path)
        assert result["weak_assertion_count"] >= 1, (
            f"Expected >= 1 weak assertion from 'assert True'; "
            f"got {result['weak_assertion_count']}"
        )

    def test_strong_assertions_not_weak(self, tmp_path, monkeypatch):
        monkeypatch.setattr(aqs, "REPO_ROOT", tmp_path)
        test_file = tmp_path / "test_strong.py"
        test_file.write_text("def test_foo():\n    assert result == 42\n")
        result = aqs.score_test_directory(tmp_path)
        assert result["weak_assertion_count"] == 0, (
            f"'assert result == 42' must not be counted as weak; "
            f"got {result['weak_assertion_count']}"
        )

    def test_fixture_with_weak_assertion_detected(self):
        fixture_dir = FIXTURE_ROOT / "fixture-with-weak-assertion"
        result = aqs.score_test_directory(fixture_dir)
        assert result["weak_assertion_count"] >= 1, (
            f"fixture-with-weak-assertion must produce >= 1 weak assertion; "
            f"got {result['weak_assertion_count']}"
        )


class TestCIGateBlocksOnRegression:
    """ci_certification_gate exits 1 when stub count exceeds baseline threshold."""

    def test_gate_exits_1_when_stubs_exceed_baseline(self, tmp_path, monkeypatch):
        import ci_certification_gate as cig

        # Baseline allows 0 material stubs
        baseline = {
            "locked_at": "2026-01-01T00:00:00Z",
            "formats": {
                "csv": {"max_material_stubs": 0, "max_weak_assertions": 0}
            },
        }
        baseline_path = tmp_path / "certification-baseline.json"
        baseline_path.write_text(json.dumps(baseline))

        # Create a stub-audit.json showing 1 material stub
        cert_dir = tmp_path / "reports" / "certification" / "csv"
        cert_dir.mkdir(parents=True)
        stub_report = {"material_finding_count": 1, "finding_count": 1, "stub_count": 1}
        (cert_dir / "stub-audit.json").write_text(json.dumps(stub_report))

        monkeypatch.setattr(cig, "BASELINE_PATH", baseline_path)
        monkeypatch.setattr(cig, "REPO_ROOT", tmp_path)

        result = cig.run_gate(strict=False)
        assert result == 1, (
            f"Gate must exit 1 when material_stubs=1 > allowed=0; got exit {result}"
        )

    def test_gate_exits_0_when_within_baseline(self, tmp_path, monkeypatch):
        import ci_certification_gate as cig

        baseline = {
            "locked_at": "2026-01-01T00:00:00Z",
            "formats": {
                "csv": {"max_material_stubs": 5, "max_weak_assertions": 5}
            },
        }
        baseline_path = tmp_path / "certification-baseline.json"
        baseline_path.write_text(json.dumps(baseline))

        cert_dir = tmp_path / "reports" / "certification" / "csv"
        cert_dir.mkdir(parents=True)
        stub_report = {"material_finding_count": 2, "finding_count": 2, "stub_count": 2}
        (cert_dir / "stub-audit.json").write_text(json.dumps(stub_report))

        monkeypatch.setattr(cig, "BASELINE_PATH", baseline_path)
        monkeypatch.setattr(cig, "REPO_ROOT", tmp_path)

        result = cig.run_gate(strict=False)
        assert result == 0, (
            f"Gate must exit 0 when material_stubs=2 <= allowed=5; got exit {result}"
        )
