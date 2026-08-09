"""NRRD-FRAME-001 against the shipped namespace.

(Teem NRRD Format Specification, Sections 1.1 and 4) MUST: "Starting
with NRRD0005, measurement frame supplies exactly space-dimension
vectors that transform measurement coefficients into the surrounding
space basis." A sibling obligation (SAL-NRRD-OBL-666DA3540EE4E38D,
NRRD-SPACE-001) explicitly instructs keeping this "in a separate model
and API" from space.py's own NRRD0004+ index-to-world transform.

required_tests: "Identity, rotated, and non-orthogonal frame fixtures;
cardinality and NRRD0001-NRRD0004 rejection negatives."

Before this file: `measurement frame` was recognized only as a
version-gate trigger (`NrrdDocument.version_requirements()` bumps to
NRRD0005 when the field is present) -- there was no typed parser, no
cardinality validation, no measurement-to-world transform, and no
read-time rejection under an older magic (the field could be silently
present in a pre-NRRD0005 file and only `validate()`, a separately
-invoked, opt-in call, would ever flag it -- the same
read-time-vs-validate()-only gap NRRD-MULTIFILE-001's own LIST/printf
version gate closed earlier this session, now closed the same way here).

Deliberately NOT built as part of `SpaceTransform`/`space.py`: a
measurement frame maps COEFFICIENTS of a vector/tensor quantity, not
point POSITIONS -- confirmed directly against the pinned spec text
("the matrix transforms... coordinates in the measurement frame to
coordinates in world space," no origin term at all), unlike
`index_to_world`'s own affine (origin + direction) map.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import (
    MeasurementFrameTransform,
    NrrdParseError,
    build_measurement_frame_transform,
    loads,
)


def _header(measurement_frame: str, *, magic: str = "NRRD0005") -> bytes:
    # Deliberately no "space dimension" field: this file tests the
    # "measurement frame" version gate in isolation. A real NRRD0005 file
    # would normally also declare space dimension (the spec requires it
    # to precede other orientation fields), but nothing in this test
    # file's own assertions reads it, and including it would also trip
    # the separate NRRD0004 space-field gate under an older magic --
    # test_obligation_space_field_typing.py covers that gate on its own.
    return (
        f"{magic}\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n"
        f"measurement frame: {measurement_frame}\n\n"
    ).encode() + bytes((1, 2, 3, 4))


# ── Building a validated transform ────────────────────────────────────────


def test_identity_frame_maps_coordinates_unchanged() -> None:
    transform = build_measurement_frame_transform(
        measurement_frame="(1,0,0) (0,1,0) (0,0,1)", space_dimension=3
    )

    assert transform.measurement_to_world((1.0, 2.0, 3.0)) == pytest.approx((1.0, 2.0, 3.0))


def test_rotated_frame_maps_coordinates_through_a_90_degree_rotation() -> None:
    """A 90-degree rotation about z (x-axis maps to +y, y-axis maps to
    -x), hand-verified independently of this module's own arithmetic."""
    transform = build_measurement_frame_transform(
        measurement_frame="(0,1,0) (-1,0,0) (0,0,1)", space_dimension=3
    )

    assert transform.measurement_to_world((1.0, 0.0, 0.0)) == pytest.approx((0.0, 1.0, 0.0))
    assert transform.measurement_to_world((0.0, 1.0, 0.0)) == pytest.approx((-1.0, 0.0, 0.0))


def test_non_orthogonal_frame_is_a_real_linear_combination() -> None:
    """Two non-perpendicular basis vectors -- proves this is genuine
    matrix-vector multiplication, not a shortcut that only happens to
    work for orthonormal bases."""
    transform = build_measurement_frame_transform(
        measurement_frame="(1,0) (1,1)", space_dimension=2
    )

    # world = 2*(1,0) + 3*(1,1) = (2,0) + (3,3) = (5,3)
    assert transform.measurement_to_world((2.0, 3.0)) == pytest.approx((5.0, 3.0))


def test_measurement_frame_transform_carries_no_origin() -> None:
    """A MeasurementFrameTransform has no origin field at all -- unlike
    SpaceTransform, which does -- because a measurement frame is a pure
    linear map (spec: no translation term), not an affine one."""
    transform = build_measurement_frame_transform(
        measurement_frame="(1,0) (0,1)", space_dimension=2
    )

    assert not hasattr(transform, "origin")
    assert isinstance(transform, MeasurementFrameTransform)


# ── Cardinality and shape validation ──────────────────────────────────────


def test_too_few_vectors_is_a_cardinality_error() -> None:
    with pytest.raises(NrrdParseError, match="declares 2 vectors but space dimension is 3"):
        build_measurement_frame_transform(measurement_frame="(1,0,0) (0,1,0)", space_dimension=3)


def test_too_many_vectors_is_a_cardinality_error() -> None:
    with pytest.raises(NrrdParseError, match="declares 4 vectors but space dimension is 3"):
        build_measurement_frame_transform(
            measurement_frame="(1,0,0) (0,1,0) (0,0,1) (1,1,1)", space_dimension=3
        )


def test_a_vector_with_the_wrong_component_count_is_rejected() -> None:
    with pytest.raises(NrrdParseError, match="must have 3 components"):
        build_measurement_frame_transform(
            measurement_frame="(1,0,0) (0,1) (0,0,1)", space_dimension=3
        )


def test_a_malformed_vector_with_non_numeric_content_is_rejected() -> None:
    """Inherited directly from space.py's own parse_space_directions
    (reused, not duplicated) -- exercised here through this obligation's
    own public entry point, not merely cross-referenced from a sibling
    test file."""
    with pytest.raises(NrrdParseError, match="invalid space directions"):
        build_measurement_frame_transform(
            measurement_frame="(1,0,0) garbage (0,0,1)", space_dimension=3
        )


def test_a_none_entry_is_rejected_there_is_no_per_axis_concept() -> None:
    with pytest.raises(NrrdParseError, match="no per-axis concept"):
        build_measurement_frame_transform(
            measurement_frame="(1,0,0) none (0,0,1)", space_dimension=3
        )


def test_calling_measurement_to_world_with_the_wrong_arity_is_rejected() -> None:
    transform = build_measurement_frame_transform(
        measurement_frame="(1,0,0) (0,1,0) (0,0,1)", space_dimension=3
    )

    with pytest.raises(NrrdParseError, match="2 components but the measurement frame is 3"):
        transform.measurement_to_world((1.0, 2.0))


# ── NRRD0005-only applicability, enforced at read time ────────────────────


def test_a_measurement_frame_under_nrrd0005_loads_successfully() -> None:
    document = loads(_header("(1,0,0) (0,1,0) (0,0,1)", magic="NRRD0005"))

    assert document.header["measurement frame"] == "(1,0,0) (0,1,0) (0,0,1)"


@pytest.mark.parametrize("magic", ["NRRD0001", "NRRD0002", "NRRD0003", "NRRD0004"])
def test_a_measurement_frame_under_an_older_magic_is_rejected_at_read_time(magic: str) -> None:
    """Confirmed genuinely unenforced at read time before this fix, the
    same way NRRD-MULTIFILE-001's own LIST/printf version gate was --
    only validate() (a separate, opt-in call) previously caught this."""
    with pytest.raises(NrrdParseError, match="NRRD0005 or newer"):
        loads(_header("(1,0,0) (0,1,0) (0,0,1)", magic=magic))
