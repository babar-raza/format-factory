"""TC-S6P4-SYS-001 (select-6 Phase 4): V227 gate9 mechanical enforcement.

Closes SF1: implementation_authorized=true must be backed by a real,
gate_9_eligible coverage report. Pre-Phase-3 formats are grandfathered via
registry/gate9-coverage-baseline.yaml so the rule applies going forward only.
"""
from __future__ import annotations

import json

import pytest
import yaml

from governance_validators_gate9 import (
    validate_gate9_implementation_authorization_linkage as v227,
)


def _write_registry(tmp_path, formats):
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    (reg_dir / "format-registry.yaml").write_text(
        yaml.safe_dump({"formats": formats}), encoding="utf-8")
    return reg_dir


def _write_baseline(tmp_path, grandfathered_ids):
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    (reg_dir / "gate9-coverage-baseline.yaml").write_text(
        yaml.safe_dump({"grandfathered_pre_phase3":
                        [{"format_id": f} for f in grandfathered_ids]}),
        encoding="utf-8")


def _write_coverage(tmp_path, fmt, gate_9_eligible):
    cov_dir = tmp_path / "reports" / "spec-coverage"
    cov_dir.mkdir(parents=True, exist_ok=True)
    (cov_dir / f"{fmt}-coverage-report.json").write_text(
        json.dumps({"format_id": fmt, "gate_9_eligible": gate_9_eligible}),
        encoding="utf-8")


class TestV227:
    def test_no_authorized_formats_passes(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "x", "implementation_authorized": False}])
        r = v227({}, tmp_path)
        assert r["result"] == "PASS"
        assert r["blocks_sprint"] is False

    def test_grandfathered_format_skipped_even_without_report(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "zst", "implementation_authorized": True}])
        _write_baseline(tmp_path, ["zst"])
        r = v227({}, tmp_path)
        assert r["result"] == "PASS"

    def test_non_grandfathered_authorized_without_report_fails(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "newfmt", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        r = v227({}, tmp_path)
        assert r["result"] == "FAIL"
        assert r["blocks_sprint"] is True
        assert "newfmt" in r["summary"]

    def test_authorized_with_ineligible_report_fails(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "newfmt", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        _write_coverage(tmp_path, "newfmt", gate_9_eligible=False)
        r = v227({}, tmp_path)
        assert r["result"] == "FAIL"
        assert "gate_9_eligible is not true" in r["summary"]

    def test_authorized_with_eligible_report_passes(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "newfmt", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        _write_coverage(tmp_path, "newfmt", gate_9_eligible=True)
        r = v227({}, tmp_path)
        assert r["result"] == "PASS"
        assert r["blocks_sprint"] is False

    def test_live_repo_passes(self):
        """Regression proof against the real repo: all 7 currently authorized
        formats (zst/fodp/fodg/gnumeric/abw/ndjson/toml) predate the coverage
        gate and are grandfathered; V227 must not retroactively block them."""
        from pathlib import Path
        repo = Path(__file__).resolve().parents[2]
        r = v227({}, repo)
        assert r["result"] == "PASS", r["summary"]
