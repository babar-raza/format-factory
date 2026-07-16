"""Tests for mtlx_to_csv dogfood export (TC-S6P4-PROD-007, select-6 Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format" / "mtlx" / "valid"

from mtlx.mtlx_to_csv import mtlx_to_csv


class TestMtlxToCsv:
    def test_returns_data_row_count(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = mtlx_to_csv(SAMPLES / "multi-material.mtlx", dest)
        assert count >= 2

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.csv"
        mtlx_to_csv(SAMPLES / "multi-material.mtlx", dest)
        assert dest.exists()

    def test_header_and_material_names_present(self, tmp_path):
        dest = tmp_path / "out.csv"
        mtlx_to_csv(SAMPLES / "multi-material.mtlx", dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("name,type,shader_nodename")
        assert "metal" in content
        assert "plastic" in content
        assert "surfacematerial" in content

    def test_simple_material_single_row(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = mtlx_to_csv(SAMPLES / "simple-material.mtlx", dest)
        assert count == 1

    def test_node_graph_sample_no_crash(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = mtlx_to_csv(SAMPLES / "node-graph.mtlx", dest)
        assert count >= 0
        assert dest.exists()
