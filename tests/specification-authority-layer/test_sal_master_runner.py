"""
test_sal_master_runner.py — Smoke tests for the SAL master runner.

REQ-SAL-001: sal_master_runner.py is executable and produces structured
spec-fact output per format with qname, section, description fields.
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from sal_master_runner import run_sal_pipeline, _load_format_registry, _spec_facts_for_format


class TestSALMasterRunnerBasic:
    def test_run_pipeline_returns_dict(self, tmp_path):
        result = run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        assert isinstance(result, dict)

    def test_run_pipeline_fods_has_results(self, tmp_path):
        result = run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        assert result["formats_processed"] >= 1

    def test_run_pipeline_fods_spec_facts_nonempty(self, tmp_path):
        result = run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        assert result["spec_facts_total"] >= 3, (
            f"Expected >= 3 spec facts for FODS, got {result['spec_facts_total']}"
        )

    def test_run_pipeline_fodt_spec_facts_nonempty(self, tmp_path):
        result = run_sal_pipeline(formats=["fodt"], output_dir=tmp_path)
        assert result["spec_facts_total"] >= 3

    def test_run_pipeline_zst_spec_facts_nonempty(self, tmp_path):
        result = run_sal_pipeline(formats=["zst"], output_dir=tmp_path)
        assert result["spec_facts_total"] >= 3

    def test_output_json_written_to_disk(self, tmp_path):
        run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        assert latest.exists(), "sal-facts-latest.json was not written"

    def test_output_json_is_valid_json(self, tmp_path):
        run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        assert "results" in data

    def test_output_contains_qname_field(self, tmp_path):
        run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        fods_result = next(
            r for r in data["results"] if r["format_id"] == "fods"
        )
        for fact in fods_result["spec_facts"]:
            assert "qname" in fact, f"Spec fact missing qname: {fact}"

    def test_output_contains_section_field(self, tmp_path):
        run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        fods_result = next(
            r for r in data["results"] if r["format_id"] == "fods"
        )
        for fact in fods_result["spec_facts"]:
            assert "section" in fact, f"Spec fact missing section: {fact}"

    def test_output_contains_description_field(self, tmp_path):
        run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        fods_result = next(
            r for r in data["results"] if r["format_id"] == "fods"
        )
        for fact in fods_result["spec_facts"]:
            assert "description" in fact, f"Spec fact missing description: {fact}"
            assert len(fact["description"]) > 10, "Description too short"


class TestSALMasterRunnerFormats:
    def test_all_formats_returns_multiple(self, tmp_path):
        result = run_sal_pipeline(output_dir=tmp_path)
        assert result["formats_processed"] >= 5, (
            f"Expected >= 5 formats, got {result['formats_processed']}"
        )

    def test_all_formats_total_facts_substantial(self, tmp_path):
        result = run_sal_pipeline(output_dir=tmp_path)
        assert result["spec_facts_total"] >= 20, (
            f"Expected >= 20 total facts across all formats, "
            f"got {result['spec_facts_total']}"
        )

    def test_fods_qnames_are_format_specific(self, tmp_path):
        result = run_sal_pipeline(formats=["fods"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        fods = next(r for r in data["results"] if r["format_id"] == "fods")
        qnames = [f["qname"] for f in fods["spec_facts"]]
        assert any("FODS" in q for q in qnames), (
            f"Expected FODS-specific QNames, got: {qnames}"
        )

    def test_fodt_qnames_are_format_specific(self, tmp_path):
        result = run_sal_pipeline(formats=["fodt"], output_dir=tmp_path)
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        fodt = next(r for r in data["results"] if r["format_id"] == "fodt")
        qnames = [f["qname"] for f in fodt["spec_facts"]]
        assert any("FODT" in q for q in qnames), (
            f"Expected FODT-specific QNames, got: {qnames}"
        )


class TestSALMasterRunnerRegistryLoad:
    def test_format_registry_loads(self):
        formats = _load_format_registry()
        assert len(formats) >= 5, f"Expected >= 5 formats, got {len(formats)}"

    def test_format_registry_has_fods(self):
        formats = _load_format_registry()
        fids = [f.get("format_id", "") for f in formats]
        assert "fods" in fids

    def test_spec_facts_for_unknown_format_returns_defaults(self):
        fake_fmt = {"format_id": "xxx", "spec_body": "", "spec_version": ""}
        facts = _spec_facts_for_format(fake_fmt)
        assert len(facts) >= 1
        assert all("qname" in f for f in facts)
