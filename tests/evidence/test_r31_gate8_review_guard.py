"""R31 Gate 8 delegated expert review evidence guard tests.

Validates that Gate 8 approval evidence is consistent across security reports,
pack.yaml files, and the expert review report.
"""

import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

import pytest
import yaml


GATE8_FORMATS = ["ods", "odt", "qoi", "xcf", "dif", "ppm", "pgm", "pbm", "sylk"]
GATE10_FORMATS = ["ods", "odt", "qoi", "xcf", "dif", "ppm"]
EXPECTED_APPROVAL_METHOD = "delegated_expert_agent_review_requested_by_babar"


class TestGate8PackYamlConsistency:
    """Gate 8 entries in pack.yaml are consistent."""

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_gate8_entry_exists(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        assert "gate_8" in pack["stages"], f"{fmt} pack.yaml missing gate_8"

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_gate8_status_is_pass(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        assert pack["stages"]["gate_8"]["status"] == "pass"

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_gate8_approval_method(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        assert pack["stages"]["gate_8"]["approval_method"] == EXPECTED_APPROVAL_METHOD

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_gate8_commercial_product_ready_false(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        assert pack["stages"]["gate_8"]["commercial_product_ready"] is False

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_gate8_no_critical_findings(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        g8 = pack["stages"]["gate_8"]
        assert g8.get("findings_critical", 0) == 0
        assert g8.get("findings_high", 0) == 0


class TestGate8SecurityReports:
    """Security reports reflect delegated expert approval."""

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_security_report_exists(self, fmt):
        report_path = _root / "reports" / "security" / f"{fmt}.md"
        assert report_path.exists(), f"Missing security report for {fmt}"

    @pytest.mark.parametrize("fmt", GATE8_FORMATS)
    def test_security_report_has_approval(self, fmt):
        report_path = _root / "reports" / "security" / f"{fmt}.md"
        text = report_path.read_text(encoding="utf-8")
        assert "DELEGATED_EXPERT_APPROVED" in text, f"{fmt} report not marked approved"


class TestGate10Consistency:
    """Gate 10 entries exist for formats that passed Gate 8+9."""

    @pytest.mark.parametrize("fmt", GATE10_FORMATS)
    def test_gate10_entry_exists(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        assert "gate_10" in pack["stages"], f"{fmt} pack.yaml missing gate_10"

    @pytest.mark.parametrize("fmt", GATE10_FORMATS)
    def test_gate10_publication_not_authorized(self, fmt):
        pack_path = _root / "acquisition-packs" / fmt / "pack.yaml"
        with open(pack_path) as f:
            pack = yaml.safe_load(f)
        assert pack["stages"]["gate_10"]["publication_authorized"] is False


class TestExpertReviewReport:
    """The expert review report exists and covers all formats."""

    def test_report_exists(self):
        report = _root / "reports" / "r31" / "delegated-gate8-expert-review-20260519.md"
        assert report.exists()

    def test_report_covers_all_original_formats(self):
        report = _root / "reports" / "r31" / "delegated-gate8-expert-review-20260519.md"
        text = report.read_text(encoding="utf-8")
        for fmt in ["ODS", "ODT", "QOI", "XCF", "DIF", "PPM"]:
            assert f"## {fmt}" in text, f"Report missing section for {fmt}"

    def test_report_all_approved(self):
        report = _root / "reports" / "r31" / "delegated-gate8-expert-review-20260519.md"
        text = report.read_text(encoding="utf-8")
        assert text.count("GATE8_DELEGATED_EXPERT_APPROVED") >= 6
