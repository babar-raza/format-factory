"""UBL-LIFECYCLE-001 -- detected vs. declared version, never silently rewritten.

MUST: "Expose the detected format version and any declared version
separately; never silently rewrite a declared version."

Before this slice, UblDocument had no version-related field or accessor at
all: cbc:UBLVersionID was checked inline, ad hoc, only inside validate()
(hardcoded to require exactly "2.3" for the stable profile), with no way
for a caller to read "what version did this file actually declare" as a
first-class value, and no distinction between what was originally read
and what the tree currently says after an edit.

`detected_version` is set once, only by document_from_root() (the parser's
own document constructor), from the UBLVersionID the source file actually
contained; it survives with_root()-based edits unchanged. `declared_version`
is a live property reading the current tree's UBLVersionID, so it reflects
edits immediately. A freshly hand-built document (UblDocument.build(), no
parsing involved) has detected_version=None -- nothing was detected,
because nothing was read.

The writer (codec/writer/writer.py's dumps()/dump()) never touches
document content at all -- it walks the XmlNode tree verbatim -- so "never
silently rewrite a declared version" is a structural guarantee, not a
runtime check; this file proves it empirically via round-trip.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import ROOT_CLASSES, XmlNode, dumps, loads, ubl_version_id
from format_factory.ubl.errors import UblWriteError

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
Invoice = ROOT_CLASSES["Invoice"]


def _invoice(version: str = "2.3") -> bytes:
    return (
        f'<Invoice xmlns="{NAMESPACE}" xmlns:cbc="{CBC}">'
        f"<cbc:UBLVersionID>{version}</cbc:UBLVersionID>"
        "<cbc:ID>INV-001</cbc:ID>"
        "</Invoice>"
    ).encode()


# ── detected_version: set once, by the parser, from the real source ────────


def test_a_freshly_built_document_has_no_detected_version() -> None:
    document = Invoice.build(children=(XmlNode.create(f"{{{CBC}}}ID", text="INV-1"),))

    assert document.detected_version is None


def test_loading_a_file_records_its_actual_declared_version_as_detected() -> None:
    document = loads(_invoice("2.3"))

    assert document.detected_version == "2.3"


def test_detected_version_reflects_whatever_the_source_actually_said() -> None:
    """Not hardcoded to "2.3" -- loads() must record what the file said, not
    what the stable profile happens to require."""
    document = loads(_invoice("2.1"))

    assert document.detected_version == "2.1"


def test_detected_version_survives_a_with_root_edit_unchanged() -> None:
    """Editing the document (e.g. adding an unrelated extension) must not
    erase the memory of what was originally read."""
    document = loads(_invoice("2.3"))
    edited = document.with_root(
        document.root.with_children(
            (*document.root.children, XmlNode.create(f"{{{CBC}}}Note", text="edited"))
        )
    )

    assert edited.detected_version == "2.3"


# ── declared_version: live, reflects the current tree ───────────────────────


def test_declared_version_reads_the_current_trees_ublversionid() -> None:
    document = loads(_invoice("2.3"))

    assert document.declared_version == "2.3"


def test_declared_version_is_none_when_ublversionid_is_absent() -> None:
    document = Invoice.build(children=(XmlNode.create(f"{{{CBC}}}ID", text="INV-1"),))

    assert document.declared_version is None


def test_declared_version_is_an_empty_string_when_explicitly_empty() -> None:
    """Distinct from absence: an explicitly present but empty
    cbc:UBLVersionID is not collapsed to None."""
    document = loads(_invoice(""))

    assert document.declared_version == ""
    assert document.declared_version is not None


def test_editing_the_version_element_changes_declared_but_not_detected() -> None:
    """The obligation's own distinction, directly: an edit changes what is
    declared without silently rewriting what was detected."""
    document = loads(_invoice("2.3"))
    version_index = next(
        index
        for index, child in enumerate(document.root.children)
        if child.qname == f"{{{CBC}}}UBLVersionID"
    )
    new_children = list(document.root.children)
    new_children[version_index] = XmlNode.create(f"{{{CBC}}}UBLVersionID", text="2.4")
    edited = document.with_root(document.root.with_children(tuple(new_children)))

    assert edited.declared_version == "2.4"
    assert edited.detected_version == "2.3"


def test_ubl_version_id_helper_matches_the_declared_version_property() -> None:
    document = loads(_invoice("2.3"))

    assert ubl_version_id(document.root) == document.declared_version


# ── The writer never silently rewrites a declared version ──────────────────


def test_dumps_refuses_rather_than_silently_rewriting_an_unsupported_version() -> None:
    """dumps() validates before writing, and the stable profile accepts only
    "2.3" (validation/validator.py). A document declaring "2.1" is refused
    outright -- dumps() has no code path that could coerce it to "2.3" and
    write anyway, which is what "never silently rewrite" rules out most
    directly: not wrong output, but no silent substitution at all."""
    document = loads(_invoice("2.1"))

    with pytest.raises(UblWriteError, match="2.1"):
        dumps(document)

    assert document.declared_version == "2.1"


def test_repeated_round_trips_never_drift_the_declared_version() -> None:
    document = loads(_invoice("2.3"))

    once = loads(dumps(document))
    twice = loads(dumps(once))

    assert once.declared_version == "2.3"
    assert twice.declared_version == "2.3"
