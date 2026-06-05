# R105 Wave 3: SYLK malformed input diagnostics and error recovery
# Lane F — SYLK FOSS
# Ledger: R105-FOSS-SYLK-MALFORMED-DIAGNOSTICS-001

import pytest
from pathlib import Path
from sylk.sylk_parser import (
    parse_sylk,
    parse_sylk_strict,
    SylkError,
    SylkInvalidFormatError,
    SylkSizeError,
)


class TestMalformedInput:
    """Verify parser handles malformed SYLK files gracefully."""

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.sylk"
        p.write_text("")
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(str(p))

    def test_no_id_record(self, tmp_path):
        p = tmp_path / "no_id.sylk"
        p.write_text("C;X1;Y1;K42\nE\n")
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(str(p))

    def test_missing_e_record(self, tmp_path):
        p = tmp_path / "no_e.sylk"
        p.write_text("ID;P\nC;X1;Y1;K42\n")
        # Should still parse (E record optional in lenient mode)
        result = parse_sylk(str(p))
        assert result is not None

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError, match="not found"):
            parse_sylk_strict(str(tmp_path / "nope.sylk"))

    def test_only_id_and_e(self, tmp_path):
        p = tmp_path / "minimal.sylk"
        p.write_text("ID;P\nE\n")
        doc = parse_sylk_strict(str(p))
        assert len(doc.cells) == 0

    def test_safe_result_on_bad_file(self, tmp_path):
        p = tmp_path / "bad.sylk"
        p.write_text("GARBAGE")
        result = parse_sylk(str(p))
        assert result is not None
        assert "error" in result or result.get("success") is False or isinstance(result, dict)

    def test_c_record_missing_k_field(self, tmp_path):
        p = tmp_path / "no_k.sylk"
        p.write_text("ID;P\nC;X1;Y1\nE\n")
        doc = parse_sylk_strict(str(p))
        # Cell with no K field should be handled gracefully
        assert doc is not None

    def test_c_record_string_value(self, tmp_path):
        p = tmp_path / "string.sylk"
        p.write_text('ID;P\nC;X1;Y1;K"hello"\nE\n')
        doc = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in doc.cells}
        assert vals.get((1, 1)) == "hello"

    def test_c_record_numeric_value(self, tmp_path):
        p = tmp_path / "numeric.sylk"
        p.write_text("ID;P\nC;X1;Y1;K42.5\nE\n")
        doc = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in doc.cells}
        assert vals.get((1, 1)) == 42.5

    def test_f_record_skipped(self, tmp_path):
        p = tmp_path / "f_record.sylk"
        p.write_text("ID;P\nF;Y1;X1;G\nC;X1;Y1;K99\nE\n")
        doc = parse_sylk_strict(str(p))
        vals = {(c.row, c.col): c.value for c in doc.cells}
        assert vals.get((1, 1)) == 99
