"""XLIFF-MODEL-001 -- deeply nested group hierarchy: order and IDs survive a
full load, traversal, and round-trip.

MUST (SAL-XLIFF-OBL-7DA078717EA60881 / SAL-XLIFF-OBL-867500AA0AC3D2C1):
"Expose the document hierarchy as typed XliffDocument/XliffFile/Group/Unit/
Segment objects with tree order ... resolved" / "Model the full core
hierarchy with tree order, IDs, references ... preserved through edits."

Before this slice, every shipped-namespace test used at most one level of
group nesting (file > group > unit > segment). Group.children already
supports Group | Unit | ExtensionNode (groups nesting within groups), and
iter_units() already recurses through them, but nothing in the shipped test
suite exercised a group-within-group document to prove order and IDs
survive traversal and a round trip at depth. (The only prior fixture using
actual nested groups, test_xliff_structural_fidelity.py, imports the
deprecated bare xliff.* shadow package and does not count as shipped-
namespace evidence.)
"""

from __future__ import annotations

from format_factory.xliff import Group, Unit, dumps, loads

_NESTED = b"""<?xml version="1.0" encoding="UTF-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.1" srcLang="en">
  <file id="f1">
    <group id="outer">
      <unit id="u-outer-1"><segment id="s1"><source>Outer first</source></segment></unit>
      <group id="inner">
        <unit id="u-inner-1"><segment id="s2"><source>Inner first</source></segment></unit>
        <unit id="u-inner-2"><segment id="s3"><source>Inner second</source></segment></unit>
      </group>
      <unit id="u-outer-2"><segment id="s4"><source>Outer second</source></segment></unit>
    </group>
  </file>
</xliff>
"""


def test_nested_groups_parse_as_typed_group_objects_at_every_level() -> None:
    document = loads(_NESTED)
    file = document.children[0]
    outer = file.children[0]

    assert isinstance(outer, Group)
    assert outer.id == "outer"
    inner = next(child for child in outer.children if isinstance(child, Group))
    assert inner.id == "inner"
    assert all(isinstance(child, (Group, Unit)) for child in outer.children)


def test_iter_units_visits_nested_group_units_in_document_order() -> None:
    document = loads(_NESTED)

    unit_ids = [unit.id for unit in document.iter_units()]

    assert unit_ids == ["u-outer-1", "u-inner-1", "u-inner-2", "u-outer-2"]


def test_nested_group_and_unit_ids_survive_a_full_round_trip() -> None:
    document = loads(_NESTED)

    reloaded = loads(dumps(document))

    assert [unit.id for unit in reloaded.iter_units()] == [
        unit.id for unit in document.iter_units()
    ]
    outer = reloaded.children[0].children[0]
    inner = next(child for child in outer.children if isinstance(child, Group))
    assert outer.id == "outer"
    assert inner.id == "inner"
