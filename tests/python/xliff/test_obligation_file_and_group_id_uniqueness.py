"""XLIFF-PARSE-001 against the shipped namespace.

MUST (SAL-XLIFF-OBL-087892B36F8591FF): "(XLIFF core - file element) The
xliff root element contains one or more file elements each carrying an
id attribute unique within the document."

MUST (SAL-XLIFF-OBL-EC188D4F6DD138A0, partial): "(XLIFF core - identifier
constraints) id attributes on file group unit and inline elements must be
unique within their specification-defined scope and references must
resolve."

Before this slice: xliff.file.id.duplicate already existed in
validator.py but no shipped test built a real multi-file document to
exercise it. Group-id duplicate detection did not exist in the validator
at all. Per the pinned XLIFF 2.1 specification's own identifier-scope
rules (section 3.1, "Selectors for Core Elements", and the identical
scope table in section 4.9): a file id must be unique among all file ids
within the enclosing xliff element (document-wide), and a group id must
be unique among all group ids within the enclosing file element
(file-wide, but not document-wide) -- both flatten across nesting depth,
the same way unit ids already do via file.iter_units().

"references must resolve" (e.g. mrk ref, dataRef) beyond the existing
ec/sc pairing check remains genuinely unbuilt and is not attempted here
-- this file closes only the file-id and group-id uniqueness halves of
SAL-XLIFF-OBL-EC188D4F6DD138A0, and fully closes SAL-XLIFF-OBL-087892B36F8591FF.
"""

from __future__ import annotations

from format_factory.xliff import loads, validate

_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _document(body: str) -> bytes:
    return f'<xliff xmlns="{_NS}" version="2.1" srcLang="en">{body}</xliff>'.encode()


def _file(file_id: str, group_id: str, unit_id: str, segment_id: str) -> str:
    return (
        f'<file id="{file_id}"><group id="{group_id}">'
        f'<unit id="{unit_id}"><segment id="{segment_id}"><source>hi</source></segment></unit>'
        "</group></file>"
    )


def test_a_real_multi_file_document_with_distinct_file_ids_is_valid() -> None:
    document = loads(_document(_file("f1", "g1", "u1", "s1") + _file("f2", "g2", "u2", "s2")))

    report = validate(document)

    assert report.is_valid is True


def test_two_files_sharing_an_id_are_flagged_as_duplicate() -> None:
    document = loads(_document(_file("f1", "g1", "u1", "s1") + _file("f1", "g2", "u2", "s2")))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "xliff.file.id.duplicate" for item in report.diagnostics)


def test_two_sibling_groups_in_one_file_sharing_an_id_are_flagged_as_duplicate() -> None:
    body = (
        '<file id="f1">'
        '<group id="g1"><unit id="u1"><segment id="s1"><source>hi</source></segment></unit></group>'
        '<group id="g1"><unit id="u2"><segment id="s2"><source>bye</source></segment></unit></group>'
        "</file>"
    )
    document = loads(_document(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "xliff.group.id.duplicate" for item in report.diagnostics)


def test_a_nested_group_sharing_its_parents_id_is_flagged_as_duplicate() -> None:
    """Group-id uniqueness scope is the whole enclosing file, not just
    immediate siblings, so a duplicate two levels deep must also be
    caught -- the flattening walk (_iter_groups) must descend fully."""
    body = (
        '<file id="f1"><group id="g1"><group id="g1">'
        '<unit id="u1"><segment id="s1"><source>hi</source></segment></unit>'
        "</group></group></file>"
    )
    document = loads(_document(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "xliff.group.id.duplicate" for item in report.diagnostics)


def test_two_groups_with_distinct_ids_in_one_file_are_not_flagged() -> None:
    body = (
        '<file id="f1">'
        '<group id="g1"><unit id="u1"><segment id="s1"><source>hi</source></segment></unit></group>'
        '<group id="g2"><unit id="u2"><segment id="s2"><source>bye</source></segment></unit></group>'
        "</file>"
    )
    document = loads(_document(body))

    report = validate(document)

    assert report.is_valid is True


def test_the_same_group_id_reused_across_different_files_is_not_a_duplicate() -> None:
    """The scope is per-file, per the spec's own text ("unique among all
    group id attribute values within the enclosing file element") -- not
    document-wide, unlike file ids themselves."""
    document = loads(_document(_file("f1", "g1", "u1", "s1") + _file("f2", "g1", "u2", "s2")))

    report = validate(document)

    assert report.is_valid is True
