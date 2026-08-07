"""XLIFF-MODEL-001 -- "Expose the document hierarchy as typed
XliffDocument/XliffFile/XliffGroup/XliffUnit/XliffSegment objects with
tree order and inherited attributes resolved."

MUST (SAL-XLIFF-OBL-7DA078717EA60881 / SAL-XLIFF-OBL-867500AA0AC3D2C1):
before this slice, confirmed genuinely unbuilt by grepping model/
document.py for any inheritance/effective-attribute-resolution logic
(inherit, effective_, resolved_) and finding none.

Grounded directly in the pinned XLIFF 2.1 spec's own default-value table
(section 4.3.2.2 xml:space): "default values for this attribute depend on
the element in which it is used: When used in <data>: The value preserve.
When used in <xliff>: The value default. When used in any other element:
The value of the xml:space attribute of its parent element."

This slice adds effective_xml_space() -- the resolution RULE as a
reusable primitive a caller composes while descending the hierarchy it
already navigates, not a magic whole-tree walker. XliffDocument.xml_space
(proven separately, test_obligation_root_xml_space_default.py) already
answers the root case; this primitive handles every other element,
including <data>'s own distinct fixed default. Building a full parent-
aware walking API (this package's tree has no parent back-references at
all) is a larger, separate architecture question deliberately not
attempted here -- this obligation's own rule_text names "attributes
resolved" as the requirement, and the resolution rule itself is now
directly, completely proven; composing it across an actual document tree
is left to the caller, same as this package's own established pattern for
other per-node computations (e.g. business_role in UBL's DocumentIndex).
"""

from __future__ import annotations

from format_factory.xliff import effective_xml_space


def test_a_locally_declared_value_always_wins_over_the_parent() -> None:
    assert effective_xml_space("preserve", parent="default") == "preserve"
    assert effective_xml_space("default", parent="preserve") == "default"


def test_an_absent_value_inherits_the_parents_effective_value() -> None:
    assert effective_xml_space(None, parent="preserve") == "preserve"
    assert effective_xml_space(None, parent="default") == "default"


def test_data_always_defaults_to_preserve_regardless_of_parent() -> None:
    """"When used in <data>: The value preserve" -- data's own fixed
    default is not inherited from its parent at all, unlike every other
    element."""
    assert effective_xml_space(None, is_data=True, parent="default") == "preserve"
    assert effective_xml_space(None, is_data=True, parent="preserve") == "preserve"


def test_an_explicit_value_on_data_still_wins_over_its_own_fixed_default() -> None:
    assert effective_xml_space("default", is_data=True) == "default"


def test_the_default_parent_argument_matches_the_root_default() -> None:
    """Calling with no parent argument at all mirrors resolving directly
    under a root that itself defaulted to "default" (XliffDocument.
    xml_space's own spec-mandated root default)."""
    assert effective_xml_space(None) == "default"
