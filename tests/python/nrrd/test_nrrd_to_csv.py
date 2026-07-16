"""Tests for nrrd_to_csv dogfood export (TC-S6P4-PROD-007, select-6 Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format" / "nrrd" / "valid"

from nrrd.nrrd_to_csv import nrrd_to_csv


class TestNrrdToCsv:
    def test_returns_data_row_count(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = nrrd_to_csv(SAMPLES / "2d-float32.nrrd", dest)
        assert count > 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.csv"
        nrrd_to_csv(SAMPLES / "2d-float32.nrrd", dest)
        assert dest.exists()

    def test_header_fields_present(self, tmp_path):
        dest = tmp_path / "out.csv"
        nrrd_to_csv(SAMPLES / "2d-float32.nrrd", dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("field,value,source")
        assert "type,float,header" in content
        assert "encoding,raw,header" in content

    def test_gzip_sample_exports_metadata(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = nrrd_to_csv(SAMPLES / "gzip-encoded.nrrd", dest)
        assert count > 0
        content = dest.read_text(encoding="utf-8")
        assert "gzip" in content or "gz" in content
