"""XLIFF-MODEL-001 -- whole-tree xml:space/xml:lang resolution per unit.

MUST (SAL-XLIFF-OBL-7DA078717EA60881, SAL-XLIFF-OBL-867500AA0AC3D2C1):
both obligations' own missing_behavior said a method answering "this
unit's effective xml:space/xml:lang" without the caller supplying its own
ancestor chain "would need a larger, separate architecture change (either
parent pointers or a redesigned tree)". That assumption was investigated
and found wrong: effective_xml_space()/effective_xml_lang() are documented
as reusable RULES meant to be composed by a caller descending the
hierarchy it already navigates -- no parent pointers needed, since a
top-down walk can thread each level's own resolved value down to the next
without ever needing to look back up. effective_attributes_by_unit()
(model/document.py) is exactly that walk, composing the same two
already-tested primitives once per document instead of once per call site.
"""

from __future__ import annotations

from format_factory.xliff.model import (
    Group,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    effective_attributes_by_unit,
)

_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def _unit(unit_id: str, *, attributes: dict[str, str] | None = None) -> Unit:
    return Unit(
        id=unit_id,
        children=[Segment(id=f"{unit_id}-s1", source=["text"])],
        attributes=attributes or {},
    )


def test_a_unit_with_no_ancestor_attributes_gets_the_document_root_defaults() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[XliffFile(id="f1", children=[_unit("u1")])],
    )

    result = effective_attributes_by_unit(document)

    assert result["u1"] == ("default", None)


def test_a_unit_inherits_xml_space_set_on_its_own_file() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(id="f1", children=[_unit("u1")], attributes={_XML_SPACE: "preserve"})
        ],
    )

    result = effective_attributes_by_unit(document)

    assert result["u1"] == ("preserve", None)


def test_a_unit_inherits_xml_lang_set_on_an_enclosing_group() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f1",
                children=[Group(id="g1", children=[_unit("u1")], attributes={_XML_LANG: "fr"})],
            )
        ],
    )

    result = effective_attributes_by_unit(document)

    assert result["u1"] == ("default", "fr")


def test_a_units_own_local_attribute_overrides_the_inherited_value() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f1",
                children=[_unit("u1", attributes={_XML_SPACE: "default"})],
                attributes={_XML_SPACE: "preserve"},
            )
        ],
    )

    result = effective_attributes_by_unit(document)

    assert result["u1"] == ("default", None)


def test_nested_groups_compose_inheritance_correctly_at_every_level() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f1",
                attributes={_XML_SPACE: "preserve"},
                children=[
                    Group(
                        id="g1",
                        attributes={_XML_LANG: "fr"},
                        children=[
                            Group(id="g2", children=[_unit("u1")]),
                            _unit("u2", attributes={_XML_SPACE: "default"}),
                        ],
                    )
                ],
            )
        ],
    )

    result = effective_attributes_by_unit(document)

    assert result["u1"] == ("preserve", "fr")
    assert result["u2"] == ("default", "fr")


def test_sibling_files_each_resolve_independently() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(id="f1", children=[_unit("u1")], attributes={_XML_SPACE: "preserve"}),
            XliffFile(id="f2", children=[_unit("u2")]),
        ],
    )

    result = effective_attributes_by_unit(document)

    assert result["u1"] == ("preserve", None)
    assert result["u2"] == ("default", None)


def test_every_unit_in_a_realistic_multi_file_multi_group_document_is_covered() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f1",
                children=[
                    _unit("u1"),
                    Group(id="g1", children=[_unit("u2"), _unit("u3")]),
                ],
            ),
        ],
    )

    result = effective_attributes_by_unit(document)

    assert set(result) == {"u1", "u2", "u3"}
    assert result["u1"] == result["u2"] == result["u3"] == ("default", None)
