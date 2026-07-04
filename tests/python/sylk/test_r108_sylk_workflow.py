# R108 Lane F: SYLK installed-workflow verification
# 8 tests — module import, parse, csv export, edge cases

import importlib
import os
import tempfile
import pytest

sylk = importlib.import_module("sylk")


def _write_sylk(content: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        return f.name


class TestSylkInstalledWorkflow:
    """SYLK module installed-workflow verification."""

    def test_module_importable(self):
        assert sylk is not None

    def test_parse_sylk_returns_dict(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K42\nE")
        try:
            result = sylk.parse_sylk(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_parse_sylk_ok_field(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K42\nE")
        try:
            result = sylk.parse_sylk(path)
            assert result.get("ok") is True
        finally:
            os.unlink(path)

    def test_sylk_to_csv_returns_string(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K42\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert isinstance(csv, str)
            assert "42" in csv
        finally:
            os.unlink(path)

    def test_csv_multirow(self):
        rows = "\n".join(f"C;X1;Y{i+1};K{i}" for i in range(10))
        path = _write_sylk(f"ID;P\n{rows}\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            lines = [l for l in csv.strip().split("\n") if l.strip()]
            assert len(lines) >= 10
        finally:
            os.unlink(path)

    def test_csv_string_values(self):
        path = _write_sylk('ID;P\nC;X1;Y1;K"hello"\nE')
        try:
            csv = sylk.sylk_to_csv(path)
            assert "hello" in csv
        finally:
            os.unlink(path)

    def test_parse_then_export_consistent(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K99\nC;X2;Y1;K88\nE")
        try:
            parsed = sylk.parse_sylk(path)
            csv = sylk.sylk_to_csv(path)
            assert parsed.get("ok") is True
            assert "99" in csv
            assert "88" in csv
        finally:
            os.unlink(path)

    def test_nonexistent_file_raises(self):
        with pytest.raises(Exception):
            sylk.sylk_to_csv("/nonexistent/path.slk")
