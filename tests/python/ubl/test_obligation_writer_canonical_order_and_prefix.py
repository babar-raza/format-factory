"""UBL-WRITE-001 -- "Write elements in schema-valid order independent of
mutation order; offer canonical prefix/formatting policies and lossless
mode preserving significant lexical values."

MUST (SAL-UBL-OBL-4BD9BBC9F974C175): "Same confirmed gap as SAL-UBL-OBL-
3B43504E9C74003C (UBL-MODEL-001, element order) ... nothing in the writer
reorders elements assembled in arbitrary order into schema-valid
sequence."

This obligation has three distinct clauses; this slice proves all three:

1. "canonical prefix ... policies": dumps() already normalizes ANY source
   namespace prefix alias to the package's own canonical cbc:/cac:/ext:
   prefixes via ET.register_namespace(), regardless of what prefix the
   original document used -- proven directly here for the first time.

2. "lossless mode preserving significant lexical values": already proven
   by test_obligation_preservation_mode.py's TestPreservationModeDefault
   class (PreservationMode.LOSSLESS is the default and preserves the
   extension container byte-for-byte) -- cited, not re-proven, here.

3. "write elements in schema-valid order independent of mutation order":
   FF6-EVENT-000286 closes this clause. dumps() previously REFUSED (via
   validate()'s own integration) to serialize a document whose already-
   checked components had elements in the wrong relative order --
   refusal, not the "independent of mutation order" guarantee this
   obligation's own rule_text asks for. validate.validator.
   reorder_for_schema_order() now runs before validation on every
   dumps()/dump() call, permuting only the positions already occupied by
   an already-modeled, order-checked field (the same
   _ORDER_CHECKED_COMPONENTS ground truth _order_diagnostics validates
   against) into their schema-declared relative sequence -- a caller who
   assembles a Party with Contact before PostalAddress now gets schema-
   valid output regardless, not a raised UblWriteError.
"""

from __future__ import annotations

from format_factory.ubl import dumps, loads

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


def test_dumps_reorders_a_document_with_checked_components_in_the_wrong_order() -> None:
    """SAL-UBL-OBL-4BD9BBC9F974C175 (UBL-WRITE-001): "write elements in
    schema-valid order independent of mutation order." dumps() no longer
    refuses a Party with Contact before PostalAddress -- it reorders the
    two known-order fields into their schema-declared sequence and writes
    successfully."""
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

    output = dumps(document)

    assert output.index(b"PostalAddress") < output.index(b"Contact")


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
