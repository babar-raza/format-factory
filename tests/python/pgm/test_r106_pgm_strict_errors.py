# R106 Wave 3: PGM strict parse error diagnostics
# Lane E — Python Netpbm FOSS
# Ledger: R106-FOSS-PGM-STRICT-ERRORS-001

import pytest
from pgm.pgm_parser import (
    parse_pgm,
    parse_pgm_strict,
    PgmError,
    PgmInvalidMagicError,
    PgmSizeError,
)


class TestPgmStrictErrors:
    """PGM P2 strict parser error handling."""

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.pgm"
        p.write_text("")
        with pytest.raises(PgmError):
            parse_pgm_strict(str(p))

    def test_invalid_magic(self, tmp_path):
        p = tmp_path / "bad.pgm"
        p.write_text("P9\n1 1\n255\n0\n")
        with pytest.raises((PgmInvalidMagicError, PgmError)):
            parse_pgm_strict(str(p))

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PgmError):
            parse_pgm_strict(str(tmp_path / "nope.pgm"))

    def test_safe_mode_on_garbage(self, tmp_path):
        p = tmp_path / "garbage.pgm"
        p.write_text("GARBAGE")
        result = parse_pgm(str(p))
        assert result is not None
        assert isinstance(result, dict)

    def test_valid_minimal(self, tmp_path):
        p = tmp_path / "min.pgm"
        p.write_text("P2\n1 1\n255\n128\n")
        img = parse_pgm_strict(str(p))
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [128]

    def test_with_comment(self, tmp_path):
        p = tmp_path / "comment.pgm"
        p.write_text("P2\n# A comment\n2 2\n255\n0 64 128 255\n")
        img = parse_pgm_strict(str(p))
        assert img.pixels == [0, 64, 128, 255]

    def test_extra_whitespace(self, tmp_path):
        p = tmp_path / "space.pgm"
        p.write_text("P2\n  2   2  \n  255  \n 0  64  128  255 \n")
        img = parse_pgm_strict(str(p))
        assert img.pixels == [0, 64, 128, 255]

    def test_multiple_comments(self, tmp_path):
        p = tmp_path / "multi.pgm"
        p.write_text("P2\n# c1\n# c2\n# c3\n1 1\n255\n42\n")
        img = parse_pgm_strict(str(p))
        assert img.pixels == [42]

    def test_maxval_boundary(self, tmp_path):
        p = tmp_path / "maxval.pgm"
        p.write_text("P2\n1 1\n1\n1\n")
        img = parse_pgm_strict(str(p))
        assert img.maxval == 1
        assert img.pixels == [1]
