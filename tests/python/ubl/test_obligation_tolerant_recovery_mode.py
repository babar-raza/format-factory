"""UBL-LIFECYCLE-001 -- a genuine tolerant/recovery read mode.

MUST, quoted from the format contract (SAL-UBL-OBL-6C91BBF7F11E4402):

  "Support a strict read mode that rejects malformed input with
   diagnostics and a tolerant read mode that recovers where the format
   permits, with recovery actions reported."

reader.py's own `_parse` has exactly three raise sites: malformed XML
syntax, an unrecognized document root name, and a root namespace
mismatch. The first two are genuinely unrecoverable (there is either no
tree at all, or no typed document class to build without a recognized
root name) and stay hard failures under both modes, matching
test_obligation_read_mode_lifecycle.py's own characterization for
malformed XML. The third -- a root namespace mismatch -- is the one
genuinely recoverable defect: `find()`/`find_all()` (model/typed.py) are
already documented as matching by LOCAL NAME ONLY, never by namespace, so
a document whose root carries the wrong namespace is still fully
field-accessible once built; the mismatch is purely a structural sanity
check the rest of the object model never depended on.

probe() is deliberately switched from mode="preservation" to
mode="strict" as part of this same slice: before this obligation had any
real recovery behavior, that choice was a no-op; recognizing a
namespace-mismatched document as "this is UBL" is not what a probe's own
yes/no judgment should mean, and the pre-existing
test_wrong_namespace_and_preview_profile_fail_closed /
test_production_namespace.py::probe assertions already depend on strict
rejection.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import loads, probe
from format_factory.ubl.errors import UblParseError
from format_factory.ubl.model.typed import find

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_INVOICE_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
_ORDER_NS = "urn:oasis:names:specification:ubl:schema:xsd:Order-2"


def _invoice(namespace: str) -> bytes:
    return (
        f'<Invoice xmlns="{namespace}" xmlns:cbc="{_CBC}">'
        "<cbc:ID>INV-1</cbc:ID>"
        "<cbc:UBLVersionID>2.3</cbc:UBLVersionID>"
        "</Invoice>"
    ).encode()


class TestNamespaceMismatch:
    def test_strict_mode_refuses_a_namespace_mismatch(self) -> None:
        with pytest.raises(UblParseError, match="namespace mismatch"):
            loads(_invoice(_ORDER_NS), mode="strict")

    def test_preservation_mode_recovers_a_namespace_mismatch(self) -> None:
        document = loads(_invoice(_ORDER_NS), mode="preservation")
        assert document.root_name == "Invoice"
        assert len(document.recovery_actions) == 1
        assert "namespace mismatch" in document.recovery_actions[0]
        assert "Invoice" in document.recovery_actions[0]

    def test_recovered_document_is_fully_field_accessible(self) -> None:
        document = loads(_invoice(_ORDER_NS), mode="preservation")
        node = find(document.root, "ID")
        assert node is not None
        assert node.text == "INV-1"

    def test_default_mode_is_strict_and_still_refuses(self) -> None:
        with pytest.raises(UblParseError, match="namespace mismatch"):
            loads(_invoice(_ORDER_NS))


class TestCleanDocumentUnaffected:
    def test_a_correctly_namespaced_document_has_no_recovery_actions(self) -> None:
        strict_doc = loads(_invoice(_INVOICE_NS), mode="strict")
        preservation_doc = loads(_invoice(_INVOICE_NS), mode="preservation")
        assert strict_doc.recovery_actions == ()
        assert preservation_doc.recovery_actions == ()

    def test_a_document_built_directly_in_memory_has_no_recovery_actions(self) -> None:
        from format_factory.ubl.model import XmlNode
        from format_factory.ubl.model.root_types import Invoice

        root = XmlNode.create(f"{{{_INVOICE_NS}}}Invoice")
        document = Invoice(root)
        assert document.recovery_actions == ()


class TestUnrecoverableDefectsStayHardFailuresInBothModes:
    def test_malformed_xml_syntax_is_never_recoverable(self) -> None:
        malformed = f'<Invoice xmlns="{_INVOICE_NS}"><bad'.encode()
        with pytest.raises(UblParseError, match="malformed XML"):
            loads(malformed, mode="strict")
        with pytest.raises(UblParseError, match="malformed XML"):
            loads(malformed, mode="preservation")

    def test_an_unrecognized_root_name_is_never_recoverable(self) -> None:
        xml = b'<NotARealUblRoot xmlns="urn:example:not-ubl"/>'
        with pytest.raises(UblParseError, match="unsupported UBL document root"):
            loads(xml, mode="strict")
        with pytest.raises(UblParseError, match="unsupported UBL document root"):
            loads(xml, mode="preservation")


class TestProbeStaysStrict:
    def test_probe_rejects_a_namespace_mismatched_document(self) -> None:
        result = probe(_invoice(_ORDER_NS))
        assert result.matched is False

    def test_probe_accepts_a_correctly_namespaced_document(self) -> None:
        result = probe(_invoice(_INVOICE_NS))
        assert result.matched is True

    def test_probe_still_rejects_a_bare_unnamespaced_element(self) -> None:
        assert probe(b"<Invoice/>").matched is False
