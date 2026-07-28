"""Tests for the capability queue consumer (system-healing lane).

Verifies the gap -> taskcard -> execution pipeline is live.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

import capability_queue_consumer
from capability_queue_consumer import (
    gap_to_compiler_input,
    compile_gaps_to_taskcards,
    load_foss_gaps,
    run_consumer,
)


# ---------------------------------------------------------------------------
# TC-EXT-002 remediation (2026-07-15, GAP-TCEXT002-01 / FI-017 / RC-FIO-005):
# capability_queue_consumer.py must resolve its compile_gap/compile_gap_to_feature_ir/
# compile_feature_ir_to_taskcard functions from tools/capability_layer/capability_compiler.py
# (L03's backward-compatible API, built specifically for this consumer per TC-CAP-011/TC-C8)
# — NOT tools/supervisor/capability_compiler.py (L14, a different, unrelated implementation
# that happens to define same-named functions). This used to depend on sys.path insertion
# order silently breaking this tie; it is now an explicit importlib load. This test pins the
# resolved module's identity so a future accidental regression (e.g. someone "cleaning up"
# the import back to a bare sys.path-order-dependent one, or repointing it at the wrong file)
# fails loudly here instead of silently producing the wrong Feature-IR/taskcard shape.
# ---------------------------------------------------------------------------

def test_capability_compiler_resolves_to_capability_layer_not_supervisor():
    resolved_path = Path(capability_queue_consumer._capability_layer_compiler.__file__).resolve()
    expected_path = (_REPO / "tools" / "capability_layer" / "capability_compiler.py").resolve()
    wrong_path = (_REPO / "tools" / "supervisor" / "capability_compiler.py").resolve()
    assert resolved_path == expected_path, (
        f"capability_queue_consumer must resolve capability_compiler functions from "
        f"{expected_path}, not {resolved_path}"
    )
    assert resolved_path != wrong_path


def test_compile_gap_to_feature_ir_matches_capability_layer_shape():
    """Confirms the resolved function is L03's backward-compatible API (expected_module
    shaped as src/python/{fmt}/{fmt}_codec.py), not L14's differently-shaped output."""
    gap = {"gap_id": "GAP-PINNING-001", "format": "CSV", "capability_name": "csv_row_count"}
    ir = capability_queue_consumer.compile_gap_to_feature_ir(
        capability_queue_consumer.gap_to_compiler_input(gap)
    )
    assert ir["expected_module"] == "src/python/csv/csv_codec.py"
    taskcard = capability_queue_consumer.compile_feature_ir_to_taskcard(ir)
    assert taskcard["required_skill"] == "add-python-api"


# ---------------------------------------------------------------------------
# Unit: gap_to_compiler_input
# ---------------------------------------------------------------------------

class TestGapToCompilerInput:
    def test_converts_format_and_capability(self):
        gap = {
            "gap_id": "GAP-CSV-FOSS-PROBE_CSV-001",
            "format": "CSV",
            "capability_name": "Probe CSV",
            "gap_type": "missing_test_coverage",
            "priority": "P0",
            "commercial_impact": "NONE",
        }
        result = gap_to_compiler_input(gap)
        assert result["format_id"] == "CSV"
        assert result["function_name"] == "probe_csv"
        assert "->" in result["expected_signature"]  # ASCII only, no Unicode arrows

    def test_normalizes_capability_name_to_snake_case(self):
        gap = {"format": "ZST", "capability_name": "File Info", "gap_type": "x"}
        result = gap_to_compiler_input(gap)
        assert result["function_name"] == "file_info"

    def test_preserves_gap_id(self):
        gap = {"gap_id": "GAP-TEST-001", "format": "CSV", "capability_name": "Load", "gap_type": "x"}
        result = gap_to_compiler_input(gap)
        assert result["gap_id"] == "GAP-TEST-001"

    def test_output_is_ascii_only(self):
        """Critical: no Unicode arrows or special chars in compiler input."""
        gap = {"format": "CSV", "capability_name": "Probe CSV", "gap_type": "x"}
        result = gap_to_compiler_input(gap)
        for key, val in result.items():
            for char in str(val):
                assert ord(char) < 128, f"Non-ASCII char {char!r} in {key}: {val!r}"


# ---------------------------------------------------------------------------
# Unit: compile_gaps_to_taskcards
# ---------------------------------------------------------------------------

class TestCompileGapsToTaskcards:
    def _make_gap(self, fmt: str, cap: str) -> dict:
        return {
            "gap_id": f"GAP-{fmt}-FOSS-{cap.upper()}-001",
            "format": fmt,
            "capability_name": cap,
            "gap_type": "missing_test_coverage",
            "priority": "P1",
            "commercial_impact": "NONE",
        }

    def test_compiles_single_gap(self, tmp_path):
        gaps = [self._make_gap("CSV", "probe csv")]
        results = compile_gaps_to_taskcards(gaps, tmp_path / "out")
        assert len(results) == 1
        assert results[0]["status"] == "compiled"

    def test_compiles_multiple_gaps(self, tmp_path):
        gaps = [
            self._make_gap("CSV", "probe csv"),
            self._make_gap("ZST", "file info"),
            self._make_gap("ABW", "word count"),
        ]
        results = compile_gaps_to_taskcards(gaps, tmp_path / "out")
        compiled = [r for r in results if r["status"] == "compiled"]
        assert len(compiled) == 3

    def test_writes_taskcard_json_files(self, tmp_path):
        gaps = [self._make_gap("CSV", "row count")]
        out_dir = tmp_path / "taskcards"
        compile_gaps_to_taskcards(gaps, out_dir)
        json_files = list(out_dir.glob("TC-*.json"))
        assert len(json_files) == 1
        # Verify the taskcard is valid JSON
        tc = json.loads(json_files[0].read_text(encoding="utf-8"))
        assert "taskcard_id" in tc
        assert "function_name" in tc

    def test_taskcard_has_source_gap_id(self, tmp_path):
        gap = {
            "gap_id": "GAP-DIF-FOSS-PROBE_DIF-001",
            "format": "DIF",
            "capability_name": "probe_dif",
            "gap_type": "missing_test_coverage",
            "priority": "P1",
            "commercial_impact": "NONE",
        }
        results = compile_gaps_to_taskcards([gap], tmp_path / "out")
        tc_path = Path(results[0]["taskcard_path"])
        tc = json.loads(tc_path.read_text(encoding="utf-8"))
        assert tc.get("source_gap_id") == "GAP-DIF-FOSS-PROBE_DIF-001"

    def test_taskcard_files_are_utf8(self, tmp_path):
        """Taskcard files must be valid UTF-8 (no encoding errors on write)."""
        gaps = [self._make_gap("CSV", "row count")]
        out_dir = tmp_path / "taskcards"
        compile_gaps_to_taskcards(gaps, out_dir)
        for tc_file in out_dir.glob("*.json"):
            # Should not raise
            content = tc_file.read_text(encoding="utf-8")
            json.loads(content)


# ---------------------------------------------------------------------------
# Integration: run_consumer
# ---------------------------------------------------------------------------

class TestRunConsumer:
    def test_compiles_gaps_from_real_ledger(self, tmp_path):
        """Integration test: consumer reads real gap ledger and compiles."""
        gap_ledger = _REPO / "reports" / "capability-layer" / "gap-ledger.json"
        if not gap_ledger.exists():
            pytest.skip("Gap ledger not found")

        summary = run_consumer(max_gaps=3, output_dir=tmp_path / "taskcards")
        assert summary["gaps_loaded"] >= 1, "Should load at least 1 gap from ledger"
        assert summary["gaps_compiled"] >= 1, "Should compile at least 1 taskcard"

    def test_consumer_writes_summary_file(self, tmp_path):
        gap_ledger = _REPO / "reports" / "capability-layer" / "gap-ledger.json"
        if not gap_ledger.exists():
            pytest.skip("Gap ledger not found")

        out_dir = tmp_path / "taskcards"
        run_consumer(max_gaps=2, output_dir=out_dir)
        summary_path = out_dir / "consumer-summary.json"
        assert summary_path.exists()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert "gaps_compiled" in summary
        assert "compiled_taskcards" in summary

    def test_consumer_does_not_compile_commercial_gaps(self, tmp_path):
        """Commercial gaps must be excluded (require Gate 11)."""
        gap_ledger = _REPO / "reports" / "capability-layer" / "gap-ledger.json"
        if not gap_ledger.exists():
            pytest.skip("Gap ledger not found")

        out_dir = tmp_path / "taskcards"
        summary = run_consumer(max_gaps=10, output_dir=out_dir)

        # All compiled taskcards must be from FOSS gaps
        for tc_info in summary.get("compiled_taskcards", []):
            tc_path = Path(tc_info["taskcard_path"])
            if tc_path.exists():
                tc = json.loads(tc_path.read_text(encoding="utf-8"))
                # Taskcard should not mention Gate 11 execution
                tc_str = json.dumps(tc).lower()
                assert "gate_11_approval" not in tc_str, (
                    f"Commercial/Gate11 taskcard found: {tc_path.name}"
                )
