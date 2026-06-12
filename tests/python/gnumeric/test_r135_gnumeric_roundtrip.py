"""Gnumeric roundtrip tests: create → write → load → compare.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001
TC-PRODUCT-GNUMERIC-ROUNDTRIP
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, write_gnumeric, load


class TestGnumericRoundtrip:
    def test_roundtrip_preserves_sheet_count(self, tmp_path):
        model = create_gnumeric([{"name": "Sheet1"}, {"name": "Sheet2"}])
        dest = tmp_path / "test.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        assert model2["sheet_count"] == 2

    def test_roundtrip_preserves_sheet_names(self, tmp_path):
        sheets = [{"name": "Alpha"}, {"name": "Beta"}]
        model = create_gnumeric(sheets)
        dest = tmp_path / "test.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        names = [s["name"] for s in model2["sheets"]]
        assert "Alpha" in names
        assert "Beta" in names

    def test_roundtrip_preserves_cell_values(self, tmp_path):
        sheets = [{"name": "Data", "rows": [["A", "B", "C"], ["1", "2", "3"]]}]
        model = create_gnumeric(sheets)
        dest = tmp_path / "data.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        # Cell values should still be present in the grid
        sheet = model2["sheets"][0]
        assert "A" in sheet["cell_values"]
        assert "1" in sheet["cell_values"]

    def test_roundtrip_single_sheet(self, tmp_path):
        model = create_gnumeric([{"name": "Single"}])
        dest = tmp_path / "single.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        assert model2["sheet_count"] == 1
        assert model2["sheets"][0]["name"] == "Single"

    def test_roundtrip_empty_workbook(self, tmp_path):
        model = create_gnumeric([])
        dest = tmp_path / "empty.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        assert model2["sheet_count"] == 0

    def test_roundtrip_writes_gzip_file(self, tmp_path):
        model = create_gnumeric([{"name": "S1"}])
        dest = tmp_path / "out.gnumeric"
        write_gnumeric(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0
        # Gnumeric files are gzip-compressed
        content = dest.read_bytes()
        assert content[:2] == b"\x1f\x8b"  # gzip magic bytes

    def test_roundtrip_is_gnumeric_flag(self, tmp_path):
        model = create_gnumeric([{"name": "Test"}])
        dest = tmp_path / "out.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        assert model2.get("is_gnumeric") is True

    def test_roundtrip_three_sheets_with_data(self, tmp_path):
        sheets = [
            {"name": "A", "rows": [["x"]]},
            {"name": "B", "rows": [["y", "z"]]},
            {"name": "C", "rows": []},
        ]
        model = create_gnumeric(sheets)
        dest = tmp_path / "multi.gnumeric"
        write_gnumeric(model, dest)
        model2 = load(dest)
        assert model2["sheet_count"] == 3

    def test_double_roundtrip_preserves_structure(self, tmp_path):
        """Create → write → reload → write again → reload: should still match."""
        sheets = [{"name": "Main", "rows": [["val1", "val2"]]}]
        model = create_gnumeric(sheets)
        dest1 = tmp_path / "round1.gnumeric"
        dest2 = tmp_path / "round2.gnumeric"
        write_gnumeric(model, dest1)
        model2 = load(dest1)
        write_gnumeric(model2, dest2)
        model3 = load(dest2)
        assert model3["sheet_count"] == model2["sheet_count"]
        assert model3["sheets"][0]["name"] == model2["sheets"][0]["name"]
