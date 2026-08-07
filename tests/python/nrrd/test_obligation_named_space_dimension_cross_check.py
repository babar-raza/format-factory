"""NRRD-SPACE-001 -- named-space dimension cross-validation.

MUST (SAL-NRRD-OBL-D7B962F3981120A7 and its sibling): "Support NRRD0004+
space/orientation metadata with vector-length validation against space
dimension, non-spatial axes, and index-to-world transforms; never infer
axis order from a named space." Before this slice, confirmed genuinely
absent: no SAL fact in this repository enumerated Teem's named-space
strings with their exact implied dimensionality precisely enough to
hard-code that table safely, so the "space" field's own name was never
even a parameter to build_space_transform.

That was true of the SAL fact cache, but not of the pinned raw spec
acquisition cache: .local/format-contracts/acquired/nrrd/src-nrrd-002.bin
is a gzip-compressed tar archive (confirmed directly, not assumed) --
the full Teem 1.9.0 reference implementation source tree, not spec
prose. Its src/nrrd/enumsNrrd.c (_nrrdSpaceStr, the 12 canonical space
names and their string aliases) and src/nrrd/simple.c
(nrrdSpaceDimension()'s own switch statement, 3 for the six non-Time
variants, 4 for the six Time variants) together give the exact,
authoritative table this obligation's own missing_behavior said no SAL
fact could safely provide.

Deliberately narrow, per the obligation's own explicit, twice-stated
"never infer axis order from a named space": this ONLY cross-CHECKS a
scalar dimension already derived from explicit data (space_dimension/
space_origin/space_directions, exactly as before) against Teem's own
fixed dimension for a recognized standard name. It never infers, fills
in, or overrides the dimension FROM the name, and it makes no attempt
at axis order/handedness inference (a categorically different, much
larger, and still out-of-scope question). An unrecognized (but
spec-permitted) custom space name is not cross-checked and is not an
error.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdParseError, build_space_transform, named_space_dimension


# ── named_space_dimension() lookups ─────────────────────────────────────


@pytest.mark.parametrize(
    "name,expected",
    [
        ("right-anterior-superior", 3),
        ("left-anterior-superior", 3),
        ("left-posterior-superior", 3),
        ("right-anterior-superior-time", 4),
        ("left-anterior-superior-time", 4),
        ("left-posterior-superior-time", 4),
        ("scanner-xyz", 3),
        ("scanner-xyz-time", 4),
        ("3D-right-handed", 3),
        ("3D-left-handed", 3),
        ("3D-right-handed-time", 4),
        ("3D-left-handed-time", 4),
    ],
)
def test_every_standard_named_space_has_the_correct_teem_dimension(
    name: str, expected: int
) -> None:
    assert named_space_dimension(name) == expected


def test_lookup_is_case_insensitive() -> None:
    assert named_space_dimension("Right-Anterior-Superior") == 3
    assert named_space_dimension("RIGHT-ANTERIOR-SUPERIOR") == 3


@pytest.mark.parametrize(
    "acronym,expected",
    [("RAS", 3), ("LAS", 3), ("LPS", 3), ("RAST", 4), ("LAST", 4), ("LPST", 4)],
)
def test_teems_own_short_acronym_aliases_are_recognized(acronym: str, expected: int) -> None:
    assert named_space_dimension(acronym) == expected


def test_an_unrecognized_custom_space_name_returns_none_not_an_error() -> None:
    """The NRRD spec permits arbitrary "space" strings beyond Teem's 12
    standard names -- an unrecognized one is not cross-checkable, which
    is not the same as invalid."""
    assert named_space_dimension("my-custom-scanner-space") is None


# ── build_space_transform() cross-validation ────────────────────────────


def test_a_named_space_agreeing_with_the_derived_dimension_is_accepted() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(0,0,0)",
        space="right-anterior-superior",
        axis_count=3,
    )

    assert transform.space_dimension == 3


def test_a_time_variant_named_space_agreeing_with_4d_data_is_accepted() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0,0) (0,1,0,0) (0,0,1,0) none",
        space_origin="(0,0,0,0)",
        space="left-posterior-superior-time",
        axis_count=4,
    )

    assert transform.space_dimension == 4


def test_a_named_space_conflicting_with_the_derived_dimension_is_rejected() -> None:
    """"right-anterior-superior" (Teem's own fixed dimension: 3) cannot
    coexist with 4-component space directions/origin -- a genuine,
    previously-undetected document inconsistency."""
    with pytest.raises(NrrdParseError, match="implies dimension 3"):
        build_space_transform(
            space_directions="(1,0,0,0) (0,1,0,0) (0,0,1,0) none",
            space_origin="(0,0,0,0)",
            space="right-anterior-superior",
            axis_count=4,
        )


def test_a_time_variant_named_space_conflicting_with_3d_data_is_rejected() -> None:
    with pytest.raises(NrrdParseError, match="implies dimension 4"):
        build_space_transform(
            space_directions="(1,0,0) (0,1,0) (0,0,1)",
            space_origin="(0,0,0)",
            space="scanner-xyz-time",
            axis_count=3,
        )


def test_an_unrecognized_custom_space_name_is_not_cross_checked() -> None:
    """A custom (non-standard, but spec-permitted) space name must not
    block a document whose dimension is otherwise perfectly consistent
    -- there is nothing to check it against."""
    transform = build_space_transform(
        space_directions="(1,0,0,0) (0,1,0,0) (0,0,1,0) none",
        space_origin="(0,0,0,0)",
        space="my-custom-scanner-space",
        axis_count=4,
    )

    assert transform.space_dimension == 4


def test_omitting_space_entirely_is_unaffected_matching_prior_behavior() -> None:
    transform = build_space_transform(
        space_directions="(1,0,0) (0,1,0) (0,0,1)",
        space_origin="(0,0,0)",
        axis_count=3,
    )

    assert transform.space_dimension == 3


def test_the_cross_check_does_not_infer_or_alter_axis_order() -> None:
    """The obligation's own "never infer axis order from a named space"
    instruction stays fully honored: direction_vectors are returned
    exactly as parsed, in document order, regardless of what the named
    space's own canonical axis convention would imply."""
    transform = build_space_transform(
        space_directions="(0,0,1) (0,1,0) (1,0,0)",  # deliberately "backwards"
        space_origin="(0,0,0)",
        space="right-anterior-superior",
        axis_count=3,
    )

    assert transform.direction_vectors == ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
