"""XLIFF-TEXT-001 -- target-from-source creation under the 'none' code-copy
policy, and its whitespace/language preservation contract.

MUST (SAL-XLIFF-OBL-7E36DEBEB4162BA3): "support target creation from source
with explicit code-copy policy" (module-level copy_source_to_target,
code_copy_policy='all'|'none' -- distinct from the already-fully-tested
Segment.create_target_from_source(code_policy='copy'|'strip'|'empty')).

Before this slice, only the 'all' policy (full inline-code copy) and the
'invalid' rejection path were tested; 'none' (plain-text-only target,
explicitly discarding source code structure) was never exercised.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, copy_source_to_target

_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _segment() -> Segment:
    return Segment(
        id="s",
        source=["Hello ", InlineElement("pc", {"id": "1"}, ["world"]), "!"],
        source_attributes={_XML_LANG: "en-GB", _XML_SPACE: "preserve"},
    )


def test_none_policy_creates_a_plain_text_only_target() -> None:
    segment = _segment()

    copy_source_to_target(segment, code_copy_policy="none")

    assert segment.target == ["Hello world!"]
    assert not any(isinstance(node, InlineElement) for node in segment.target)


def test_none_policy_preserves_xml_space_but_never_copies_xml_lang() -> None:
    segment = _segment()

    copy_source_to_target(segment, code_copy_policy="none")

    assert segment.target_attributes == {_XML_SPACE: "preserve"}
    assert _XML_LANG not in segment.target_attributes


def test_none_policy_sets_an_explicitly_provided_target_language() -> None:
    segment = _segment()

    copy_source_to_target(segment, code_copy_policy="none", target_language="fr-FR")

    assert segment.target_attributes[_XML_LANG] == "fr-FR"
    assert segment.target_attributes[_XML_SPACE] == "preserve"


def test_all_and_none_policies_agree_on_flattened_text_but_differ_on_structure() -> None:
    all_segment = _segment()
    none_segment = _segment()

    copy_source_to_target(all_segment, code_copy_policy="all")
    copy_source_to_target(none_segment, code_copy_policy="none")

    assert len(all_segment.target) == 3
    assert isinstance(all_segment.target[1], InlineElement)
    assert len(none_segment.target) == 1
    assert none_segment.target[0] == "Hello world!"
