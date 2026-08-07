"""UBL-DOCTYPES-001 -- programmatic document-type coverage operations.

MUST (SAL-UBL-OBL-1ACFBE52C6642031 / SAL-UBL-OBL-8DA615FF51A38A5A):
"Expose a distinct typed root per supported document type plus
create_empty, detect_document_type, and supported_document_types
operations ... so integrations enumerate coverage programmatically."

Before this slice, the typed-root capability existed (ROOT_CLASSES,
UblDocument.build(), loads()) but not under these named operations --
an integration wanting to enumerate coverage, detect a document's type,
or construct an empty instance of a named type had to reach into
model.root_types directly rather than use a stable top-level API.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    ROOT_CLASSES,
    DocumentTypeCoverage,
    create_empty,
    detect_document_type,
    document_type_coverage,
    document_type_coverage_manifest,
    dumps,
    supported_document_types,
)


def test_supported_document_types_matches_the_pinned_root_inventory() -> None:
    types = supported_document_types()

    assert len(types) == 91
    assert set(types) == set(ROOT_CLASSES)
    assert types == tuple(sorted(types))


def test_create_empty_builds_a_minimal_valid_document() -> None:
    document = create_empty("Invoice")

    assert isinstance(document, ROOT_CLASSES["Invoice"])
    assert document.root_name == "Invoice"


def test_create_empty_refuses_an_unsupported_document_type() -> None:
    with pytest.raises(ValueError, match="unsupported UBL document type"):
        create_empty("NotARealUblDocumentType")


def test_detect_document_type_reads_a_freshly_written_document() -> None:
    written = dumps(create_empty("CreditNote"))

    assert detect_document_type(written) == "CreditNote"


@pytest.mark.parametrize("root_name", sorted(ROOT_CLASSES))
def test_create_empty_and_detect_document_type_round_trip_every_root(
    root_name: str,
) -> None:
    written = dumps(create_empty(root_name))

    assert detect_document_type(written) == root_name


# ── SAL-UBL-OBL-4AEF6E978EC11AA1: the three-tier coverage vocabulary ───────


def test_a_supported_root_reports_the_supported_tier() -> None:
    """"Document-type coverage is declared per type... never claimed
    globally" -- a per-name classification, not a single blanket fact."""
    assert document_type_coverage("Invoice") == DocumentTypeCoverage.SUPPORTED


def test_an_unrecognized_root_name_reports_the_unsupported_tier() -> None:
    assert (
        document_type_coverage("NotARealUblDocumentType")
        == DocumentTypeCoverage.UNSUPPORTED
    )


@pytest.mark.parametrize("root_name", sorted(ROOT_CLASSES))
def test_every_known_root_reports_supported(root_name: str) -> None:
    """All 91 UBL 2.3 root types this package recognizes are fully typed
    today -- there is currently no preservation-only tier in practice."""
    assert document_type_coverage(root_name) == DocumentTypeCoverage.SUPPORTED


def test_the_coverage_manifest_covers_every_supported_type_exactly_once() -> None:
    manifest = document_type_coverage_manifest()

    assert set(manifest) == set(supported_document_types())
    assert all(value == DocumentTypeCoverage.SUPPORTED for value in manifest.values())


def test_the_coverage_vocabulary_names_all_three_tiers() -> None:
    """The obligation names the vocabulary itself as the requirement --
    proving the enum carries all three tiers, not only the two currently
    reachable from this package's own data."""
    assert {tier.value for tier in DocumentTypeCoverage} == {
        "supported",
        "preservation_only",
        "unsupported",
    }
