"""NRRD-SPACE-001 against the shipped namespace.

SAL-NRRD-00019 (MUST): starting with NRRD0004, space, space dimension,
space units, space origin, and per-axis space directions describe array
orientation in a surrounding space. required_behavior: support vector-length
validation against space dimension, non-spatial axes, and index-to-world
transforms; never infer axis order from a named space.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import (
    NrrdParseError,
    build_space_transform,
    parse_space_directions,
    parse_space_origin,
)


# ── Parsing ──────────────────────────────────────────────────────────────


def test_parse_space_directions_reads_one_vector_per_axis() -> None:
    vectors = parse_space_directions("(1,0,0) (0,1,0) (0,0,1)")

    assert vectors == ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def test_parse_space_directions_marks_non_spatial_axis_as_none() -> None:
    """A 4th axis (e.g. a color channel) is marked "none", distinguishing it
    from the 3 real spatial axes."""
    vectors = parse_space_directions("(1,0,0) (0,1,0) (0,0,1) none")

    assert vectors == ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), None)


def test_parse_space_directions_is_case_insensitive_for_none() -> None:
    assert parse_space_directions("None (1,0,0)") == (None, (1.0, 0.0, 0.0))


def test_parse_space_origin_reads_a_vector() -> None:
    assert parse_space_origin("(0,0,0)") == (0.0, 0.0, 0.0)


def test_parse_space_origin_accepts_negative_and_float_values() -> None:
    assert parse_space_origin("(-12.5,0.25,100)") == (-12.5, 0.25, 100.0)


def test_parse_space_directions_rejects_a_malformed_entry() -> None:
    with pytest.raises(NrrdParseError, match="invalid space directions"):
        parse_space_directions("(1,0,0) garbage")


def test_parse_space_origin_rejects_a_malformed_value() -> None:
    with pytest.raises(NrrdParseError, match="invalid space origin"):
        parse_space_origin("not-a-vector")


# ── Building a validated transform ──────────────────────────────────────────


def test_build_space_transform_from_consistent_3d_data() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(0,0,0)",
        axis_count=3,
    )

    assert transform.space_dimension == 3
    assert transform.spatial_axes == (0, 1, 2)


def test_space_dimension_is_derived_from_data_not_the_named_space() -> None:
    """"never infer axis order from a named space" -- dimension comes only
    from the vectors actually present, never from the "space" field's own
    name (even when omitted entirely, as here)."""
    transform = build_space_transform(
        space_directions="(1,0) (0,1)",
        space_origin="(5,5)",
        axis_count=2,
    )

    assert transform.space_dimension == 2


def test_explicit_space_dimension_must_agree_with_vector_lengths() -> None:
    with pytest.raises(NrrdParseError, match="inconsistent space dimension"):
        build_space_transform(
            space_directions="(1,0,0) (0,1,0) (0,0,1)",
            space_origin="(0,0,0)",
            space_dimension="4",
            axis_count=3,
        )


def test_explicit_space_dimension_agreeing_with_vectors_is_accepted() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(0,0,0)",
        space_dimension="3",
        axis_count=3,
    )

    assert transform.space_dimension == 3


def test_direction_entry_count_must_match_the_document_axis_count() -> None:
    with pytest.raises(NrrdParseError, match="declares 3 entries"):
        build_space_transform(
            space_directions="(1,0,0) (0,1,0) (0,0,1)",
            space_origin="(0,0,0)",
            axis_count=4,
        )


def test_origin_length_inconsistent_with_direction_vectors_is_rejected() -> None:
    """The origin's length is itself one of the dimension-determining
    signals, so a 3-component origin alongside 2-component direction vectors
    is an inconsistency caught at dimension inference, not a later per-field
    check against an already-decided dimension."""
    with pytest.raises(NrrdParseError, match="inconsistent space dimension"):
        build_space_transform(
            space_directions="(1,0) (0,1) none",
            space_origin="(0,0,0)",
            axis_count=3,
        )


def test_direction_vectors_of_differing_lengths_are_rejected() -> None:
    with pytest.raises(NrrdParseError, match="inconsistent space dimension"):
        build_space_transform(
            space_directions="(1,0,0) (0,1)",
            space_origin="(0,0,0)",
            axis_count=2,
        )


# ── Non-spatial axes ─────────────────────────────────────────────────────


def test_non_spatial_axis_is_excluded_from_spatial_axes() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1) none",
        space_origin="(0,0,0)",
        axis_count=4,
    )

    assert transform.spatial_axes == (0, 1, 2)


def test_non_spatial_axis_does_not_contribute_to_index_to_world() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1) none",
        space_origin="(0,0,0)",
        axis_count=4,
    )

    # The 4th axis (e.g. a color channel index of 2) must not move the world
    # position at all -- it has no spatial direction to move along.
    at_channel_0 = transform.index_to_world((1, 2, 3, 0))
    at_channel_2 = transform.index_to_world((1, 2, 3, 2))

    assert at_channel_0 == at_channel_2 == (1.0, 2.0, 3.0)


# ── Index-to-world transform ────────────────────────────────────────────


def test_identity_transform_maps_index_to_itself_plus_origin() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(10,20,30)",
        axis_count=3,
    )

    assert transform.index_to_world((1, 2, 3)) == (11.0, 22.0, 33.0)


def test_scaled_transform_applies_axis_spacing() -> None:
    """A real acquisition's axis spacing shows up as a non-unit direction
    vector magnitude -- 2mm per index step along X, for example."""
    transform = build_space_transform(
        space_directions="(2,0,0) (0,1,0) (0,0,0.5)",
        space_origin="(0,0,0)",
        axis_count=3,
    )

    assert transform.index_to_world((3, 4, 5)) == (6.0, 4.0, 2.5)


def test_index_to_world_rejects_an_index_of_the_wrong_length() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(0,0,0)",
        axis_count=3,
    )

    with pytest.raises(NrrdParseError, match="declares 3 axes"):
        transform.index_to_world((1, 2))


def test_zero_index_maps_exactly_to_the_origin() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(7,8,9)",
        axis_count=3,
    )

    assert transform.index_to_world((0, 0, 0)) == (7.0, 8.0, 9.0)
