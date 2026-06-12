"""
test_r165_abw_export_coverage.py — Closes ABW export capability gaps.

Gaps closed:
  GAP-ABW-FOSS-WRITE_ABW-001     (write_abw)
  GAP-ABW-FOSS-EXPORT_TO_CS-001  (export_to_csv)
  GAP-ABW-FOSS-EXPORT_TO_JS-001  (export_to_json)
  GAP-ABW-FOSS-EXPORT_TO_MA-001  (export_to_markdown)
  GAP-ABW-FOSS-GET_PARAGRAP-001  (get_paragraphs via extract_text)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    export_to_csv,
    export_to_json,
    export_to_markdown,
    extract_text,
    load,
    write_abw,
)


def _make_abw_file(paragraphs: list[str], tmp_path: Path) -> Path:
    doc = create_abw(paragraphs)
    p = tmp_path / "test.abw"
    write_abw(doc, str(p))
    return p


def _make_abw_bytes(paragraphs: list[str]) -> bytes:
    doc = create_abw(paragraphs)
    with tempfile.NamedTemporaryFile(suffix=".abw", delete=False) as f:
        path = Path(f.name)
    write_abw(doc, str(path))
    data = path.read_bytes()
    path.unlink()
    return data


class TestWriteAbw:
    def test_write_creates_file(self, tmp_path):
        doc = create_abw(["Hello"])
        p = tmp_path / "out.abw"
        write_abw(doc, str(p))
        assert p.exists()
        assert p.stat().st_size > 0

    def test_write_produces_valid_xml(self, tmp_path):
        doc = create_abw(["Hello", "World"])
        p = tmp_path / "out.abw"
        write_abw(doc, str(p))
        text = p.read_text(encoding="utf-8")
        assert "<abiword" in text
        assert "Hello" in text

    def test_write_roundtrip_count(self, tmp_path):
        doc = create_abw(["A", "B", "C"])
        p = tmp_path / "out.abw"
        write_abw(doc, str(p))
        reloaded = load(str(p))
        assert reloaded["paragraph_count"] == 3

    def test_write_roundtrip_content(self, tmp_path):
        doc = create_abw(["First paragraph"])
        p = tmp_path / "out.abw"
        write_abw(doc, str(p))
        reloaded = load(str(p))
        assert "First paragraph" in reloaded["paragraphs"]

    def test_write_empty_document(self, tmp_path):
        doc = create_abw([])
        p = tmp_path / "empty.abw"
        write_abw(doc, str(p))
        assert p.exists()
        reloaded = load(str(p))
        assert reloaded["paragraph_count"] == 0


class TestExportToCsv:
    def test_export_returns_string(self, tmp_path):
        p = _make_abw_file(["Hello", "World"], tmp_path)
        result = export_to_csv(str(p))
        assert isinstance(result, str)

    def test_export_contains_content(self, tmp_path):
        p = _make_abw_file(["Line one", "Line two"], tmp_path)
        result = export_to_csv(str(p))
        assert "Line one" in result or "line one" in result.lower()

    def test_export_from_bytes(self):
        data = _make_abw_bytes(["Alpha", "Beta"])
        result = export_to_csv(data)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_has_rows(self, tmp_path):
        p = _make_abw_file(["A", "B", "C"], tmp_path)
        result = export_to_csv(str(p))
        lines = [ln for ln in result.strip().split("\n") if ln.strip()]
        assert len(lines) >= 1


class TestExportToJson:
    def test_export_returns_string(self, tmp_path):
        p = _make_abw_file(["Hello"], tmp_path)
        result = export_to_json(str(p))
        assert isinstance(result, str)

    def test_export_is_valid_json(self, tmp_path):
        p = _make_abw_file(["Hello", "World"], tmp_path)
        result = export_to_json(str(p))
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_export_has_paragraphs(self, tmp_path):
        p = _make_abw_file(["Para one", "Para two"], tmp_path)
        result = export_to_json(str(p))
        parsed = json.loads(result)
        assert "paragraphs" in parsed

    def test_export_from_bytes(self):
        data = _make_abw_bytes(["Alpha"])
        result = export_to_json(data)
        parsed = json.loads(result)
        assert parsed["paragraph_count"] >= 1


class TestExportToMarkdown:
    def test_export_returns_string(self, tmp_path):
        p = _make_abw_file(["Hello"], tmp_path)
        model = load(str(p))
        result = export_to_markdown(model)
        assert isinstance(result, str)

    def test_export_contains_content(self, tmp_path):
        p = _make_abw_file(["Hello World"], tmp_path)
        model = load(str(p))
        result = export_to_markdown(model)
        assert "Hello World" in result

    def test_export_multiple_paragraphs(self, tmp_path):
        p = _make_abw_file(["First", "Second", "Third"], tmp_path)
        model = load(str(p))
        result = export_to_markdown(model)
        assert "First" in result
        assert "Third" in result


class TestExtractText:
    def test_extract_returns_list(self, tmp_path):
        p = _make_abw_file(["Hello", "World"], tmp_path)
        result = extract_text(str(p))
        assert isinstance(result, list)

    def test_extract_correct_count(self, tmp_path):
        p = _make_abw_file(["A", "B", "C"], tmp_path)
        result = extract_text(str(p))
        assert len(result) == 3

    def test_extract_content(self, tmp_path):
        p = _make_abw_file(["The quick brown fox"], tmp_path)
        result = extract_text(str(p))
        assert result[0] == "The quick brown fox"
