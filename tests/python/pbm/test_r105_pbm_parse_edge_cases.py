# R105 Wave 3: PBM P1 parse edge cases — malformed headers, boundary conditions
# Lane E — Python Netpbm FOSS
# Ledger: R105-FOSS-PBM-PARSE-EDGE-CASES-001

import pytest
from pbm.pbm_parser import (
    parse_pbm,
    parse_pbm_strict,
    write_pbm,
    PbmError,
    PbmInvalidMagicError,
)


class TestP1ParseEdgeCases:
    """P1 (ASCII) parser edge cases."""

    def test_minimal_valid_p1(self, tmp_path):
        p = tmp_path / "min.pbm"
        p.write_text("P1\n1 1\n0\n")
        img = parse_pbm_strict(str(p))
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [0]

    def test_p1_with_comment(self, tmp_path):
        p = tmp_path / "comment.pbm"
        p.write_text("P1\n# A comment\n2 2\n0 1\n1 0\n")
        img = parse_pbm_strict(str(p))
        assert img.pixels == [0, 1, 1, 0]

    def test_p1_extra_whitespace(self, tmp_path):
        p = tmp_path / "space.pbm"
        p.write_text("P1\n  2   2  \n 0  1  1  0 \n")
        img = parse_pbm_strict(str(p))
        assert img.pixels == [0, 1, 1, 0]

    def test_invalid_magic(self, tmp_path):
        p = tmp_path / "bad.pbm"
        p.write_text("P9\n1 1\n0\n")
        with pytest.raises((PbmInvalidMagicError, PbmError)):
            parse_pbm_strict(str(p))

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.pbm"
        p.write_text("")
        with pytest.raises(PbmError):
            parse_pbm_strict(str(p))

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PbmError):
            parse_pbm_strict(str(tmp_path / "nope.pbm"))

    def test_write_read_roundtrip_checkerboard(self, tmp_path):
        pixels = [0, 1, 1, 0, 0, 1, 1, 0, 0]
        p = tmp_path / "checker.pbm"
        write_pbm(pixels, 3, 3, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == pixels

    def test_safe_result_on_bad_file(self, tmp_path):
        p = tmp_path / "trash.pbm"
        p.write_text("GARBAGE_DATA")
        result = parse_pbm(str(p))
        assert result is not None
        # parse_pbm never raises — returns dict
        assert isinstance(result, dict)

    def test_multiple_comments(self, tmp_path):
        p = tmp_path / "multi.pbm"
        p.write_text("P1\n# comment 1\n# comment 2\n2 1\n0 1\n")
        img = parse_pbm_strict(str(p))
        assert img.pixels == [0, 1]
