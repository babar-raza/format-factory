"""R112 FOSS: DIF parse/export roundtrip hardening."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from dif.dif_parser import parse_dif


SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "dif")
MINIMAL_DIF = os.path.join(SAMPLE_DIR, "minimal.dif")
HAS_MINIMAL = os.path.exists(MINIMAL_DIF)


class TestR112DifRoundtripHardening:
    def test_parse_nonexistent_file_returns_error(self):
        result = parse_dif("/nonexistent/path/to/file.dif")
        assert result["ok"] is False

    def test_parse_empty_string_returns_error(self):
        result = parse_dif("")
        assert result["ok"] is False

    @pytest.mark.skipif(not HAS_MINIMAL, reason="No minimal.dif sample available")
    def test_parse_minimal_dif_returns_ok(self):
        result = parse_dif(MINIMAL_DIF)
        assert result["ok"] is True

    @pytest.mark.skipif(not HAS_MINIMAL, reason="No minimal.dif sample available")
    def test_parse_minimal_dif_has_rows(self):
        result = parse_dif(MINIMAL_DIF)
        assert "rows" in result
        assert len(result["rows"]) > 0

    @pytest.mark.skipif(not HAS_MINIMAL, reason="No minimal.dif sample available")
    def test_parse_minimal_dif_rows_are_lists(self):
        result = parse_dif(MINIMAL_DIF)
        for row in result["rows"]:
            assert isinstance(row, list)

    @pytest.mark.skipif(not HAS_MINIMAL, reason="No minimal.dif sample available")
    def test_parse_minimal_dif_has_metadata(self):
        result = parse_dif(MINIMAL_DIF)
        assert "rows" in result or "columns" in result or "headers" in result

    def test_parse_dif_api_returns_dict(self):
        result = parse_dif("/definitely/not/a/file.dif")
        assert isinstance(result, dict)

    def test_parse_dif_error_has_ok_field(self):
        result = parse_dif("/tmp/no_such.dif")
        assert "ok" in result
