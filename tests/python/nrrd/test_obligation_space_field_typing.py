"""NRRD-SPACE-001 against the shipped namespace.

(Teem NRRD Format Specification, Sections 1.1 and 4) MUST: "Starting with
NRRD0004, space, space dimension, space units, space origin, and
per-axis space directions describe array orientation in a surrounding
space; measurement frame is not available until NRRD0005."

Before this file: `space`/`space dimension`/`space units`/`space origin`/
`space directions` were retained only as raw header strings -- `space`
had its own typed accessor, but the other four did not (a caller had to
reach into `document.header` and parse the raw text themselves, or go
through `space.build_space_transform`, which needs an already-known
`axis_count` and only returns a validated `SpaceTransform`, not the raw
per-field values). There was also no read-time NRRD0004 profile-boundary
enforcement for any of these five fields -- only `NrrdDocument.
version_requirements()`/`validate()`, a separate, opt-in call, ever
flagged a declaration under an older magic; `load()`/`loads()` accepted
it silently. This file closes both gaps: typed accessors
(`NrrdDocument.space_dimension`/`.space_units`/`.space_origin`/
`.space_directions`, matching the existing `.space`/`.labels`/`.units`
accessor convention) and a read-time refusal mirroring the precedent
already established for the NRRD0004 LIST/printf multi-file form and the
NRRD0005 `measurement frame` field.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdParseError, loads


def _header(magic: str = "NRRD0005", extra: str = "") -> bytes:
    extra = extra.rstrip("\n")
    lines = f"{magic}\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw"
    if extra:
        lines += "\n" + extra
    return (lines + "\n\n").encode() + bytes((1, 2, 3, 4))


# ── Typed accessors ────────────────────────────────────────────────────


def test_space_dimension_is_typed_as_an_int() -> None:
    document = loads(_header(extra="space dimension: 3"))

    assert document.space_dimension == 3


def test_space_dimension_is_none_when_absent() -> None:
    document = loads(_header())

    assert document.space_dimension is None


def test_space_units_is_typed_as_a_list_of_strings() -> None:
    document = loads(_header(extra='space units: "mm" "mm" "mm"'))

    assert document.space_units == ["mm", "mm", "mm"]


def test_space_units_is_empty_when_absent() -> None:
    document = loads(_header())

    assert document.space_units == []


def test_space_origin_is_typed_as_a_coordinate_vector() -> None:
    document = loads(_header(extra="space origin: (1.5,-2,0)"))

    assert document.space_origin == pytest.approx((1.5, -2.0, 0.0))


def test_space_origin_is_none_when_absent() -> None:
    document = loads(_header())

    assert document.space_origin is None


def test_space_directions_is_typed_as_one_entry_per_axis() -> None:
    document = loads(_header(extra="space directions: (1,0,0)"))

    assert document.space_directions == ((1.0, 0.0, 0.0),)


def test_space_directions_marks_a_non_spatial_axis_as_none() -> None:
    payload = bytes((1, 2, 3, 4))
    header = (
        b"NRRD0005\ntype: uint8\ndimension: 2\nsizes: 4 1\nencoding: raw\n"
        b"space directions: (1,0,0) none\n\n"
    )
    document = loads(header + payload)

    assert document.space_directions == ((1.0, 0.0, 0.0), None)


def test_space_directions_is_none_when_absent() -> None:
    document = loads(_header())

    assert document.space_directions is None


def test_a_malformed_space_origin_is_rejected() -> None:
    """Parsing is lazy (on property access, not at `loads()` time) --
    the raw header value survives loading regardless of its own
    validity, matching every other typed accessor in this module
    (`labels`/`units`/`centers` etc. are also computed on access)."""
    document = loads(_header(extra="space origin: not-a-vector"))

    with pytest.raises(NrrdParseError, match="invalid space origin"):
        _ = document.space_origin


# ── NRRD0004-only applicability, enforced at read time ────────────────


@pytest.mark.parametrize(
    "field_line",
    [
        "space: right-anterior-superior",
        "space dimension: 3",
        'space units: "mm" "mm" "mm"',
        "space origin: (0,0,0)",
        "space directions: (1,0,0)",
    ],
)
@pytest.mark.parametrize("magic", ["NRRD0001", "NRRD0002", "NRRD0003"])
def test_a_space_field_under_an_older_magic_is_rejected_at_read_time(
    magic: str, field_line: str
) -> None:
    """Confirmed genuinely unenforced at read time before this fix, the
    same way NRRD-MULTIFILE-001's own LIST/printf gate and NRRD-FRAME
    -001's own measurement-frame gate both were."""
    with pytest.raises(NrrdParseError, match="NRRD0004 or newer"):
        loads(_header(magic=magic, extra=field_line))


def test_a_space_field_under_nrrd0004_loads_successfully() -> None:
    document = loads(_header(magic="NRRD0004", extra="space dimension: 3"))

    assert document.space_dimension == 3


def test_multiple_space_fields_under_an_older_magic_are_all_named_in_the_error() -> None:
    with pytest.raises(NrrdParseError) as excinfo:
        loads(_header(magic="NRRD0002", extra="space dimension: 3\nspace origin: (0,0,0)"))

    assert "space dimension" in str(excinfo.value)
    assert "space origin" in str(excinfo.value)
