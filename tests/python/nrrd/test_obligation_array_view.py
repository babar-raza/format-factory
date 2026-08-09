"""NRRD-ARRAY-001 against the shipped namespace.

MUST: "Expose typed N-dimensional array access with shape, strides,
dtype, slicing, axis permutation, flip, and crop where orientation and
per-axis metadata follow every operation - the imaging-pipeline core."

required_tests: "Metadata-follows-operation fixtures for each axis
operation."

Before this file, no test anywhere in the tree exercised element-level
`__getitem__`, multi-axis slicing, axis permutation/transpose, flip, or
crop as an operation on a returned array object with metadata
propagation -- `NrrdDocument.array`/`.to_array()` are a flat/nested
Python `list` with no shape/strides/dtype object and no operations
(confirmed by a full repository search before writing this obligation's
implementation). This file proves `format_factory.nrrd.array_view` (and
the `NrrdArrayView`/`NrrdDtype`/`AxisMetadata` types it returns) fills
that gap: shape/strides/dtype exposure, element access, slicing,
permutation, flip, crop, zero-copy view sharing vs explicit `.copy()`,
and per-axis metadata (kind, spacing, axis min/max, space direction/
origin) following every operation, including the "range" kind axis guard
that refuses a crop/slice which would change a fixed-width sample
structure's own element count.

FF6-EVENT-000477 closed the cell-vs-node `centers` gap this file used to
disclose here as unattempted: `_sliced_axis_metadata` (array_view.py) now
branches on the axis's own `center` field, confirmed directly against
the pinned NRRD spec's own worked example (5 samples, axis min 0.0, axis
max 1.0: node-centered samples land at 0.00/0.25/.../1.00; cell-centered
samples land at 0.10/0.30/.../0.90) -- a node-centered axis keeps this
module's original formula unchanged (axis_min/axis_max ARE sample
positions), while a cell-centered axis now correctly spans the retained
region's own outer edges, one full cell wider than the node case for the
same retained sample count.

Not attempted here, and not claimed: negative-step slicing (use
`.flip()`), and any numpy interop (no numpy dependency exists in this
package; `adapters/` stays empty -- and, per SAL-NRRD-OBL-E4B3D1A206784660
/SAL-NRRD-OBL-FEF73EC95DF631C3's own literal rule_text, a numpy/pynrrd
adapter is not actually a requirement of either obligation at all; that
was scope a prior evidence entry's own missing_behavior text added
beyond what either obligation's rule_text/required_tests/release_gates
name, not something this file force-builds to match).
"""

from __future__ import annotations

import pytest

from format_factory.core import ResourceLimits, ResourceLimitError
from format_factory.nrrd import (
    NrrdArrayError,
    NrrdDocument,
    array_view,
    dumps,
    loads,
)


def _document(
    *,
    sizes: str,
    dtype: str = "uint8",
    array: list[int],
    extra_header: dict[str, str] | None = None,
) -> NrrdDocument:
    header = {
        "dimension": str(len(sizes.split())),
        "sizes": sizes,
        "type": dtype,
        "encoding": "raw",
    }
    header.update(extra_header or {})
    return NrrdDocument(version=5, header=header, payload=b"", array=array)


# ── Shape, strides, dtype ────────────────────────────────────────────────


def test_shape_strides_and_dtype_match_the_declared_header() -> None:
    document = _document(sizes="2 3 4", dtype="uint16", array=list(range(24)))

    view = array_view(document)

    assert view.shape == (2, 3, 4)
    assert view.ndim == 3
    assert view.size == 24
    # NRRD axis 0 is fastest-varying (SAL-NRRD-00015): its own stride is 1,
    # each subsequent axis's stride is the product of every faster size.
    assert view.strides == (1, 2, 6)
    assert view.dtype.name == "uint16"
    assert view.dtype.struct_code == "H"
    assert view.dtype.itemsize == 2
    assert view.dtype.is_block is False


def test_block_type_dtype_carries_the_declared_block_size() -> None:
    document = _document(
        sizes="4",
        dtype="block",
        array=[b"\x00" * 8 for _ in range(4)],
        extra_header={"block size": "8"},
    )

    view = array_view(document)

    assert view.dtype.is_block is True
    assert view.dtype.itemsize == 8
    assert view.dtype.struct_code is None


# ── Element access ───────────────────────────────────────────────────────


def test_element_access_follows_fastest_first_axis_order() -> None:
    document = _document(sizes="2 3 4", array=list(range(24)))
    view = array_view(document)

    assert view[0, 0, 0] == 0
    assert view[1, 0, 0] == 1  # axis 0 fastest: +1 element
    assert view[0, 1, 0] == 2  # axis 1 stride == size of axis 0 == 2
    assert view[0, 0, 1] == 6  # axis 2 stride == size(axis0) * size(axis1) == 6


def test_negative_index_counts_from_the_end() -> None:
    document = _document(sizes="4", array=[10, 20, 30, 40])
    view = array_view(document)

    assert view[-1] == 40
    assert view[-4] == 10


def test_out_of_range_index_raises() -> None:
    document = _document(sizes="4", array=[10, 20, 30, 40])
    view = array_view(document)

    with pytest.raises(NrrdArrayError, match="out of range"):
        view[4]


def test_too_many_indices_raises() -> None:
    document = _document(sizes="2 2", array=[1, 2, 3, 4])
    view = array_view(document)

    with pytest.raises(NrrdArrayError, match="too many indices"):
        view[0, 0, 0]


# ── Slicing ───────────────────────────────────────────────────────────────


def test_partial_indexing_keeps_remaining_axes() -> None:
    document = _document(sizes="2 3", array=[0, 1, 2, 3, 4, 5])
    view = array_view(document)

    row = view[1]

    assert row.shape == (3,)
    assert row.to_nested_list() == [1, 3, 5]


def test_slicing_is_zero_copy_sharing_the_same_backing_data() -> None:
    document = _document(sizes="4", array=[10, 20, 30, 40])
    view = array_view(document)

    sliced = view[1:3]

    assert sliced.data is view.data
    assert sliced.copied is False
    assert sliced.to_nested_list() == [20, 30]


def test_stepped_slices_are_rejected_in_favor_of_flip() -> None:
    document = _document(sizes="4", array=[10, 20, 30, 40])
    view = array_view(document)

    with pytest.raises(NrrdArrayError, match="flip"):
        view[::2]


# ── Metadata propagation: spacing/axis-min-max under slicing ────────────


def test_sliced_axis_metadata_recomputes_min_max_from_spacing() -> None:
    document = _document(
        sizes="5",
        array=[0, 1, 2, 3, 4],
        extra_header={
            "kinds": "domain",
            "spacings": "2.0",
            "axis mins": "0.0",
            "axis maxs": "8.0",
        },
    )
    view = array_view(document)

    sliced = view[1:4]

    meta = sliced.axes[0]
    assert meta.size == 3
    assert meta.spacing == 2.0
    assert meta.axis_min == pytest.approx(2.0)  # 0.0 + 1 * 2.0
    assert meta.axis_max == pytest.approx(6.0)  # 2.0 + (3 - 1) * 2.0


def test_sliced_axis_metadata_clears_min_max_without_spacing() -> None:
    document = _document(sizes="5", array=[0, 1, 2, 3, 4], extra_header={"kinds": "domain"})
    view = array_view(document)

    sliced = view[1:4]

    assert sliced.axes[0].spacing is None
    assert sliced.axes[0].axis_min is None
    assert sliced.axes[0].axis_max is None


# ── crop() ────────────────────────────────────────────────────────────────


def test_crop_selects_the_declared_sub_region() -> None:
    document = _document(sizes="4 4", array=list(range(16)))
    view = array_view(document)

    cropped = view.crop((1, 3), (0, 2))

    assert cropped.shape == (2, 2)
    # axis 0 (fastest) selects original x in {1,2}; axis 1 selects y in {0,1}.
    # to_nested_list() nests axis 1 (slowest of this 2-axis view) outermost:
    # row y=0 -> [x=1,y=0]=1, [x=2,y=0]=2; row y=1 -> [x=1,y=1]=5, [x=2,y=1]=6.
    assert cropped.to_nested_list() == [[1, 2], [5, 6]]
    assert cropped.data is view.data


def test_crop_on_a_fixed_width_range_kind_axis_is_refused() -> None:
    document = _document(
        sizes="4 3", array=list(range(12)), extra_header={"kinds": "domain 3-color"}
    )
    view = array_view(document)

    with pytest.raises(NrrdArrayError, match="3-color"):
        view.crop((0, 4), (0, 2))


def test_full_size_slice_on_a_range_kind_axis_is_permitted() -> None:
    document = _document(
        sizes="4 3", array=list(range(12)), extra_header={"kinds": "domain 3-color"}
    )
    view = array_view(document)

    result = view.crop((1, 3), (0, 3))

    assert result.shape == (2, 3)


# ── cell-vs-node `centers` semantics under crop ──────────────────────────
#
# Both worked examples reproduce the pinned NRRD spec's own example
# verbatim: 5 samples, axis min 0.0, axis max 1.0 -- node-centered
# samples land at 0.00/0.25/0.50/0.75/1.00 (spacing 0.25); cell-centered
# samples land at 0.10/0.30/0.50/0.70/0.90 (spacing 0.20).


def test_node_centered_crop_keeps_the_original_sample_position_formula() -> None:
    """Unchanged from this module's own original, node-equivalent
    formula -- node-centered `axis_min`/`axis_max` ARE sample positions,
    so cropping to samples [1, 4) spans exactly those two retained
    samples' own positions (0.25 to 0.75)."""
    document = _document(
        sizes="5",
        array=[0, 1, 2, 3, 4],
        extra_header={
            "kinds": "domain",
            "spacings": "0.25",
            "axis mins": "0.0",
            "axis maxs": "1.0",
            "centers": "node",
        },
    )
    view = array_view(document)

    cropped = view.crop((1, 4))

    assert cropped.axes[0].axis_min == pytest.approx(0.25)
    assert cropped.axes[0].axis_max == pytest.approx(0.75)


def test_cell_centered_crop_spans_the_retained_cells_own_outer_edges() -> None:
    """Cell-centered `axis_min`/`axis_max` are the grid's own OUTER
    EDGES, not sample positions -- cropping to samples [1, 4) (the cells
    at positions 0.30/0.50/0.70) must span their own edge-to-edge extent,
    0.20 to 0.80, one full cell wider than the node-centered case above
    despite selecting the same 3-of-5 samples."""
    document = _document(
        sizes="5",
        array=[0, 1, 2, 3, 4],
        extra_header={
            "kinds": "domain",
            "spacings": "0.20",
            "axis mins": "0.0",
            "axis maxs": "1.0",
            "centers": "cell",
        },
    )
    view = array_view(document)

    cropped = view.crop((1, 4))

    assert cropped.axes[0].axis_min == pytest.approx(0.20)
    assert cropped.axes[0].axis_max == pytest.approx(0.80)


def test_a_single_retained_cell_still_spans_one_full_cell_width_not_zero() -> None:
    """A cell always covers real space -- cropping a cell-centered axis
    down to exactly one retained sample must not collapse axis_min and
    axis_max to the same point the way a node-centered single-sample crop
    correctly does (see test_flip_swaps_axis_min_and_max's own sibling
    node behavior elsewhere in this file)."""
    document = _document(
        sizes="5",
        array=[0, 1, 2, 3, 4],
        extra_header={
            "kinds": "domain",
            "spacings": "0.20",
            "axis mins": "0.0",
            "axis maxs": "1.0",
            "centers": "cell",
        },
    )
    view = array_view(document)

    cropped = view.crop((2, 3))

    assert cropped.axes[0].axis_min == pytest.approx(0.40)
    assert cropped.axes[0].axis_max == pytest.approx(0.60)


def test_an_axis_with_no_declared_center_keeps_the_node_equivalent_default() -> None:
    """No `centers` header field at all (the common case) must not
    silently start behaving like a cell-centered axis -- the safe,
    conservative default this module has always used stays unchanged."""
    document = _document(
        sizes="5",
        array=[0, 1, 2, 3, 4],
        extra_header={"kinds": "domain", "spacings": "0.25", "axis mins": "0.0", "axis maxs": "1.0"},
    )
    view = array_view(document)

    cropped = view.crop((1, 4))

    assert cropped.axes[0].axis_min == pytest.approx(0.25)
    assert cropped.axes[0].axis_max == pytest.approx(0.75)


# ── transpose() / permute() ──────────────────────────────────────────────


def test_transpose_reorders_shape_strides_and_axis_metadata() -> None:
    document = _document(
        sizes="2 3 4", array=list(range(24)), extra_header={"labels": '"x" "y" "z"'}
    )
    view = array_view(document)

    transposed = view.transpose(2, 0, 1)

    assert transposed.shape == (4, 2, 3)
    assert [axis.label for axis in transposed.axes] == ["z", "x", "y"]
    # Value at the new coordinates must match the old element at the
    # corresponding permuted coordinates.
    assert transposed[1, 0, 0] == view[0, 0, 1]


def test_transpose_with_no_arguments_reverses_axis_order() -> None:
    document = _document(sizes="2 3", array=[0, 1, 2, 3, 4, 5])
    view = array_view(document)

    reversed_view = view.transpose()

    assert reversed_view.shape == (3, 2)


def test_transpose_rejects_a_non_permutation_order() -> None:
    document = _document(sizes="2 3", array=[0, 1, 2, 3, 4, 5])
    view = array_view(document)

    with pytest.raises(NrrdArrayError, match="permutation"):
        view.transpose(0, 0)


def test_permute_is_an_alias_for_transpose_taking_one_sequence() -> None:
    document = _document(sizes="2 3 4", array=list(range(24)))
    view = array_view(document)

    assert view.permute((2, 0, 1)).shape == view.transpose(2, 0, 1).shape


# ── flip() ────────────────────────────────────────────────────────────────


def test_flip_reverses_axis_order_of_values() -> None:
    document = _document(sizes="4", array=[10, 20, 30, 40])
    view = array_view(document)

    flipped = view.flip(0)

    assert flipped.to_nested_list() == [40, 30, 20, 10]
    assert flipped.data is view.data  # zero-copy


def test_flip_swaps_axis_min_and_max() -> None:
    document = _document(
        sizes="4",
        array=[0, 1, 2, 3],
        extra_header={"kinds": "domain", "spacings": "1.0", "axis mins": "0.0", "axis maxs": "3.0"},
    )
    view = array_view(document)

    flipped = view.flip(0)

    assert flipped.axes[0].axis_min == 3.0
    assert flipped.axes[0].axis_max == 0.0


def test_flip_negates_space_direction_and_shifts_origin_to_compensate() -> None:
    document = _document(
        sizes="3 2",
        array=list(range(6)),
        extra_header={
            "space dimension": "2",
            "space directions": "(1,0) (0,1)",
            "space origin": "(10,20)",
        },
    )
    view = array_view(document)

    flipped = view.flip(0)

    assert flipped.axes[0].space_direction == pytest.approx((-1.0, 0.0))
    # origin + (size - 1) * old_direction == (10 + 2*1, 20 + 2*0) == (12, 20)
    assert flipped.space_origin == pytest.approx((12.0, 20.0))


def test_double_flip_of_the_same_axis_restores_the_original_values() -> None:
    document = _document(sizes="5", array=[1, 2, 3, 4, 5])
    view = array_view(document)

    twice_flipped = view.flip(0).flip(0)

    assert twice_flipped.to_nested_list() == view.to_nested_list()


# ── copy() ────────────────────────────────────────────────────────────────


def test_copy_materializes_independent_backing_data() -> None:
    document = _document(sizes="4", array=[10, 20, 30, 40])
    view = array_view(document)
    sliced = view[1:3]

    copied = sliced.copy()

    assert copied.data is not sliced.data
    assert copied.copied is True
    assert copied.to_nested_list() == sliced.to_nested_list()


def test_copy_of_a_transposed_view_preserves_values_in_the_new_order() -> None:
    document = _document(sizes="2 3", array=[0, 1, 2, 3, 4, 5])
    view = array_view(document)
    transposed = view.transpose()

    copied = transposed.copy()

    assert copied.to_nested_list() == transposed.to_nested_list()
    assert copied.shape == transposed.shape


# ── Resource limits ───────────────────────────────────────────────────────


def test_array_view_rejects_a_document_whose_array_length_disagrees_with_sizes() -> None:
    document = _document(sizes="4", array=[1, 2, 3])  # declares 4, provides 3

    with pytest.raises(NrrdArrayError, match="expected"):
        array_view(document)


def test_array_view_bounds_element_count_against_supplied_limits() -> None:
    document = _document(sizes="1000000", array=list(range(1000000)))
    tiny_limits = ResourceLimits(max_decompressed_bytes=64)

    with pytest.raises(ResourceLimitError):
        array_view(document, limits=tiny_limits)


# ── Integration: a real load()/dumps() round trip, not just a hand-built document ──


def test_array_view_over_a_loaded_document_matches_to_array() -> None:
    document = _document(sizes="2 3", array=[0, 1, 2, 3, 4, 5])
    payload = dumps(document)
    reloaded = loads(payload)

    view = array_view(reloaded)

    assert view.to_nested_list() == reloaded.to_array()
