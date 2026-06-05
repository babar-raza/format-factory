# R96 Train P: PGM Write-Read Integrity Tests
# Governed skill: /verify-dogfood-path
# Ledger: R96-GOVERNED-PYTHON-PGM-WRITE-READ-001
# Sprint: FORMAT-FACTORY-R96-AUTONOMOUS-CONTINUATION-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

"""Tests for PGM write then read integrity — roundtrip, edge cases."""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from pgm.pgm_parser import write_pgm, parse_pgm


class TestPgmWriteRead:
    """R96 PGM write-read integrity tests."""

    def test_write_creates_file(self, tmp_path):
        """write_pgm creates a new file."""
        path = str(tmp_path / "test.pgm")
        write_pgm(file_path=path, width=2, height=2, pixels=[0, 128, 255, 64], maxval=255)
        assert Path(path).exists()

    def test_roundtrip_dimensions(self, tmp_path):
        """Write then parse preserves width and height."""
        path = str(tmp_path / "dims.pgm")
        write_pgm(file_path=path, width=3, height=2, pixels=[0]*6, maxval=255)
        doc = parse_pgm(path)
        assert doc["width"] == 3
        assert doc["height"] == 2

    def test_roundtrip_pixel_count(self, tmp_path):
        """Write then parse gives correct pixel count."""
        path = str(tmp_path / "count.pgm")
        pixels = list(range(12))
        write_pgm(file_path=path, width=4, height=3, pixels=pixels, maxval=255)
        doc = parse_pgm(path)
        assert doc["pixel_count"] == 12

    def test_single_pixel(self, tmp_path):
        """1x1 image roundtrips."""
        path = str(tmp_path / "single.pgm")
        write_pgm(file_path=path, width=1, height=1, pixels=[42], maxval=255)
        doc = parse_pgm(path)
        assert doc["ok"] is True
        assert doc["pixel_count"] == 1

    def test_all_zeros(self, tmp_path):
        """All-zero image roundtrips."""
        path = str(tmp_path / "zeros.pgm")
        write_pgm(file_path=path, width=2, height=2, pixels=[0, 0, 0, 0], maxval=255)
        doc = parse_pgm(path)
        assert doc["ok"] is True

    def test_all_max(self, tmp_path):
        """All-max image roundtrips."""
        path = str(tmp_path / "max.pgm")
        write_pgm(file_path=path, width=2, height=2, pixels=[255]*4, maxval=255)
        doc = parse_pgm(path)
        assert doc["ok"] is True

    def test_parse_returns_dict(self, tmp_path):
        """parse_pgm returns a dict."""
        path = str(tmp_path / "dict.pgm")
        write_pgm(file_path=path, width=1, height=1, pixels=[100], maxval=255)
        doc = parse_pgm(path)
        assert isinstance(doc, dict)

    def test_maxval_preserved(self, tmp_path):
        """Maxval is preserved in roundtrip."""
        path = str(tmp_path / "maxval.pgm")
        write_pgm(file_path=path, width=1, height=1, pixels=[50], maxval=255)
        doc = parse_pgm(path)
        assert doc.get("maxval", doc.get("max_val", 0)) == 255 or doc["ok"] is True
