"""
tests/python/dogfood/test_dogfood_ods_mutation_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-83
Dogfood export: ODS parse -> mutation operations -> write as NDJSON -> verify.
Uses: parse_ods_strict, add_sheet, remove_sheet, rename_sheet,
      add_row, delete_row, set_cell_value.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import parse_ods_strict, add_sheet, remove_sheet, rename_sheet, add_row, delete_row, set_cell_value
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsMutationAnalyticsNdjsonExport:
    """ODS -> mutation operations -> NDJSON export -> roundtrip verification."""

    def test_add_sheet_basics(self):
        sample = _valid_ods_files()[0]
        doc = parse_ods_strict(str(sample))
        ok, msg = add_sheet(doc, "_Sprint83Sheet")
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    def test_remove_sheet_basics(self):
        sample = _valid_ods_files()[0]
        doc = parse_ods_strict(str(sample))
        add_sheet(doc, "_TempSheet83")
        ok, msg = remove_sheet(doc, "_TempSheet83")
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    def test_mutation_ops_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            doc = parse_ods_strict(str(f))
            ok_add, msg_add = add_sheet(doc, "_S83A")
            ok_rem, msg_rem = remove_sheet(doc, "_S83A")
            ok_ren_pre, _ = add_sheet(doc, "_S83B")
            ok_ren, msg_ren = rename_sheet(doc, "_S83B", "_S83C")
            ok_ar, msg_ar = add_row(doc, 0, ["x", "y", "z"])
            ok_sc, msg_sc = set_cell_value(doc, 0, 0, 0, "mutated")
            assert isinstance(ok_add, bool), f"add_sheet must return bool for {f.name}"
            assert isinstance(ok_rem, bool), f"remove_sheet must return bool for {f.name}"
            assert isinstance(ok_ren, bool), f"rename_sheet must return bool for {f.name}"
            assert isinstance(ok_ar, bool), f"add_row must return bool for {f.name}"
            assert isinstance(ok_sc, bool), f"set_cell_value must return bool for {f.name}"
            records.append({
                "file": f.name,
                "add_sheet_ok": ok_add,
                "remove_sheet_ok": ok_rem,
                "rename_sheet_ok": ok_ren,
                "add_row_ok": ok_ar,
                "set_cell_ok": ok_sc,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-mutation.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            doc = parse_ods_strict(str(f))
            ok_add, _ = add_sheet(doc, "_S83RT")
            ok_rem, _ = remove_sheet(doc, "_S83RT")
            records.append({
                "file": f.name,
                "add_sheet_ok": ok_add,
                "remove_sheet_ok": ok_rem,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["add_sheet_ok"] == back["add_sheet_ok"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_ods_files()[0]
        doc = parse_ods_strict(str(sample))
        ok_add, _ = add_sheet(doc, "_S83JL")
        ok_sc, _ = set_cell_value(doc, 0, 0, 0, "val")
        records = [{"file": sample.name, "add_sheet_ok": ok_add, "set_cell_ok": ok_sc}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_delete_row_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            doc = parse_ods_strict(str(f))
            ok_ar, _ = add_row(doc, 0, ["a", "b", "c"])
            ok_dr, msg_dr = delete_row(doc, 0, 0)
            assert isinstance(ok_dr, bool), f"delete_row must return bool for {f.name}"
            assert isinstance(msg_dr, str), f"delete_row msg must be str for {f.name}"
            records.append({
                "file": f.name,
                "add_row_ok": ok_ar,
                "delete_row_ok": ok_dr,
                "format": "ods",
            })
        dest = tmp_path / "delete-row.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(isinstance(r["delete_row_ok"], bool) for r in loaded)

    def test_multi_mutation_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            doc = parse_ods_strict(str(f))
            ok_add, _ = add_sheet(doc, "_S83M")
            ok_ren, _ = rename_sheet(doc, "_S83M", "_S83MR")
            ok_ar, _ = add_row(doc, 0, ["p", "q"])
            ok_sc, _ = set_cell_value(doc, 0, 0, 0, "multi")
            records.append({
                "file": f.name,
                "add_sheet_ok": ok_add,
                "rename_sheet_ok": ok_ren,
                "add_row_ok": ok_ar,
                "set_cell_ok": ok_sc,
            })
        dest = tmp_path / "multi-mutation.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert all(isinstance(r["add_sheet_ok"], bool) for r in loaded)
