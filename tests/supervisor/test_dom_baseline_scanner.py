"""Tests for dom_baseline_scanner.py — TC-DL2-007."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from dom_baseline_scanner import scan_format, generate_baseline


class TestDomBaselineScanner:

    def test_fods_has_nonempty_node_types(self):
        """FODS baseline has non-empty node_types and qname_count > 0."""
        baseline = scan_format("fods")
        assert "error" not in baseline
        assert len(baseline["node_types"]) > 0
        assert baseline["qname_count"] > 0

    def test_missing_format_handled(self):
        """Scanner handles missing format gracefully."""
        baseline = scan_format("nonexistent_xyz_format")
        assert "error" in baseline

    def test_generated_yaml_valid(self):
        """Generated YAML is valid and parseable."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
            path = Path(f.name)
        result_path = generate_baseline("fods", path)
        assert result_path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["format"] == "fods"
        assert isinstance(data["qname_count"], int)
        path.unlink(missing_ok=True)

    def test_all_full_formats_generate(self):
        """All 8 FULL-applicability formats produce baselines."""
        from dom_baseline_scanner import FULL_FORMATS
        for fmt in FULL_FORMATS:
            baseline = scan_format(fmt)
            assert "error" not in baseline, f"Failed for {fmt}: {baseline.get('error')}"
            assert baseline["qname_count"] >= 1, f"{fmt} has 0 spec_qname classes"
