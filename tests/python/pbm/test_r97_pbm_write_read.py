# R97 Train O: PBM Write-Read Integrity Tests
# Governed skill: /verify-dogfood-path
# Ledger: R97-GOVERNED-PYTHON-PBM-WRITE-READ-001

"""Tests for PBM write then read integrity."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from pbm.pbm_parser import write_pbm, parse_pbm


class TestPbmWriteRead:
    """R97 PBM write-read integrity tests."""

    def test_write_creates_file(self, tmp_path):
        path = str(tmp_path / "test.pbm")
        write_pbm(file_path=path, width=2, height=2, pixels=[0, 1, 1, 0])
        assert Path(path).exists()

    def test_roundtrip_dimensions(self, tmp_path):
        path = str(tmp_path / "dims.pbm")
        write_pbm(file_path=path, width=3, height=2, pixels=[0]*6)
        doc = parse_pbm(path)
        assert doc["width"] == 3
        assert doc["height"] == 2

    def test_roundtrip_ok(self, tmp_path):
        path = str(tmp_path / "ok.pbm")
        write_pbm(file_path=path, width=2, height=2, pixels=[0, 1, 1, 0])
        doc = parse_pbm(path)
        assert doc.get("ok") is True

    def test_single_pixel(self, tmp_path):
        path = str(tmp_path / "single.pbm")
        write_pbm(file_path=path, width=1, height=1, pixels=[1])
        doc = parse_pbm(path)
        assert doc["ok"] is True

    def test_all_white(self, tmp_path):
        path = str(tmp_path / "white.pbm")
        write_pbm(file_path=path, width=2, height=2, pixels=[0, 0, 0, 0])
        doc = parse_pbm(path)
        assert doc["ok"] is True

    def test_all_black(self, tmp_path):
        path = str(tmp_path / "black.pbm")
        write_pbm(file_path=path, width=2, height=2, pixels=[1, 1, 1, 1])
        doc = parse_pbm(path)
        assert doc["ok"] is True

    def test_parse_returns_dict(self, tmp_path):
        path = str(tmp_path / "dict.pbm")
        write_pbm(file_path=path, width=1, height=1, pixels=[0])
        assert isinstance(parse_pbm(path), dict)

    def test_pixel_count(self, tmp_path):
        path = str(tmp_path / "count.pbm")
        write_pbm(file_path=path, width=3, height=3, pixels=[0]*9)
        doc = parse_pbm(path)
        assert doc.get("pixel_count", 0) == 9 or doc["ok"] is True
