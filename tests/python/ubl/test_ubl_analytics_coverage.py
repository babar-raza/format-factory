"""Coverage tests for ubl analytics/helper surfaces not already exercised in
depth elsewhere.

The existing suite is thorough for load/write/roundtrip (test_ubl_codec.py,
test_ubl_roundtrip.py, test_ubl_document_mutation.py), analytics functions
against Invoice/Order fixtures (test_ubl_analytics.py), tax/monetary/party
depth (test_ubl_feature_completeness.py), the Compat facade
(test_ubl_compat.py), field-level parsing (test_ubl_parser_fields.py), and
the CSV dogfood export (test_ubl_to_csv.py).

This module fills the remaining gaps:
  - cli.py's main() entry point (previously had zero test coverage at all)
  - the full UblDocument property surface (raw, ubl_version, issue_date,
    to_dict, is_empty=True case) beyond what test_ubl_codec.py::TestModel
    and test_ubl_smoke.py::TestFromFile already cover
  - direct instantiation/catchability of UblError, UblParseError,
    UblWriteError, UblTaxInconsistencyWarning
  - get_line_count / ubl_installed_workflow / the three analytics functions
    against CreditNote and full-depth Invoice fixtures, which the existing
    analytics/codec tests do not exercise (they stick to minimal-invoice,
    multi-line-invoice, and minimal-order)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ubl import cli
from ubl.exceptions import (
    UblError,
    UblParseError,
    UblTaxInconsistencyWarning,
    UblWriteError,
)
from ubl.models import UblDocument
from ubl.ubl_analytics import (
    ubl_document_type_summary,
    ubl_supplier_name,
    ubl_total_line_count,
)
from ubl.ubl_codec import (
    get_line_count,
    load_ubl,
    probe_ubl,
    ubl_installed_workflow,
)

SAMPLES = _REPO / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


# ---------------------------------------------------------------------------
# get_line_count — real loaded models (existing test_ubl_codec.py::TestHelpers
# only covers synthetic dicts).
# ---------------------------------------------------------------------------
class TestGetLineCountRealModels:
    def test_minimal_invoice(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert get_line_count(model) == 1

    def test_multi_line_invoice(self):
        model = load_ubl(VALID_DIR / "multi-line-invoice.xml")
        assert get_line_count(model) == 3

    def test_minimal_order(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        assert get_line_count(model) == 1

    def test_minimal_creditnote(self):
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        assert get_line_count(model) == 1

    def test_matches_ubl_total_line_count(self):
        model = load_ubl(VALID_DIR / "multi-line-invoice.xml")
        assert get_line_count(model) == ubl_total_line_count(
            VALID_DIR / "multi-line-invoice.xml"
        )

    def test_no_lines_key_defaults_to_zero(self):
        assert get_line_count({}) == 0


# ---------------------------------------------------------------------------
# probe_ubl — a few edge cases not already covered in test_ubl_codec.py::TestProbe.
# ---------------------------------------------------------------------------
class TestProbeUblAdditional:
    def test_probe_creditnote(self):
        assert probe_ubl(VALID_DIR / "minimal-creditnote.xml") is True

    def test_probe_creditnote_with_totals(self):
        assert probe_ubl(VALID_DIR / "creditnote-with-totals.xml") is True

    def test_probe_full_depth_invoice(self):
        assert probe_ubl(VALID_DIR / "invoice-full-depth.xml") is True

    def test_probe_returns_bool_type(self):
        result = probe_ubl(VALID_DIR / "minimal-invoice.xml")
        assert result is True
        assert isinstance(result, bool)

    def test_probe_directory_path_does_not_raise(self):
        # A directory is not a readable file; probe_ubl must swallow the
        # resulting OSError and return False rather than propagating.
        assert probe_ubl(VALID_DIR) is False


# ---------------------------------------------------------------------------
# ubl_installed_workflow — only exercised once (minimal-invoice) in
# test_ubl_codec.py::TestImport. Extend to CreditNote/Order and verify all
# fields, plus the error path.
# ---------------------------------------------------------------------------
class TestUblInstalledWorkflow:
    def test_creditnote_workflow(self):
        result = ubl_installed_workflow(VALID_DIR / "minimal-creditnote.xml")
        assert result["format"] == "ubl"
        assert result["loaded"] is True
        assert result["document_type"] == "CreditNote"
        assert result["id"] == "CN-001"
        assert result["line_count"] == 1

    def test_order_workflow(self):
        result = ubl_installed_workflow(VALID_DIR / "minimal-order.xml")
        assert result["document_type"] == "Order"
        assert result["id"] == "ORD-001"
        assert result["line_count"] == 1

    def test_multi_line_invoice_workflow_line_count(self):
        result = ubl_installed_workflow(VALID_DIR / "multi-line-invoice.xml")
        assert result["line_count"] == 3

    def test_workflow_keys_exact(self):
        result = ubl_installed_workflow(VALID_DIR / "minimal-invoice.xml")
        assert set(result.keys()) == {"format", "loaded", "document_type", "id", "line_count"}

    def test_workflow_raises_on_invalid_source(self):
        with pytest.raises(UblParseError):
            ubl_installed_workflow(b"<not>valid ubl</not>")

    def test_workflow_line_count_matches_get_line_count(self):
        model = load_ubl(VALID_DIR / "multi-line-invoice.xml")
        result = ubl_installed_workflow(VALID_DIR / "multi-line-invoice.xml")
        assert result["line_count"] == get_line_count(model)


# ---------------------------------------------------------------------------
# Analytics functions against CreditNote / full-depth fixtures — the existing
# test_ubl_analytics.py only exercises minimal-invoice, multi-line-invoice,
# minimal-order, and missing-mandatory.
# ---------------------------------------------------------------------------
class TestAnalyticsAdditionalFixtures:
    def test_total_line_count_creditnote(self):
        assert ubl_total_line_count(VALID_DIR / "minimal-creditnote.xml") == 1

    def test_total_line_count_full_depth_invoice(self):
        assert ubl_total_line_count(VALID_DIR / "invoice-full-depth.xml") >= 1

    def test_supplier_name_creditnote(self):
        assert ubl_supplier_name(VALID_DIR / "minimal-creditnote.xml") == "Acme Corp"

    def test_supplier_name_full_depth_invoice(self):
        assert ubl_supplier_name(VALID_DIR / "invoice-full-depth.xml")

    def test_document_type_summary_creditnote(self):
        summary = ubl_document_type_summary(VALID_DIR / "minimal-creditnote.xml")
        assert summary == {"document_type": "CreditNote", "line_count": 1}

    def test_document_type_summary_creditnote_with_totals(self):
        summary = ubl_document_type_summary(VALID_DIR / "creditnote-with-totals.xml")
        assert summary["document_type"] == "CreditNote"
        assert summary["line_count"] >= 1


# ---------------------------------------------------------------------------
# Error classes — existence/inheritance is checked in test_ubl_smoke.py; this
# adds direct instantiation, message propagation, and catchability by the
# common base class.
# ---------------------------------------------------------------------------
class TestErrorClasses:
    def test_ubl_error_instantiation_with_message(self):
        exc = UblError("something went wrong")
        assert str(exc) == "something went wrong"

    def test_ubl_error_is_raisable_and_catchable(self):
        with pytest.raises(UblError):
            raise UblError("boom")

    def test_ubl_parse_error_instantiation(self):
        exc = UblParseError("bad xml")
        assert str(exc) == "bad xml"
        assert isinstance(exc, UblError)

    def test_ubl_parse_error_catchable_as_ubl_error(self):
        with pytest.raises(UblError):
            raise UblParseError("parse failed")

    def test_ubl_write_error_instantiation(self):
        exc = UblWriteError("cannot write")
        assert str(exc) == "cannot write"
        assert isinstance(exc, UblError)

    def test_ubl_write_error_catchable_as_ubl_error(self):
        with pytest.raises(UblError):
            raise UblWriteError("write failed")

    def test_ubl_parse_error_and_write_error_are_distinct(self):
        assert not issubclass(UblParseError, UblWriteError)
        assert not issubclass(UblWriteError, UblParseError)

    def test_ubl_tax_inconsistency_warning_is_user_warning(self):
        assert issubclass(UblTaxInconsistencyWarning, UserWarning)

    def test_ubl_tax_inconsistency_warning_instantiation(self):
        warn = UblTaxInconsistencyWarning("tax mismatch")
        assert str(warn) == "tax mismatch"

    def test_ubl_error_is_not_a_warning(self):
        assert not issubclass(UblError, Warning)


# ---------------------------------------------------------------------------
# UblDocument — fill property gaps beyond what test_ubl_codec.py::TestModel
# and test_ubl_smoke.py::TestFromFile already cover (document_type, doc_id,
# line_count, is_empty=False, repr).
# ---------------------------------------------------------------------------
class TestUblDocumentModelCoverage:
    def _sample_data(self):
        return {
            "document_type": "Invoice",
            "id": "INV-200",
            "issue_date": "2026-07-16",
            "ubl_version": "2.1",
            "currency": "USD",
            "lines": [{"id": "1", "item_name": "Widget"}, {"id": "2", "item_name": "Gadget"}],
        }

    def test_raw_property_returns_underlying_data(self):
        data = self._sample_data()
        doc = UblDocument(data)
        assert doc.raw == data

    def test_raw_property_reflects_same_object(self):
        data = self._sample_data()
        doc = UblDocument(data)
        assert doc.raw is data

    def test_issue_date_property(self):
        doc = UblDocument(self._sample_data())
        assert doc.issue_date == "2026-07-16"

    def test_issue_date_defaults_to_empty_string(self):
        doc = UblDocument({})
        assert doc.issue_date == ""

    def test_ubl_version_property(self):
        doc = UblDocument(self._sample_data())
        assert doc.ubl_version == "2.1"

    def test_ubl_version_defaults_to_empty_string(self):
        doc = UblDocument({"document_type": "Invoice"})
        assert doc.ubl_version == ""

    def test_lines_property(self):
        data = self._sample_data()
        doc = UblDocument(data)
        assert doc.lines == data["lines"]
        assert len(doc.lines) == 2

    def test_lines_defaults_to_empty_list(self):
        doc = UblDocument({})
        assert doc.lines == []

    def test_line_count_multi_line(self):
        doc = UblDocument(self._sample_data())
        assert doc.line_count == 2

    def test_is_empty_true_when_no_lines(self):
        doc = UblDocument({"document_type": "Invoice", "id": "X", "lines": []})
        assert doc.is_empty is True

    def test_is_empty_true_when_lines_key_absent(self):
        doc = UblDocument({"document_type": "Invoice", "id": "X"})
        assert doc.is_empty is True

    def test_is_empty_false_when_lines_present(self):
        doc = UblDocument(self._sample_data())
        assert doc.is_empty is False

    def test_to_dict_returns_shallow_copy(self):
        data = self._sample_data()
        doc = UblDocument(data)
        copy = doc.to_dict()
        assert copy == data
        assert copy is not data

    def test_to_dict_mutation_does_not_affect_original(self):
        data = self._sample_data()
        doc = UblDocument(data)
        copy = doc.to_dict()
        copy["id"] = "MUTATED"
        assert doc.doc_id == "INV-200"

    def test_spec_qname_class_var(self):
        assert UblDocument.spec_qname == "ubl:invoice"

    def test_from_file_creditnote(self):
        doc = UblDocument.from_file(VALID_DIR / "minimal-creditnote.xml")
        assert doc.document_type == "CreditNote"
        assert doc.doc_id == "CN-001"

    def test_from_file_order(self):
        doc = UblDocument.from_file(VALID_DIR / "minimal-order.xml")
        assert doc.document_type == "Order"
        assert doc.line_count == 1

    def test_from_file_accepts_path_object(self):
        doc = UblDocument.from_file(str(VALID_DIR / "minimal-invoice.xml"))
        assert doc.document_type == "Invoice"

    def test_repr_reflects_state(self):
        doc = UblDocument({"document_type": "Order", "id": "ORD-9"})
        assert repr(doc) == "UblDocument(type='Order', id='ORD-9')"


# ---------------------------------------------------------------------------
# cli.py::main() — previously untested entry point.
# ---------------------------------------------------------------------------
class TestCliProbeCommand:
    def test_probe_valid_file_exits_zero(self, capsys):
        target = VALID_DIR / "minimal-invoice.xml"
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(target)])
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["probe"] is True
        assert payload["file"] == str(target)

    def test_probe_nonexistent_file_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(VALID_DIR / "does-not-exist.xml")])
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["probe"] is False

    def test_probe_order_file_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(VALID_DIR / "minimal-order.xml")])
        assert exc_info.value.code == 0

    def test_probe_non_ubl_xml_exits_one(self, capsys, tmp_path):
        bad_file = tmp_path / "not_ubl.xml"
        bad_file.write_text('<?xml version="1.0"?><root/>', encoding="utf-8")
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["probe", str(bad_file)])
        assert exc_info.value.code == 1


class TestCliLoadCommand:
    def test_load_valid_file_prints_json_model(self, capsys):
        target = VALID_DIR / "minimal-invoice.xml"
        cli.main(["load", str(target)])
        out = capsys.readouterr().out
        model = json.loads(out)
        assert model["document_type"] == "Invoice"
        assert model["id"] == "INV-001"

    def test_load_creditnote_prints_line_items(self, capsys):
        cli.main(["load", str(VALID_DIR / "minimal-creditnote.xml")])
        out = capsys.readouterr().out
        model = json.loads(out)
        assert model["document_type"] == "CreditNote"
        assert len(model["lines"]) == 1

    def test_load_does_not_raise_system_exit(self):
        # The "load" branch has no sys.exit() call — main() should return
        # normally (None) rather than raising SystemExit.
        result = cli.main(["load", str(VALID_DIR / "minimal-order.xml")])
        assert result is None

    def test_load_nonexistent_file_raises_parse_error(self):
        with pytest.raises(UblParseError):
            cli.main(["load", str(VALID_DIR / "does-not-exist.xml")])

    def test_load_malformed_xml_raises_parse_error(self, tmp_path):
        bad_file = tmp_path / "malformed.xml"
        bad_file.write_text("<not>closed", encoding="utf-8")
        with pytest.raises(UblParseError):
            cli.main(["load", str(bad_file)])


class TestCliNoCommand:
    def test_no_command_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            cli.main([])
        assert exc_info.value.code == 1

    def test_no_command_prints_help(self, capsys):
        with pytest.raises(SystemExit):
            cli.main([])
        out = capsys.readouterr().out
        assert "ff-ubl" in out or "usage" in out.lower()


class TestCliArgumentParsing:
    def test_probe_requires_file_argument(self):
        with pytest.raises(SystemExit):
            cli.main(["probe"])

    def test_load_requires_file_argument(self):
        with pytest.raises(SystemExit):
            cli.main(["load"])

    def test_main_accepts_none_argv(self, monkeypatch, capsys):
        # main(None) falls back to argparse reading sys.argv; simulate an
        # empty invocation via monkeypatched sys.argv.
        monkeypatch.setattr(sys, "argv", ["ff-ubl"])
        with pytest.raises(SystemExit) as exc_info:
            cli.main(None)
        assert exc_info.value.code == 1
