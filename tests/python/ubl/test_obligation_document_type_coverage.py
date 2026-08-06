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
    create_empty,
    detect_document_type,
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
