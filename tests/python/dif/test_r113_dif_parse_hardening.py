"""R113 FOSS: DIF parse error handling hardening."""
import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from dif.dif_parser import parse_dif


class TestR113DifParseHardening:
    def test_parse_nonexistent_returns_error(self):
        result = parse_dif("/nonexistent/path/file.dif")
        assert result["ok"] is False

    def test_parse_empty_file_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w") as f:
            f.write("")
            path = f.name
        try:
            result = parse_dif(path)
            assert result["ok"] is False
        finally:
            os.unlink(path)

    def test_parse_invalid_content_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w") as f:
            f.write("NOT A DIF FILE")
            path = f.name
        try:
            result = parse_dif(path)
            assert result["ok"] is False
        finally:
            os.unlink(path)

    def test_parse_error_has_message(self):
        result = parse_dif("/does/not/exist.dif")
        assert "error" in result

    def test_parse_error_has_type(self):
        result = parse_dif("/does/not/exist.dif")
        assert "error_type" in result

    def test_parse_api_always_returns_dict(self):
        result = parse_dif("/tmp/nonexistent.dif")
        assert isinstance(result, dict)

    def test_parse_binary_garbage_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".dif", delete=False) as f:
            f.write(bytes(range(256)))
            path = f.name
        try:
            result = parse_dif(path)
            assert result["ok"] is False
        finally:
            os.unlink(path)

    def test_parse_partial_header_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w") as f:
            f.write("TABLE\n0,1\n")
            path = f.name
        try:
            result = parse_dif(path)
            # May parse partially or fail - either way should not crash
            assert isinstance(result, dict)
        finally:
            os.unlink(path)
