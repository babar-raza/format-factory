"""
test_r201_sal003_min_spec_facts_validator.py — Tests for validate_min_spec_facts_per_format (V19).

REQ-SAL-003: governance_validators.py has a per-format spec-fact count validator.
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators import validate_min_spec_facts_per_format


def _make_decl(items=None):
    return {
        "run_id": "test-sal003",
        "sprint_id": "TEST-SPRINT-SAL003",
        "planned_work_items": items or [],
    }


def _write_sal_output(tmp_path, formats_data):
    sal_dir = tmp_path / ".local" / "sal-output"
    sal_dir.mkdir(parents=True)
    sal_file = sal_dir / "sal-facts-latest.json"
    sal_file.write_text(json.dumps({"formats": formats_data}), encoding="utf-8")
    return sal_dir


class TestMinSpecFactsValidatorNoSALOutput:
    def test_pass_when_no_sal_output(self, tmp_path):
        result = validate_min_spec_facts_per_format(_make_decl(), repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_summary_mentions_skipping(self, tmp_path):
        result = validate_min_spec_facts_per_format(_make_decl(), repo_root=tmp_path)
        assert "skipping" in result["summary"].lower() or "not found" in result["summary"].lower()

    def test_never_blocks_sprint_when_no_sal(self, tmp_path):
        result = validate_min_spec_facts_per_format(_make_decl(), repo_root=tmp_path)
        assert result["blocks_sprint"] is False


class TestMinSpecFactsValidatorWithSALOutput:
    def test_pass_when_format_has_enough_facts(self, tmp_path):
        _write_sal_output(tmp_path, [
            {"format_id": "FODS", "spec_facts": [{"qname": f"FODS-FACT-{i:03d}"} for i in range(5)]},
        ])
        decl = _make_decl([{
            "item_id": "FODS-001",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": ["FODS-FACT-001"],
        }])
        result = validate_min_spec_facts_per_format(decl, repo_root=tmp_path, min_facts=3)
        assert result["result"] == "PASS"

    def test_fail_when_format_below_minimum(self, tmp_path):
        _write_sal_output(tmp_path, [
            {"format_id": "FODS", "spec_facts": [{"qname": "FODS-FACT-001"}]},
        ])
        decl = _make_decl([{
            "item_id": "FODS-001",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": ["FODS-FACT-001"],
        }])
        result = validate_min_spec_facts_per_format(decl, repo_root=tmp_path, min_facts=3)
        assert result["result"] == "FAIL"
        assert len(result["items"]) == 1
        assert result["items"][0]["spec_fact_count"] == 1

    def test_governance_doc_items_exempt(self, tmp_path):
        _write_sal_output(tmp_path, [
            {"format_id": "FODS", "spec_facts": [{"qname": "FODS-FACT-001"}]},
        ])
        decl = _make_decl([{
            "item_id": "FODS-001",
            "item_type": "GOVERNANCE_DOC",
            "spec_fact_refs": ["FODS-FACT-001"],
        }])
        result = validate_min_spec_facts_per_format(decl, repo_root=tmp_path, min_facts=3)
        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_unknown_format_skipped(self, tmp_path):
        # SAL has no entry for UNKNOWN format — item is silently skipped
        _write_sal_output(tmp_path, [
            {"format_id": "FODS", "spec_facts": [{"qname": "FODS-FACT-001"}]},
        ])
        decl = _make_decl([{
            "item_id": "UNKNOWN-001",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
        }])
        result = validate_min_spec_facts_per_format(decl, repo_root=tmp_path, min_facts=3)
        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_never_blocks_sprint(self, tmp_path):
        _write_sal_output(tmp_path, [
            {"format_id": "FODS", "spec_facts": [{"qname": "FODS-FACT-001"}]},
        ])
        decl = _make_decl([{
            "item_id": "FODS-001",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": ["FODS-FACT-001"],
        }])
        result = validate_min_spec_facts_per_format(decl, repo_root=tmp_path, min_facts=3)
        assert result["blocks_sprint"] is False

    def test_returns_required_keys(self, tmp_path):
        result = validate_min_spec_facts_per_format(_make_decl(), repo_root=tmp_path)
        assert "validator" in result
        assert "result" in result
        assert "summary" in result
        assert "blocks_sprint" in result

    def test_multiple_formats_partial_fail(self, tmp_path):
        _write_sal_output(tmp_path, [
            {"format_id": "FODS", "spec_facts": [{"qname": f"FODS-FACT-{i}"} for i in range(5)]},
            {"format_id": "FODT", "spec_facts": [{"qname": "FODT-FACT-001"}]},
        ])
        decl = _make_decl([
            {"item_id": "FODS-001", "item_type": "PRODUCT_SOURCE", "spec_fact_refs": ["FODS-FACT-001"]},
            {"item_id": "FODT-001", "item_type": "PRODUCT_SOURCE", "spec_fact_refs": ["FODT-FACT-001"]},
        ])
        result = validate_min_spec_facts_per_format(decl, repo_root=tmp_path, min_facts=3)
        assert result["result"] == "FAIL"
        fail_items = [i for i in result["items"] if i["result"] == "FAIL"]
        pass_items = [i for i in result["items"] if i["result"] == "PASS"]
        assert len(fail_items) == 1
        assert len(pass_items) == 1
        assert fail_items[0]["format"] == "FODT"
