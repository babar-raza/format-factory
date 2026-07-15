"""Core tests for the ubl codec — probe, load, write, roundtrip."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ubl.ubl_codec import (
    get_line_count,
    load_ubl,
    probe_ubl,
    roundtrip,
    ubl_installed_workflow,
    write_ubl,
)
from ubl.exceptions import UblParseError
from ubl.models import UblDocument

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestProbe:
    def test_probe_valid_minimal_invoice(self):
        assert probe_ubl(VALID_DIR / "minimal-invoice.xml") is True

    def test_probe_valid_multi_line_invoice(self):
        assert probe_ubl(VALID_DIR / "multi-line-invoice.xml") is True

    def test_probe_valid_minimal_order(self):
        assert probe_ubl(VALID_DIR / "minimal-order.xml") is True

    def test_probe_invalid_missing_mandatory(self):
        assert probe_ubl(INVALID_DIR / "missing-mandatory.xml") is True

    def test_probe_nonexistent_file(self):
        assert probe_ubl("/nonexistent/file.xml") is False

    def test_probe_random_bytes(self):
        assert probe_ubl(b"not xml") is False

    def test_probe_empty(self):
        assert probe_ubl(b"") is False

    def test_probe_non_ubl_xml(self):
        assert probe_ubl(b'<?xml version="1.0"?><root/>') is False


class TestLoad:
    def test_load_minimal_invoice(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert isinstance(model, dict)
        assert model["document_type"] == "Invoice"
        assert "id" in model
        assert "issue_date" in model

    def test_load_multi_line_invoice(self):
        model = load_ubl(VALID_DIR / "multi-line-invoice.xml")
        assert len(model.get("lines", [])) >= 2

    def test_load_minimal_order(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        assert model["document_type"] == "Order"

    def test_load_invoice_has_parties(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert "supplier" in model or "customer" in model

    def test_load_non_ubl_raises(self):
        with pytest.raises(UblParseError):
            load_ubl(b'<?xml version="1.0"?><root/>')

    def test_load_bad_xml_raises(self):
        with pytest.raises(UblParseError, match="Invalid XML"):
            load_ubl(b"<not>closed xml")


class TestWrite:
    def test_write_returns_xml_string(self):
        model = {
            "document_type": "Invoice",
            "id": "INV-001",
            "issue_date": "2026-01-01",
            "currency": "USD",
            "lines": [],
        }
        result = write_ubl(model)
        assert "INV-001" in result
        assert "Invoice" in result

    def test_write_to_file(self):
        model = {
            "document_type": "Invoice",
            "id": "INV-002",
            "issue_date": "2026-07-14",
            "lines": [],
        }
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            dest = f.name
        try:
            write_ubl(model, dest)
            content = Path(dest).read_text(encoding="utf-8")
            assert "INV-002" in content
        finally:
            Path(dest).unlink(missing_ok=True)


class TestRoundtrip:
    def test_roundtrip_minimal_invoice(self):
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            dest = f.name
        try:
            original = load_ubl(VALID_DIR / "minimal-invoice.xml")
            reloaded = roundtrip(VALID_DIR / "minimal-invoice.xml", dest)
            assert original["document_type"] == reloaded["document_type"]
            assert original["id"] == reloaded["id"]
        finally:
            Path(dest).unlink(missing_ok=True)


class TestHelpers:
    def test_get_line_count(self):
        model = {"lines": [{"id": "1"}, {"id": "2"}, {"id": "3"}]}
        assert get_line_count(model) == 3

    def test_get_line_count_empty(self):
        model = {"lines": []}
        assert get_line_count(model) == 0


class TestModel:
    def test_ubl_document(self):
        data = {
            "document_type": "Invoice",
            "id": "INV-100",
            "issue_date": "2026-07-14",
            "lines": [{"id": "1", "item_name": "Widget"}],
        }
        doc = UblDocument(data)
        assert doc.document_type == "Invoice"
        assert doc.doc_id == "INV-100"
        assert doc.line_count == 1
        assert not doc.is_empty
        assert repr(doc) == "UblDocument(type='Invoice', id='INV-100')"


class TestImport:
    def test_import_probe_load(self):
        from ubl import probe, load
        assert callable(probe)
        assert callable(load)

    def test_import_write(self):
        from ubl import write
        assert callable(write)

    def test_installed_workflow(self):
        result = ubl_installed_workflow(VALID_DIR / "minimal-invoice.xml")
        assert result["format"] == "ubl"
        assert result["loaded"] is True
        assert result["document_type"] == "Invoice"
