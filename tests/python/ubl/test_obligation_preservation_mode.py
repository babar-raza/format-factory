"""UBL-PRESERVE-001 -- explicit LOSSLESS-vs-CANONICAL dump mode, and a
first-class loss-reporting API.

MUST, quoted from the format contract (SAL-UBL-OBL-5A831127B0AA359F,
SAL-UBL-OBL-79F230CE7F5852E9):

  "dumps()/dump() take no preservation-mode parameter at all -- there is
   exactly one output path" -- closed by threading a keyword-only ``mode:
   PreservationMode`` parameter through the real, exported ``dumps()``/
   ``dump()`` in codec/writer/writer.py, defaulting to LOSSLESS (the
   historical, unchanged behavior).
  "no LossReport/check_preservation-style API exists anywhere in this
   package" -- closed by ``codec.preservation.check_preservation()``.

Scope, quoted from the evidence YAML's own honesty note: unlike XLIFF's
ExtensionNode, this model's XmlNode tree is fully generic -- there is no
modeled/unmodeled split anywhere in it. The one place the UBL
specification itself draws that line is the root-level
ext:UBLExtensions container (the schema family's own dedicated vendor/
customization extension slot). CANONICAL mode drops that one container
when present as a direct child of the document root; every other
element -- the entire core business-document tree -- is preserved in
both modes. This file tests exactly that scope.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    ROOT_CLASSES,
    LossReport,
    PreservationMode,
    UblWriteError,
    XmlNode,
    canonicalize,
    check_preservation,
    dump,
    dumps,
    loads,
)

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_EXT_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
_EXT_QNAME = f"{{{_EXT_NS}}}UBLExtensions"
_INVOICE_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
Invoice = ROOT_CLASSES["Invoice"]


def _extensions_container(payload: str = "vendor payload") -> XmlNode:
    return XmlNode.create(
        _EXT_QNAME,
        children=(
            XmlNode.create(
                f"{{{_EXT_NS}}}UBLExtension",
                children=(
                    XmlNode.create(f"{{{_EXT_NS}}}ExtensionContent", text=payload),
                ),
            ),
        ),
    )


def _version_node(version: str = "2.3") -> XmlNode:
    return XmlNode.create(f"{{{_CBC}}}UBLVersionID", text=version)


def _id_node(value: str = "INV-001") -> XmlNode:
    return XmlNode.create(f"{{{_CBC}}}ID", text=value)


def _clean_document():
    return Invoice.build(children=(_version_node(), _id_node()))


def _document_with_extensions():
    return Invoice.build(
        children=(_extensions_container(), _version_node(), _id_node())
    )


class TestPreservationModeDefault:
    def test_default_mode_is_lossless(self) -> None:
        doc = _document_with_extensions()
        assert dumps(doc) == dumps(doc, mode=PreservationMode.LOSSLESS)

    def test_lossless_mode_preserves_extension_container(self) -> None:
        doc = _document_with_extensions()
        out = dumps(doc, mode=PreservationMode.LOSSLESS)
        assert b"UBLExtensions" in out
        assert b"vendor payload" in out

    def test_lossless_dump_roundtrips_through_load(self, tmp_path) -> None:
        doc = _document_with_extensions()
        destination = tmp_path / "lossless.xml"
        dump(doc, destination, mode=PreservationMode.LOSSLESS)
        reloaded = loads(destination.read_bytes())
        report = check_preservation(reloaded)
        assert report.dropped_count == 1

    def test_unknown_mode_string_rejected(self) -> None:
        with pytest.raises(UblWriteError):
            dumps(_clean_document(), mode="not-a-real-mode")  # type: ignore[arg-type]

    def test_plain_string_matching_enum_value_is_accepted(self) -> None:
        doc = _document_with_extensions()
        assert dumps(doc, mode="canonical") == dumps(  # type: ignore[arg-type]
            doc, mode=PreservationMode.CANONICAL
        )


class TestPreservationModeCanonical:
    def test_canonical_mode_drops_root_extensions_container(self) -> None:
        doc = _document_with_extensions()
        out = dumps(doc, mode=PreservationMode.CANONICAL)
        assert b"UBLExtensions" not in out
        assert b"vendor payload" not in out
        assert b"INV-001" in out

    def test_canonical_mode_output_still_loads_and_validates(self, tmp_path) -> None:
        doc = _document_with_extensions()
        destination = tmp_path / "canonical.xml"
        dump(doc, destination, mode=PreservationMode.CANONICAL)
        reloaded = loads(destination.read_bytes())
        assert check_preservation(reloaded).is_lossless is True

    def test_canonical_mode_is_noop_when_no_extensions_present(self) -> None:
        doc = _clean_document()
        assert dumps(doc, mode=PreservationMode.LOSSLESS) == dumps(
            doc, mode=PreservationMode.CANONICAL
        )

    def test_canonical_mode_preserves_non_extension_siblings(self) -> None:
        doc = Invoice.build(
            children=(
                _extensions_container(),
                _version_node(),
                _id_node("INV-999"),
                XmlNode.create(f"{{{_CBC}}}IssueDate", text="2026-01-01"),
            )
        )
        out = dumps(doc, mode=PreservationMode.CANONICAL)
        assert b"INV-999" in out
        assert b"2026-01-01" in out

    def test_canonical_mode_only_drops_root_level_extensions_not_nested(self) -> None:
        # An element that merely shares the extensions QName but is nested
        # deeper than a direct root child must not be treated as the
        # spec-defined container -- only a direct root child qualifies.
        nested_holder = XmlNode.create(
            f"{{{_CBC}}}ID",
            children=(_extensions_container("nested, not a root child"),),
            text="INV-002",
        )
        doc = Invoice.build(children=(_version_node(), nested_holder))
        out = dumps(doc, mode=PreservationMode.CANONICAL)
        assert b"nested, not a root child" in out


class TestCanonicalizeDoesNotMutateOriginal:
    def test_original_document_children_unchanged(self) -> None:
        doc = _document_with_extensions()
        original_count = len(doc.root.children)
        canonical_doc, dropped = canonicalize(doc)
        assert len(doc.root.children) == original_count
        assert len(canonical_doc.root.children) == original_count - 1
        assert dropped == (_EXT_QNAME,)

    def test_canonicalize_is_identity_when_nothing_to_drop(self) -> None:
        doc = _clean_document()
        canonical_doc, dropped = canonicalize(doc)
        assert canonical_doc is doc
        assert dropped == ()

    def test_canonicalize_invalidates_signature_assertion(self) -> None:
        # with_root() (used internally by canonicalize when it drops
        # something) resets source_sha256/signed_content_sha256 -- correct,
        # since the serialized content genuinely changed. Prove it against
        # a document that starts with those fields actually set, not just
        # a freshly-built one where they default to None already.
        base = _document_with_extensions()
        signed = type(base)(
            root=base.root, source_sha256="deadbeef", signed_content_sha256="deadbeef"
        )
        assert signed.source_sha256 == "deadbeef"
        canonical_doc, dropped = canonicalize(signed)
        assert dropped == (_EXT_QNAME,)
        assert canonical_doc.source_sha256 is None
        assert canonical_doc.signed_content_sha256 is None


class TestCheckPreservation:
    def test_clean_document_reports_lossless(self) -> None:
        report = check_preservation(_clean_document())
        assert isinstance(report, LossReport)
        assert report.is_lossless is True
        assert report.dropped_count == 0
        assert report.dropped_tags == ()

    def test_document_with_extensions_reports_lossy(self) -> None:
        report = check_preservation(_document_with_extensions())
        assert report.is_lossless is False
        assert report.dropped_count == 1
        assert report.dropped_tags == (_EXT_QNAME,)

    def test_report_detail_is_a_string_naming_the_count(self) -> None:
        report = check_preservation(_document_with_extensions())
        assert isinstance(report.detail, str)
        assert str(report.dropped_count) in report.detail

    def test_check_preservation_matches_canonicalize_drop_count(self) -> None:
        doc = _document_with_extensions()
        report = check_preservation(doc)
        _canonical, dropped = canonicalize(doc)
        assert report.dropped_count == len(dropped)


class TestLoadedDocumentPreservationReport:
    def test_real_parsed_extensions_container_reports_lossy(self) -> None:
        xml = (
            f'<Invoice xmlns="{_INVOICE_NAMESPACE}" xmlns:cbc="{_CBC}" xmlns:ext="{_EXT_NS}">'
            "<ext:UBLExtensions>"
            "<ext:UBLExtension><ext:ExtensionContent>x</ext:ExtensionContent></ext:UBLExtension>"
            "</ext:UBLExtensions>"
            "<cbc:UBLVersionID>2.3</cbc:UBLVersionID>"
            "<cbc:ID>INV-100</cbc:ID>"
            "</Invoice>"
        ).encode()
        doc = loads(xml)
        report = check_preservation(doc)
        assert report.is_lossless is False
        assert report.dropped_count == 1

    def test_real_document_without_extensions_reports_lossless(self) -> None:
        xml = (
            f'<Invoice xmlns="{_INVOICE_NAMESPACE}" xmlns:cbc="{_CBC}">'
            "<cbc:UBLVersionID>2.3</cbc:UBLVersionID>"
            "<cbc:ID>INV-101</cbc:ID>"
            "</Invoice>"
        ).encode()
        doc = loads(xml)
        assert check_preservation(doc).is_lossless is True
