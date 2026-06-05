# R107 Wave 4: SYLK → CSV dogfood export pipeline
# 6 tests — end-to-end SYLK parse + CSV export verification

import importlib
import os
import tempfile
import pytest

sylk = importlib.import_module("sylk")


def _write_sylk(content: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        return f.name


class TestSylkDogfoodCsvPipeline:
    """End-to-end SYLK → CSV dogfood pipeline."""

    def test_dogfood_simple_grid(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K1\nC;X2;Y1;K2\nC;X1;Y2;K3\nC;X2;Y2;K4\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert "1" in csv
            assert "4" in csv
            lines = [l for l in csv.strip().split("\n") if l.strip()]
            assert len(lines) >= 2
        finally:
            os.unlink(path)

    def test_dogfood_string_data(self):
        path = _write_sylk('ID;P\nC;X1;Y1;K"Name"\nC;X2;Y1;K"Age"\nC;X1;Y2;K"Alice"\nC;X2;Y2;K30\nE')
        try:
            csv = sylk.sylk_to_csv(path)
            assert "Name" in csv
            assert "Alice" in csv
        finally:
            os.unlink(path)

    def test_dogfood_parse_then_csv(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K42\nE")
        try:
            parsed = sylk.parse_sylk(path)
            assert parsed.get("ok") is True
            csv = sylk.sylk_to_csv(path)
            assert "42" in csv
        finally:
            os.unlink(path)

    def test_dogfood_multirow_csv(self):
        rows = "\n".join(f"C;X1;Y{i+1};K{i*10}" for i in range(5))
        path = _write_sylk(f"ID;P\n{rows}\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            for i in range(5):
                assert str(i * 10) in csv
        finally:
            os.unlink(path)

    def test_dogfood_csv_format_is_text(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K1\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert isinstance(csv, str)
            assert len(csv) > 0
        finally:
            os.unlink(path)

    def test_dogfood_negative_numbers(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K-5\nC;X2;Y1;K-100\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert "-5" in csv
            assert "-100" in csv
        finally:
            os.unlink(path)
