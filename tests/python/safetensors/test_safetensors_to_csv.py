"""Tests for safetensors_to_csv dogfood export (TC-S6P4-PROD-007, select-6 Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format" / "safetensors" / "valid"

from safetensors.safetensors_to_csv import safetensors_to_csv


class TestSafetensorsToCsv:
    def test_returns_data_row_count(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = safetensors_to_csv(SAMPLES / "multi-tensor.safetensors", dest)
        assert count == 2

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.csv"
        safetensors_to_csv(SAMPLES / "multi-tensor.safetensors", dest)
        assert dest.exists()

    def test_header_and_tensor_names_present(self, tmp_path):
        dest = tmp_path / "out.csv"
        safetensors_to_csv(SAMPLES / "multi-tensor.safetensors", dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("name,dtype,shape,byte_size")
        assert "alpha" in content
        assert "beta" in content

    def test_byte_size_matches_offset_delta(self, tmp_path):
        dest = tmp_path / "out.csv"
        safetensors_to_csv(SAMPLES / "single-tensor.safetensors", dest)
        content = dest.read_text(encoding="utf-8")
        rows = content.strip().splitlines()[1:]
        assert len(rows) == 1
        _name, _dtype, _shape, byte_size = rows[0].split(",")
        assert int(byte_size) > 0

    def test_single_tensor_file(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = safetensors_to_csv(SAMPLES / "single-tensor.safetensors", dest)
        assert count == 1
