"""UBL-WRITE-001 -- "Write elements in schema-valid order independent of
mutation order; offer canonical prefix/formatting policies and lossless
mode preserving significant lexical values."

MUST (SAL-UBL-OBL-4BD9BBC9F974C175): "Same confirmed gap as SAL-UBL-OBL-
3B43504E9C74003C (UBL-MODEL-001, element order) ... nothing in the writer
reorders elements assembled in arbitrary order into schema-valid
sequence."

This obligation has three distinct clauses, and this slice proves two of
them are already genuinely true (previously untested from this angle,
discovered while investigating the obligation) while honestly leaving the
third unbuilt:

1. "canonical prefix ... policies": dumps() already normalizes ANY source
   namespace prefix alias to the package's own canonical cbc:/cac:/ext:
   prefixes via ET.register_namespace(), regardless of what prefix the
   original document used -- proven directly here for the first time.

2. "lossless mode preserving significant lexical values": already proven
   by test_obligation_preservation_mode.py's TestPreservationModeDefault
   class (PreservationMode.LOSSLESS is the default and preserves the
   extension container byte-for-byte) -- cited, not re-proven, here.

3. "write elements in schema-valid order independent of mutation order":
   dumps() now REFUSES (via validate()'s integration, added when the
   element-order validation cluster was built) to serialize a document
   whose already-checked components have elements in the wrong relative
   order, rather than silently reordering them -- proven directly here for
   the first time. This is a genuinely different design from "independent
   of mutation order" (which would mean the writer silently fixes bad
   order rather than refusing it): a caller who assembles a Party with
   Contact before PostalAddress gets a clear UblWriteError, not silently
   reordered output. Automatic reordering remains honestly unbuilt --
   this obligation's own rule_text asks for the writer not to CARE what
   order fields were assembled in, and refusal is not the same guarantee
   as always producing valid output regardless of input order.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblWriteError, dumps, loads

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_INVOICE_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"


def test_dumps_normalizes_a_non_standard_source_prefix_to_the_canonical_cbc_prefix() -> None:
    xml = (
        f'<Invoice xmlns="{_INVOICE_NS}" '
        f'xmlns:ns1="{_CBC}">'
        f"<ns1:ID>INV-001</ns1:ID>"
        f"</Invoice>"
    ).encode()

    document = loads(xml)
    out = dumps(document)

    assert b"cbc:ID" in out
    assert b"ns1:" not in out


def test_dumps_normalizes_a_non_standard_cac_prefix_alias_too() -> None:
    xml = (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:x="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<x:AccountingSupplierParty><x:Party><x:PostalAddress>"
        f"<cbc:CityName>City</cbc:CityName>"
        f"</x:PostalAddress></x:Party></x:AccountingSupplierParty>"
        f"</Invoice>"
    ).encode()

    document = loads(xml)
    out = dumps(document)

    assert b"cac:AccountingSupplierParty" in out
    assert b"x:AccountingSupplierParty" not in out


def test_dumps_refuses_to_write_a_document_with_checked_components_in_the_wrong_order() -> None:
    """dumps() now enforces the same schema-valid-order requirement
    validate() checks, via its own pre-existing 'refuse invalid documents'
    behavior -- a Party with Contact before PostalAddress cannot be
    written at all."""
    xml = (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AccountingSupplierParty><cac:Party>"
        f"<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
        f"<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>"
        f"</cac:Party></cac:AccountingSupplierParty>"
        f"</Invoice>"
    ).encode()

    document = loads(xml)

    with pytest.raises(UblWriteError, match="PostalAddress"):
        dumps(document)


def test_dumps_writes_a_document_with_checked_components_in_correct_order_without_incident() -> None:
    xml = (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AccountingSupplierParty><cac:Party>"
        f"<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>"
        f"<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
        f"</cac:Party></cac:AccountingSupplierParty>"
        f"</Invoice>"
    ).encode()

    document = loads(xml)
    out = dumps(document)

    assert b"cac:PostalAddress" in out
