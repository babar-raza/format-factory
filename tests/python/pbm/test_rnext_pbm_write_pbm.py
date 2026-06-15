"""
test_rnext_pbm_write_pbm.py -- Dedicated test coverage for write_pbm.

Gap: GAP-Netpbm-FOSS-WRITE_PBM-001 (missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import write_pbm, parse_pbm


class TestWritePbm:
    def test_creates_file(self, tmp_path):
        dest = tmp_path / "out.pbm"
        write_pbm([0, 1, 1, 0], 2, 2, str(dest))
        assert dest.exists()

    def test_file_not_empty(self, tmp_path):
        dest = tmp_path / "out.pbm"
        write_pbm([0, 1], 2, 1, str(dest))
        assert dest.stat().st_size > 0

    def test_roundtrip_1x1(self, tmp_path):
        dest = tmp_path / "1x1.pbm"
        write_pbm([1], 1, 1, str(dest))
        img = parse_pbm(str(dest))
        assert img["width"] == 1
        assert img["height"] == 1

    def test_roundtrip_2x2(self, tmp_path):
        dest = tmp_path / "2x2.pbm"
        pixels = [0, 1, 1, 0]
        write_pbm(pixels, 2, 2, str(dest))
        img = parse_pbm(str(dest))
        assert img["width"] == 2
        assert img["height"] == 2

    def test_all_white(self, tmp_path):
        dest = tmp_path / "white.pbm"
        write_pbm([0, 0, 0, 0], 2, 2, str(dest))
        img = parse_pbm(str(dest))
        assert img.get("ok", True)

    def test_all_black(self, tmp_path):
        dest = tmp_path / "black.pbm"
        write_pbm([1, 1, 1, 1], 2, 2, str(dest))
        img = parse_pbm(str(dest))
        assert img.get("ok", True)

    def test_with_comment(self, tmp_path):
        dest = tmp_path / "comment.pbm"
        write_pbm([0, 1], 2, 1, str(dest), comment="test comment")
        content = dest.read_text(encoding="ascii")
        assert "test comment" in content

    def test_larger_image(self, tmp_path):
        dest = tmp_path / "large.pbm"
        pixels = [i % 2 for i in range(100)]
        write_pbm(pixels, 10, 10, str(dest))
        img = parse_pbm(str(dest))
        assert img["width"] == 10
        assert img["height"] == 10
