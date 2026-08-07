"""XLIFF-MODEL-001 -- "Expose the document hierarchy as typed
XliffDocument/XliffFile/XliffGroup/XliffUnit/XliffSegment objects with
tree order and inherited attributes resolved."

MUST (SAL-XLIFF-OBL-7DA078717EA60881 / SAL-XLIFF-OBL-867500AA0AC3D2C1):
before this slice, xml:lang's own inheritance chain was confirmed
entirely unaddressed -- distinct from source/target language
*compatibility* checking (a different, already-built concern), which the
obligation's own missing_behavior explicitly separates out.

Grounded directly in the pinned XLIFF 2.1 spec's own default-value table
(section 4.3.2.1 xml:lang): "default values for this attribute depend on
the element in which it is used: When used in a <source> element: The
value set in the srcLang attribute of the enclosing <xliff> element. When
used in a <target> element: The value set in the trgLang attribute of the
enclosing <xliff> element. When used in any other element: The value of
the xml:lang attribute of its parent element."

This slice adds effective_xml_lang(), the same reusable-primitive shape
as effective_xml_space() (test_obligation_xml_space_inheritance_
resolution.py): a caller composes it while descending the hierarchy it
already navigates, not a magic whole-tree walker (this package's tree has
no parent back-references at all -- a larger, separate architecture
question deliberately not attempted here, same as xml:space). Unlike
xml:space, <source>/<target>'s own defaults are anchored to the document
ROOT's srcLang/trgLang, not their immediate parent -- modeled here as a
distinct branch rather than folded into generic parent-inheritance.
"""

from __future__ import annotations

from format_factory.xliff import effective_xml_lang


def test_a_locally_declared_value_always_wins_over_inheritance() -> None:
    assert effective_xml_lang("de", is_source=True, src_lang="en") == "de"
    assert effective_xml_lang("de", is_target=True, trg_lang="fr") == "de"
    assert effective_xml_lang("de", parent="ja") == "de"


def test_source_with_no_local_value_inherits_the_root_src_lang() -> None:
    assert effective_xml_lang(None, is_source=True, src_lang="en", trg_lang="fr") == "en"


def test_target_with_no_local_value_inherits_the_root_trg_lang() -> None:
    assert effective_xml_lang(None, is_target=True, src_lang="en", trg_lang="fr") == "fr"


def test_source_and_target_defaults_are_independent_of_each_other() -> None:
    """<source> never inherits trgLang and <target> never inherits
    srcLang -- each is anchored to its own distinct root attribute."""
    assert effective_xml_lang(None, is_source=True, src_lang="en", trg_lang="fr") != "fr"
    assert effective_xml_lang(None, is_target=True, src_lang="en", trg_lang="fr") != "en"


def test_any_other_element_inherits_the_parents_already_resolved_value() -> None:
    assert effective_xml_lang(None, parent="ja") == "ja"


def test_an_absent_parent_and_absent_root_language_resolves_to_none() -> None:
    """xml:lang has no universal fallback default the way xml:space does
    ("default") -- an element with nothing declared anywhere above it in
    the chain genuinely has no effective language, reported as None
    rather than a fabricated placeholder."""
    assert effective_xml_lang(None) is None
    assert effective_xml_lang(None, is_target=True, src_lang="en", trg_lang=None) is None
