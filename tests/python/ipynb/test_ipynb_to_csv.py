"""Tests for ipynb_to_csv dogfood export (TC-S6P4-PROD-007, select-6 Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format" / "ipynb" / "valid"

from ipynb.ipynb_to_csv import ipynb_to_csv


class TestIpynbToCsv:
    def test_returns_data_row_count(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = ipynb_to_csv(SAMPLES / "code-and-markdown.ipynb", dest)
        assert count == 2

    def test_output_file_created_and_nonempty(self, tmp_path):
        dest = tmp_path / "out.csv"
        ipynb_to_csv(SAMPLES / "code-and-markdown.ipynb", dest)
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_header_row_present(self, tmp_path):
        dest = tmp_path / "out.csv"
        ipynb_to_csv(SAMPLES / "minimal.ipynb", dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("index,cell_type,source_preview,output_count")

    def test_cell_types_and_content_reflected(self, tmp_path):
        dest = tmp_path / "out.csv"
        ipynb_to_csv(SAMPLES / "code-and-markdown.ipynb", dest)
        content = dest.read_text(encoding="utf-8")
        assert "markdown" in content
        assert "code" in content
        assert "Hello World" in content

    def test_output_count_reflects_real_outputs(self, tmp_path):
        dest = tmp_path / "out.csv"
        ipynb_to_csv(SAMPLES / "with-outputs.ipynb", dest)
        content = dest.read_text(encoding="utf-8")
        rows = content.strip().splitlines()[1:]
        assert any(int(r.split(",")[-1]) > 0 for r in rows)

    def test_no_header_option(self, tmp_path):
        dest = tmp_path / "out.csv"
        ipynb_to_csv(SAMPLES / "minimal.ipynb", dest, include_header=False)
        content = dest.read_text(encoding="utf-8")
        assert not content.startswith("index,cell_type")
