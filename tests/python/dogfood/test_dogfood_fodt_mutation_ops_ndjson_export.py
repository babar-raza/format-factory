"""
tests/python/dogfood/test_dogfood_fodt_mutation_ops_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-84
Dogfood export: FODT parse -> mutation ops -> write as NDJSON -> verify.
Uses: parse_fodt, write_fodt, document_set_block_text, document_append_paragraph,
      document_remove_paragraph, document_warnings_for_unsupported_edit,
      fodt_char_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    write_fodt,
    document_set_block_text,
    document_append_paragraph,
    document_remove_paragraph,
    document_warnings_for_unsupported_edit,
    fodt_char_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtMutationOpsNdjsonExport:
    """FODT -> mutation ops -> NDJSON export -> roundtrip verification."""

    def test_append_paragraph_basics(self):
        sample = _valid_fodt_files()[0]
        doc = parse_fodt(str(sample))
        ok, msg = document_append_paragraph(doc, "Sprint 84 test paragraph")
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    def test_char_count_basics(self):
        for f in _valid_fodt_files():
            count = fodt_char_count(str(f))
            assert isinstance(count, int)
            assert count >= 0

    def test_mutation_ops_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            char_count = fodt_char_count(path)
            doc = parse_fodt(path)
            ok_ap, msg_ap = document_append_paragraph(doc, "Appended by Sprint 84")
            warnings = document_warnings_for_unsupported_edit(doc, 0)
            ok_sb, msg_sb = document_set_block_text(doc, 0, "Updated text")
            assert isinstance(char_count, int), f"fodt_char_count must be int for {f.name}"
            assert isinstance(ok_ap, bool), f"document_append_paragraph must return bool for {f.name}"
            assert isinstance(warnings, list), f"document_warnings_for_unsupported_edit must return list for {f.name}"
            assert isinstance(ok_sb, bool), f"document_set_block_text must return bool for {f.name}"
            records.append({
                "file": f.name,
                "char_count": char_count,
                "append_para_ok": ok_ap,
                "warnings_count": len(warnings),
                "set_block_ok": ok_sb,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-mutation-ops.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            char_count = fodt_char_count(path)
            doc = parse_fodt(path)
            ok_ap, _ = document_append_paragraph(doc, "Roundtrip test")
            records.append({
                "file": f.name,
                "char_count": char_count,
                "append_para_ok": ok_ap,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["char_count"] == back["char_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_fodt_files()[0]
        char_count = fodt_char_count(str(sample))
        doc = parse_fodt(str(sample))
        ok_ap, _ = document_append_paragraph(doc, "JSON validity test")
        records = [{"file": sample.name, "char_count": char_count, "append_para_ok": ok_ap}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_write_fodt_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            out = tmp_path / f"out_{f.name}"
            write_fodt(doc, str(out))
            assert out.exists()
            assert out.stat().st_size > 0
            ok_rp, msg_rp = document_remove_paragraph(doc, 0)
            assert isinstance(ok_rp, bool), f"document_remove_paragraph must return bool for {f.name}"
            records.append({
                "file": f.name,
                "written_bytes": out.stat().st_size,
                "remove_para_ok": ok_rp,
                "format": "fodt",
            })
        dest = tmp_path / "write-roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["written_bytes"] > 0 for r in loaded)

    def test_warnings_and_mutations_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            doc = parse_fodt(path)
            warnings = document_warnings_for_unsupported_edit(doc, 0)
            ok_sb, _ = document_set_block_text(doc, 0, "New text S84")
            ok_rp, _ = document_remove_paragraph(doc, 0)
            char_count = fodt_char_count(path)
            records.append({
                "file": f.name,
                "warnings_count": len(warnings),
                "set_block_ok": ok_sb,
                "remove_para_ok": ok_rp,
                "char_count": char_count,
            })
        dest = tmp_path / "warnings-mutations.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        assert all(isinstance(r["warnings_count"], int) for r in loaded)
