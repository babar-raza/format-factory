"""
tests/python/abw/test_r123_abw_csv_export.py

Sprint: FORMAT-FACTORY-EXPANDED-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
TC-ABW-CSV: export_to_csv()
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import create_abw, write_abw, export_to_csv


def _make_abw(paragraphs: list[str]) -> Path:
    tmp = Path(tempfile.mktemp(suffix=".abw"))
    write_abw(create_abw(paragraphs), tmp)
    return tmp


class TestExportToCsv:
    def test_returns_string(self):
        tmp = _make_abw(["Hello"])
        try:
            result = export_to_csv(tmp)
            assert isinstance(result, str)
        finally:
            tmp.unlink(missing_ok=True)

    def test_has_header_row(self):
        tmp = _make_abw(["Hello"])
        try:
            lines = export_to_csv(tmp).splitlines()
            assert lines[0] == "text"
        finally:
            tmp.unlink(missing_ok=True)

    def test_single_paragraph(self):
        tmp = _make_abw(["Hello world"])
        try:
            lines = export_to_csv(tmp).splitlines()
            assert lines[1] == "Hello world"
        finally:
            tmp.unlink(missing_ok=True)

    def test_multiple_paragraphs(self):
        tmp = _make_abw(["First", "Second", "Third"])
        try:
            lines = export_to_csv(tmp).splitlines()
            assert lines[0] == "text"
            assert lines[1] == "First"
            assert lines[2] == "Second"
            assert lines[3] == "Third"
        finally:
            tmp.unlink(missing_ok=True)

    def test_row_count_matches_paragraphs(self):
        paras = ["A", "B", "C", "D", "E"]
        tmp = _make_abw(paras)
        try:
            lines = [l for l in export_to_csv(tmp).splitlines() if l]
            assert len(lines) == len(paras) + 1  # header + N rows
        finally:
            tmp.unlink(missing_ok=True)

    def test_empty_document(self):
        tmp = _make_abw([])
        try:
            result = export_to_csv(tmp)
            lines = result.splitlines()
            assert lines[0] == "text"
            assert len(lines) == 1
        finally:
            tmp.unlink(missing_ok=True)

    def test_ends_with_newline(self):
        tmp = _make_abw(["A"])
        try:
            result = export_to_csv(tmp)
            assert result.endswith("\n")
        finally:
            tmp.unlink(missing_ok=True)

    def test_comma_in_field_is_quoted(self):
        tmp = _make_abw(["Hello, world"])
        try:
            lines = export_to_csv(tmp).splitlines()
            assert lines[1] == '"Hello, world"'
        finally:
            tmp.unlink(missing_ok=True)

    def test_double_quote_in_field_is_escaped(self):
        tmp = _make_abw(['Say "hi"'])
        try:
            lines = export_to_csv(tmp).splitlines()
            assert lines[1] == '"Say ""hi"""'
        finally:
            tmp.unlink(missing_ok=True)

    def test_plain_text_not_quoted(self):
        tmp = _make_abw(["plain text here"])
        try:
            lines = export_to_csv(tmp).splitlines()
            assert lines[1] == "plain text here"
            assert not lines[1].startswith('"')
        finally:
            tmp.unlink(missing_ok=True)

    def test_accepts_bytes(self):
        tmp = _make_abw(["Test"])
        try:
            result = export_to_csv(tmp.read_bytes())
            assert "text" in result
            assert "Test" in result
        finally:
            tmp.unlink(missing_ok=True)

    def test_accepts_string_path(self):
        tmp = _make_abw(["Test"])
        try:
            result = export_to_csv(str(tmp))
            assert "Test" in result
        finally:
            tmp.unlink(missing_ok=True)

    def test_accepts_path_object(self):
        tmp = _make_abw(["Test"])
        try:
            result = export_to_csv(tmp)
            assert "Test" in result
        finally:
            tmp.unlink(missing_ok=True)

    def test_package_import(self):
        import abw
        assert hasattr(abw, "export_to_csv")

    def test_in_all(self):
        import abw
        assert "export_to_csv" in abw.__all__
