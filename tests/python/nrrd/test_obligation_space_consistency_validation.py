"""NRRD-VALIDATE-001 -- space/space dimension/space origin/space directions
mutual consistency, reported as a validate()-time diagnostic.

MUST (SAL-NRRD-OBL-2085AD256AFE6E96): conditional fields including
"space/space dimension/space origin/space directions mutual consistency"
must be checked by validate(). build_space_transform() (space.py, added at
FF6-EVENT-000273 for the separate named-space cross-check obligation)
already performs this consistency check internally via
_infer_space_dimension(), but was never wired into validate()'s own
diagnostics -- a caller had to invoke it manually to learn a document's
space fields disagreed with each other.

This closes that gap: validate() now calls build_space_transform() itself
whenever both "space directions" and "space origin" are present (both are
required inputs to that function -- space metadata is otherwise entirely
optional per NRRD0004+, so the check only activates when a document
actually declares both), and reports NrrdParseError as a non-fatal
"nrrd.space.inconsistent" diagnostic instead of raising.
"""

from __future__ import annotations

from format_factory.nrrd import NrrdDocument, dumps, loads, validate


def _document(**header_overrides: str) -> NrrdDocument:
    header = {
        "type": "uint16",
        "dimension": "2",
        "sizes": "2 2",
        "encoding": "raw",
        "endian": "little",
        **header_overrides,
    }
    draft = NrrdDocument(version=5, header=header, payload=b"", array=[0, 1, 2, 3])
    return loads(dumps(draft))


def test_consistent_space_directions_and_origin_validate_cleanly() -> None:
    document = _document(**{"space directions": "(1,0) (0,1)", "space origin": "(0,0)"})

    assert validate(document).is_valid


def test_origin_length_disagreeing_with_directions_is_reported() -> None:
    document = _document(**{"space directions": "(1,0) (0,1)", "space origin": "(0,0,0)"})

    report = validate(document)

    assert not report.is_valid
    assert any(item.code == "nrrd.space.inconsistent" for item in report.diagnostics)


def test_declared_space_dimension_disagreeing_with_origin_is_reported() -> None:
    document = _document(
        **{
            "space directions": "(1,0) (0,1)",
            "space origin": "(0,0)",
            "space dimension": "3",
        }
    )

    report = validate(document)

    assert not report.is_valid
    assert any(item.code == "nrrd.space.inconsistent" for item in report.diagnostics)


def test_named_space_disagreeing_with_derived_dimension_is_reported() -> None:
    """Cross-checks against Teem's own fixed dimension for a standard space
    name (space.py's named_space_dimension table) -- "right-anterior-superior"
    is a 3-dimensional space, but the directions/origin here only declare 2."""
    document = _document(
        **{
            "space": "right-anterior-superior",
            "space directions": "(1,0) (0,1)",
            "space origin": "(0,0)",
        }
    )

    report = validate(document)

    assert not report.is_valid
    assert any(item.code == "nrrd.space.inconsistent" for item in report.diagnostics)


def test_neither_space_field_present_is_unaffected() -> None:
    """Space metadata is entirely optional -- a document with neither field
    must not trigger this check at all."""
    document = _document()

    assert validate(document).is_valid


def test_only_space_directions_present_is_unaffected() -> None:
    """build_space_transform() requires BOTH fields; this check must not
    fire (or fail some other way) when only one is present."""
    document = _document(**{"space directions": "(1,0) (0,1)"})

    assert validate(document).is_valid


def test_only_space_origin_present_is_unaffected() -> None:
    document = _document(**{"space origin": "(0,0)"})

    assert validate(document).is_valid


def test_this_check_does_not_infer_or_alter_axis_order() -> None:
    """Deliberately "backwards"-looking but internally self-consistent
    vectors must still validate cleanly -- this check only compares
    declared lengths/dimensions against each other, never axis semantics."""
    document = _document(**{"space directions": "(0,1) (1,0)", "space origin": "(5,-5)"})

    assert validate(document).is_valid
