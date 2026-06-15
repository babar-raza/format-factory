"""Tests for SAL-to-capability-compiler wiring.

Verifies that the capability compiler reads SAL spec facts and embeds
them in generated feature IRs and taskcards.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from capability_compiler import (
    compile_gap,
    compile_gap_to_feature_ir,
    compile_feature_ir_to_taskcard,
    load_sal_facts,
    reset_sal_cache,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SAL_OUTPUT = {
    "generated_at": "2026-06-14T00:00:00Z",
    "generator": "sal_master_runner.py v1.0",
    "formats_processed": 2,
    "spec_facts_total": 5,
    "results": [
        {
            "format_id": "FODS",
            "display_name": "Flat ODS",
            "spec_body": "OASIS",
            "spec_version": "1.3",
            "spec_url": "https://docs.oasis-open.org/office/",
            "spec_facts": [
                {"qname": "FODS-FACT-001", "section": "ODF 1.3 §3", "description": "Cell types", "authority": "ODF 1.3"},
                {"qname": "FODS-FACT-002", "section": "ODF 1.3 §4", "description": "Sheet structure", "authority": "ODF 1.3"},
                {"qname": "FODS-FACT-003", "section": "ODF 1.3 §5", "description": "Styles", "authority": "ODF 1.3"},
            ],
        },
        {
            "format_id": "CSV",
            "display_name": "CSV",
            "spec_body": "IETF",
            "spec_version": "RFC 4180",
            "spec_url": "https://tools.ietf.org/html/rfc4180",
            "spec_facts": [
                {"qname": "CSV-FACT-001", "section": "RFC 4180 §2.1", "description": "Header row", "authority": "RFC 4180"},
                {"qname": "CSV-FACT-002", "section": "RFC 4180 §2.4", "description": "Quoting", "authority": "RFC 4180"},
            ],
        },
    ],
}


@pytest.fixture(autouse=True)
def _reset_cache():
    reset_sal_cache()
    yield
    reset_sal_cache()


@pytest.fixture
def sal_file(tmp_path):
    p = tmp_path / "sal-facts-latest.json"
    p.write_text(json.dumps(SAMPLE_SAL_OUTPUT), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Tests: SAL loading
# ---------------------------------------------------------------------------

class TestLoadSalFacts:
    def test_loads_and_indexes_by_format(self, sal_file):
        facts = load_sal_facts(sal_file)
        assert "FODS" in facts
        assert "CSV" in facts

    def test_fods_has_three_facts(self, sal_file):
        facts = load_sal_facts(sal_file)
        assert len(facts["FODS"]) == 3

    def test_csv_has_two_facts(self, sal_file):
        facts = load_sal_facts(sal_file)
        assert len(facts["CSV"]) == 2

    def test_missing_file_returns_empty(self, tmp_path):
        facts = load_sal_facts(tmp_path / "nonexistent.json")
        assert facts == {}

    def test_corrupt_file_returns_empty(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("NOT JSON", encoding="utf-8")
        reset_sal_cache()
        facts = load_sal_facts(p)
        assert facts == {}

    def test_cache_returns_same_object(self, sal_file):
        f1 = load_sal_facts(sal_file)
        f2 = load_sal_facts(sal_file)
        assert f1 is f2


# ---------------------------------------------------------------------------
# Tests: Feature IR includes spec_qnames
# ---------------------------------------------------------------------------

class TestFeatureIRWithSAL:
    def test_fods_feature_ir_has_spec_qnames(self, sal_file, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", sal_file)
        gap = {"format_id": "FODS", "function_name": "fods_load"}
        ir = compile_gap_to_feature_ir(gap)
        assert "spec_qnames" in ir
        assert ir["spec_qnames"] == ["FODS-FACT-001", "FODS-FACT-002", "FODS-FACT-003"]

    def test_csv_feature_ir_has_spec_qnames(self, sal_file, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", sal_file)
        gap = {"format_id": "CSV", "function_name": "parse_csv"}
        ir = compile_gap_to_feature_ir(gap)
        assert ir["spec_qnames"] == ["CSV-FACT-001", "CSV-FACT-002"]
        assert ir["spec_facts_count"] == 2

    def test_unknown_format_empty_qnames(self, sal_file, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", sal_file)
        gap = {"format_id": "UNKNOWN_FMT", "function_name": "load"}
        ir = compile_gap_to_feature_ir(gap)
        assert ir["spec_qnames"] == []
        assert ir["spec_facts_count"] == 0


# ---------------------------------------------------------------------------
# Tests: Taskcard includes spec governance
# ---------------------------------------------------------------------------

class TestTaskcardWithSAL:
    def test_fods_taskcard_has_spec_qnames(self, sal_file, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", sal_file)
        gap = {"format_id": "FODS", "function_name": "fods_load"}
        result = compile_gap(gap)
        tc = result["taskcard"]
        gov = tc["governance_requirements"]
        assert gov["spec_qnames"] == ["FODS-FACT-001", "FODS-FACT-002", "FODS-FACT-003"]
        assert gov["exception_classification"] == "spec_authority_available"

    def test_unknown_format_exception_classification(self, sal_file, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", sal_file)
        gap = {"format_id": "UNKNOWN_FMT", "function_name": "load"}
        result = compile_gap(gap)
        tc = result["taskcard"]
        assert tc["governance_requirements"]["exception_classification"] == "no_public_spec_available"
        assert tc["governance_requirements"]["spec_qnames"] == []

    def test_csv_taskcard_spec_facts_count(self, sal_file, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", sal_file)
        gap = {"format_id": "CSV", "function_name": "csv_stats"}
        result = compile_gap(gap)
        tc = result["taskcard"]
        assert tc["governance_requirements"]["spec_facts_count"] == 2

    def test_no_sal_file_still_compiles(self, tmp_path, monkeypatch):
        monkeypatch.setattr("capability_compiler.SAL_OUTPUT_PATH", tmp_path / "nope.json")
        gap = {"format_id": "CSV", "function_name": "parse_csv"}
        result = compile_gap(gap)
        tc = result["taskcard"]
        assert tc["governance_requirements"]["exception_classification"] == "no_public_spec_available"
