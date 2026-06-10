"""Unit tests for capability_map_generator.py core functions.

Sprint: FORMAT-FACTORY-CAPABILITY-LAYER-REPAIR-AND-HARDENING-001
Tests: _determine_state, _build_gap_ledger, _scan_python_functions,
       _discover_missing_foss_formats
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "capability_layer"))

from capability_map_generator import (
    _determine_state,
    _build_gap_ledger,
    _scan_python_functions,
)


# ---------------------------------------------------------------------------
# _determine_state tests
# ---------------------------------------------------------------------------

class TestDetermineState:

    def test_missing_function(self):
        state, reason, conf = _determine_state("load", False, [], 0, "gate_evidence")
        assert state == "missing"
        assert conf == 0.9

    def test_implemented_no_tests(self):
        state, reason, conf = _determine_state("load", True, [], 0, "gate_evidence")
        assert state == "implementation_verified"
        assert "no tests in directory" in reason.lower()
        assert conf == 0.4

    def test_implemented_unmatched_tests(self):
        """Function exists but no test file name contains the function name."""
        test_files = ["test_r120_abw_text_stats.py", "test_pfgi_abw_text_stats.py"]
        state, reason, conf = _determine_state("export_to_json", True, test_files, 0, "gate_evidence")
        assert state == "implementation_verified"
        assert "export_to_json" in reason
        assert conf == 0.5

    def test_implemented_matched_test(self):
        """Function name appears in test file name."""
        test_files = ["test_r122_tsv_write.py", "test_r125_tsv_load_tsv.py"]
        state, reason, conf = _determine_state("write", True, test_files, 0, "gate_evidence")
        assert state == "test_verified"
        assert "write" in reason.lower()

    def test_implemented_matched_test_with_examples(self):
        test_files = ["test_r122_tsv_write.py"]
        state, reason, conf = _determine_state("write", True, test_files, 3, "gate_evidence")
        assert state == "example_verified"

    def test_spec_fact_boosts_confidence(self):
        test_files = ["test_r125_fact_traceability.py"]
        state1, _, conf1 = _determine_state("fact", True, test_files, 0, "gate_evidence")
        state2, _, conf2 = _determine_state("fact", True, test_files, 0, "spec_fact")
        assert conf2 > conf1
        assert state1 == state2 == "test_verified"

    def test_case_insensitive_matching(self):
        """Function name matching is case-insensitive."""
        test_files = ["test_r126_GNUMERIC_SET_CELL.py"]
        state, _, _ = _determine_state("set_cell", True, test_files, 0, "gate_evidence")
        assert state == "test_verified"


# ---------------------------------------------------------------------------
# _build_gap_ledger tests
# ---------------------------------------------------------------------------

class TestBuildGapLedger:

    def _make_record(self, state: str, format_id: str = "TSV", op: str = "load"):
        return {
            "capability_id": f"{format_id}-FOSS-{op.upper()}-001",
            "format": format_id,
            "product_type": "foss_reduced",
            "capability_name": op.replace("_", " ").title(),
            "current_state": state,
            "operation_kind": op,
            "required_for_poc": False,
            "blocks_readiness": False,
            "expected_for_commercial": False,
            "expected_for_foss": True,
            "next_task_candidate": f"Implement {op}" if state == "missing" else "",
            "blockers": [],
            "notes": "",
        }

    def test_missing_creates_gap(self):
        records = [self._make_record("missing", op="export_html")]
        gaps = _build_gap_ledger(records)
        assert len(gaps) == 1
        assert gaps[0]["gap_type"] == "missing_implementation"

    def test_implementation_verified_creates_gap(self):
        records = [self._make_record("implementation_verified", op="export_json")]
        gaps = _build_gap_ledger(records)
        assert len(gaps) == 1
        assert gaps[0]["gap_type"] == "missing_test_coverage"

    def test_test_verified_no_gap(self):
        records = [self._make_record("test_verified", op="load")]
        gaps = _build_gap_ledger(records)
        assert len(gaps) == 0

    def test_example_verified_no_gap(self):
        records = [self._make_record("example_verified", op="load")]
        gaps = _build_gap_ledger(records)
        assert len(gaps) == 0

    def test_ai_draft_creates_stale_claim_gap(self):
        records = [self._make_record("ai_draft", op="fake_fn")]
        gaps = _build_gap_ledger(records)
        assert len(gaps) == 1
        assert gaps[0]["gap_type"] == "stale_claim"

    def test_gap_priority_blocks_readiness(self):
        rec = self._make_record("missing", op="load")
        rec["blocks_readiness"] = True
        gaps = _build_gap_ledger([rec])
        assert gaps[0]["priority"] == "P0"

    def test_gap_priority_required_for_poc(self):
        rec = self._make_record("missing", op="probe")
        rec["required_for_poc"] = True
        gaps = _build_gap_ledger([rec])
        assert gaps[0]["priority"] == "P1"

    def test_gap_priority_default(self):
        rec = self._make_record("missing", op="export_html")
        gaps = _build_gap_ledger([rec])
        assert gaps[0]["priority"] == "P2"


# ---------------------------------------------------------------------------
# _scan_python_functions tests
# ---------------------------------------------------------------------------

class TestScanPythonFunctions:

    def test_scan_empty_dir(self, tmp_path):
        assert _scan_python_functions(tmp_path) == []

    def test_scan_nonexistent_dir(self, tmp_path):
        assert _scan_python_functions(tmp_path / "nonexistent") == []

    def test_scan_from_all(self, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ["load", "write", "probe"]\n')
        fns = _scan_python_functions(tmp_path)
        assert fns == ["load", "write", "probe"]

    def test_scan_from_ast_fallback(self, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text("# no __all__\n")
        codec = tmp_path / "codec.py"
        codec.write_text("def load(data): pass\ndef _private(): pass\ndef write(data): pass\n")
        fns = _scan_python_functions(tmp_path)
        assert "load" in fns
        assert "write" in fns
        assert "_private" not in fns

    def test_scan_excludes_private(self, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text("")
        mod = tmp_path / "mod.py"
        mod.write_text("def public_fn(): pass\ndef _internal(): pass\n")
        fns = _scan_python_functions(tmp_path)
        assert "public_fn" in fns
        assert "_internal" not in fns

    def test_scan_deduplicates(self, tmp_path):
        init = tmp_path / "__init__.py"
        init.write_text("")
        a = tmp_path / "a.py"
        a.write_text("def load(): pass\n")
        b = tmp_path / "b.py"
        b.write_text("def load(): pass\n")
        fns = _scan_python_functions(tmp_path)
        assert fns.count("load") == 1
