"""XLIFF roundtrip tests — load → write → reload identity verification.

Exercises all sample fixtures through the roundtrip() function. Verifies
that translation units, segments, inline markup, and metadata survive a
full serialization cycle without data loss.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xliff import load_xliff, write_xliff, roundtrip

SAMPLES = Path(_REPO / "samples" / "by-format" / "xliff" / "valid")


def _roundtrip_model(sample_name: str) -> tuple[dict, dict]:
    src = SAMPLES / sample_name
    original = load_xliff(src)
    with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        reloaded = roundtrip(src, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return original, reloaded


def _collect_units(model: dict) -> list[dict]:
    units = []
    for f in model.get("files", []):
        units.extend(f.get("units", []))
        for g in f.get("groups", []):
            units.extend(g.get("units", []))
    return units


class TestMinimalRoundtrip:
    def test_metadata_preserved(self):
        orig, rt = _roundtrip_model("minimal.xliff")
        assert rt["source_language"] == orig["source_language"]
        assert rt["target_language"] == orig["target_language"]

    def test_file_count_preserved(self):
        orig, rt = _roundtrip_model("minimal.xliff")
        assert len(rt["files"]) == len(orig["files"])

    def test_unit_content_preserved(self):
        orig, rt = _roundtrip_model("minimal.xliff")
        orig_units = _collect_units(orig)
        rt_units = _collect_units(rt)
        assert len(rt_units) == len(orig_units)
        for ou, ru in zip(orig_units, rt_units):
            assert ru["id"] == ou["id"]
            for os, rs in zip(ou.get("segments", []), ru.get("segments", [])):
                assert rs["source"] == os["source"]
                assert rs["target"] == os["target"]


class TestMultiUnitRoundtrip:
    def test_all_units_survive(self):
        orig, rt = _roundtrip_model("multi-unit.xliff")
        orig_units = _collect_units(orig)
        rt_units = _collect_units(rt)
        assert len(rt_units) == len(orig_units)

    def test_unit_ids_match(self):
        orig, rt = _roundtrip_model("multi-unit.xliff")
        orig_ids = [u["id"] for u in _collect_units(orig)]
        rt_ids = [u["id"] for u in _collect_units(rt)]
        assert rt_ids == orig_ids

    def test_segment_text_preserved(self):
        orig, rt = _roundtrip_model("multi-unit.xliff")
        for ou, ru in zip(_collect_units(orig), _collect_units(rt)):
            orig_segs = ou.get("segments", [])
            rt_segs = ru.get("segments", [])
            assert len(rt_segs) == len(orig_segs)
            for os, rs in zip(orig_segs, rt_segs):
                assert rs["source"] == os["source"]


class TestInlineCodeRoundtrip:
    def test_inline_markup_preserved(self):
        orig, rt = _roundtrip_model("with-inline-codes.xliff")
        orig_units = _collect_units(orig)
        rt_units = _collect_units(rt)
        assert len(rt_units) == len(orig_units)
        for ou, ru in zip(orig_units, rt_units):
            for os, rs in zip(ou.get("segments", []), ru.get("segments", [])):
                if os.get("source_content"):
                    assert rs.get("source_content") == os["source_content"]


class TestWriteToString:
    def test_write_returns_xml_string(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        xml_str = write_xliff(model)
        assert isinstance(xml_str, str)
        assert "xliff" in xml_str.lower()

    def test_write_produces_valid_xml(self):
        import xml.etree.ElementTree as ET
        model = load_xliff(SAMPLES / "minimal.xliff")
        xml_str = write_xliff(model)
        root = ET.fromstring(xml_str)
        assert root is not None


class TestAllSamplesRoundtrip:
    @pytest.mark.parametrize("sample", [
        "minimal.xliff",
        "multi-unit.xliff",
        "with-inline-codes.xliff",
    ])
    def test_sample_survives_roundtrip(self, sample):
        if not (SAMPLES / sample).exists():
            pytest.skip(f"Sample {sample} not found")
        orig, rt = _roundtrip_model(sample)
        assert rt["source_language"] == orig["source_language"]
        assert rt["target_language"] == orig["target_language"]
        assert len(_collect_units(rt)) == len(_collect_units(orig))
