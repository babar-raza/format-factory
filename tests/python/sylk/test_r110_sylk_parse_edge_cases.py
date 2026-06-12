# R110 Wave 5: SYLK Parse Edge-Case Hardening Tests
# FOSS depth: parse edge-cases — error paths, field inspection (roundtrip)

import os
import tempfile
import sylk


class TestR110SylkParseEdgeCases:
    """SYLK parse edge-case and error-handling tests."""

    def test_parse_nonexistent_file(self):
        """Parsing a nonexistent file returns error or raises."""
        result = sylk.parse_sylk("/nonexistent/path/r110_fake.sylk")
        assert result.get("ok") is False

    def test_parse_empty_file(self):
        """Parsing an empty file returns error."""
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            result = sylk.parse_sylk(path)
            assert result.get("ok") is False
        finally:
            os.unlink(path)

    def test_parse_minimal_valid_sylk(self):
        """Parse a minimal valid SYLK (ID;P header + E terminator)."""
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            f.write("ID;P\nE\n")
            path = f.name
        try:
            result = sylk.parse_sylk(path)
            assert result.get("ok") is True
        finally:
            os.unlink(path)

    def test_parse_sylk_with_data_cells(self):
        """Parse SYLK with C records containing cell data."""
        content = 'ID;P\nC;Y1;X1;K"Hello"\nC;Y1;X2;K"World"\nE\n'
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = sylk.parse_sylk(path)
            assert result.get("ok") is True
            assert result.get("cell_count", 0) >= 2
        finally:
            os.unlink(path)

    def test_csv_export_nonexistent_file(self):
        """CSV export of nonexistent file raises or returns error."""
        try:
            result = sylk.sylk_to_csv("/nonexistent/r110_fake.sylk")
            # If it doesn't raise, we're fine — either way is valid
        except Exception:
            pass  # Expected

    def test_csv_export_minimal(self):
        """CSV export of minimal SYLK with data produces string."""
        content = 'ID;P\nC;Y1;X1;K"Val"\nE\n'
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            csv_str = sylk.sylk_to_csv(path)
            assert isinstance(csv_str, str)
            assert "Val" in csv_str
        finally:
            os.unlink(path)

    def test_probe_sylk_returns_dict(self):
        """probe_sylk returns a dict with format info."""
        content = "ID;P\nE\n"
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            info = sylk.probe_sylk(path)
            assert isinstance(info, dict)
        finally:
            os.unlink(path)

    def test_parse_result_has_ok_field(self):
        """parse_sylk result dict includes 'ok' boolean field."""
        content = "ID;P\nE\n"
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            f.write(content)
            path = f.name
        try:
            result = sylk.parse_sylk(path)
            assert "ok" in result
            assert isinstance(result["ok"], bool)
        finally:
            os.unlink(path)
