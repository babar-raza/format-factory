"""UBL-REF-001 against the shipped namespace.

MUST (source_field: required_behavior): "Index identifiers and references;
detect duplicate IDs, broken references, and inconsistent line references
with locations."

required_tests: "Duplicate-ID and broken-reference fixtures produce complete
diagnostics."

Scope of this file: `DocumentIndex.duplicate_line_ids()`, which detects two
or more line-role components (cac:InvoiceLine, cac:CreditNoteLine, ...)
sharing the same own identifier, with every occurrence's path. Deliberately
scoped to the "line" business role rather than every identifier in the
document: cbc:ID is a generic identifier component reused for unrelated
business identifier schemes (a party identifier, a line number, an item
code), so treating any two matching ID strings anywhere in the document as
"duplicates" would flag a Party ID of "1" and a Line ID of "1" as a
conflict when they are not -- they are different identifier namespaces
that happen to share a string. Line identifiers are the one place UBL
actually expects document-scoped uniqueness for, since cross-references
(tax/allowance calculations, order-line matching) correlate against them.

Deliberately NOT attempted here: cross-document reference resolution (a
cac:OrderReference/cbc:ID pointing at a *different* Order document's own
ID cannot be verified from one document in isolation -- this library has
no multi-document context), and completeness-checking of wrapper-vs-leaf
"*Reference" elements (distinguishing cac:BillingReference, which wraps a
nested reference and carries no ID of its own by design, from a genuinely
incomplete leaf reference would require verified UBL schema data on which
Reference-suffixed elements are wrappers, which is not available from the
SAL facts backing this obligation). Both remain `missing_behavior` on this
capability's evidence, not implemented.
"""

from __future__ import annotations

from format_factory.ubl import DocumentIndex, DuplicateId, loads

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice(*, line_ids: tuple[str, ...], party_id: str = "SUPPLIER-1") -> str:
    lines = "\n".join(
        f"""<cac:InvoiceLine>
  <cbc:ID>{line_id}</cbc:ID>
  <cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">1.00</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>
</cac:InvoiceLine>"""
        for line_id in line_ids
    )
    return f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:ID>INV-001</cbc:ID>
<cac:AccountingSupplierParty>
  <cac:Party><cbc:ID>{party_id}</cbc:ID></cac:Party>
</cac:AccountingSupplierParty>
{lines}
</Invoice>"""


def _index(*, line_ids: tuple[str, ...], party_id: str = "SUPPLIER-1") -> DocumentIndex:
    root = loads(_invoice(line_ids=line_ids, party_id=party_id)).root
    return DocumentIndex(root)


# ── No duplicates ────────────────────────────────────────────────────────────


def test_unique_line_ids_report_no_duplicates() -> None:
    index = _index(line_ids=("1", "2", "3"))

    assert index.duplicate_line_ids() == ()


# ── A genuine duplicate ──────────────────────────────────────────────────────


def test_two_lines_sharing_an_id_are_reported_as_duplicates() -> None:
    index = _index(line_ids=("1", "1", "2"))

    duplicates = index.duplicate_line_ids()

    assert len(duplicates) == 1
    (duplicate,) = duplicates
    assert isinstance(duplicate, DuplicateId)
    assert duplicate.identifier == "1"
    assert len(duplicate.matches) == 2


def test_duplicate_report_carries_the_path_of_every_occurrence() -> None:
    """"... with locations." A caller must be able to tell WHERE each
    conflicting line lives, not just that a conflict exists."""
    index = _index(line_ids=("1", "1"))

    (duplicate,) = index.duplicate_line_ids()

    paths = {match.path for match in duplicate.matches}
    assert len(paths) == 2  # distinct paths, not the same node twice
    for path in paths:
        assert path[-1].startswith("InvoiceLine[")


def test_three_lines_sharing_an_id_report_all_three_occurrences() -> None:
    index = _index(line_ids=("1", "1", "1"))

    (duplicate,) = index.duplicate_line_ids()

    assert len(duplicate.matches) == 3


def test_multiple_distinct_duplicate_groups_are_all_reported() -> None:
    index = _index(line_ids=("1", "1", "2", "2", "3"))

    duplicates = index.duplicate_line_ids()

    identifiers = {d.identifier for d in duplicates}
    assert identifiers == {"1", "2"}


# ── No false positives across unrelated identifier namespaces ──────────────


def test_a_party_id_matching_a_line_id_is_not_a_false_positive() -> None:
    """cbc:ID is reused across unrelated business identifier schemes. A
    Party sharing its identifier string with a (unique) line is not a
    referential defect -- they are different identifier namespaces."""
    index = _index(line_ids=("1", "2"), party_id="1")

    assert index.duplicate_line_ids() == ()


def test_duplicate_line_ids_is_empty_for_a_single_line_document() -> None:
    index = _index(line_ids=("1",))

    assert index.duplicate_line_ids() == ()
