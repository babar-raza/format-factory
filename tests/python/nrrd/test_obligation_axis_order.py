"""NRRD-SHAPE-001 against the shipped namespace.

MUST (SAL-NRRD-OBL-94D8938DE18A6562): "Validate dimension/sizes/per-axis
arity with checked multiplication for sample and byte counts; represent the
format's axis order explicitly and convert to host order only via explicit
operations."

Per-axis arity validation, checked multiplication, and dimension/sizes
validation were already implemented and covered (see the sibling entry
SAL-NRRD-OBL-428BE326FCBC9A6E). This obligation's own remaining
missing_behavior named one further gap: "a first-class axis-order
model/conversion report is absent." `to_array()` already converts NRRD's own
flat, fastest-first payload into a Python nested-list "host order" form
(reshape_nrrd_array), but the axis-order mapping it uses was implicit inside
a recursive closure, and there was no explicit inverse operation to convert
a host-order nested list back to NRRD's own flat order, and no way to
inspect the mapping independent of performing a conversion.

This file closes that gap with three additions:
- `axis_order_report(sizes)` -- the explicit axis-order mapping (strides,
  nesting order) `reshape_nrrd_array`/`flatten_nrrd_array` use, inspectable
  on its own.
- `flatten_nrrd_array(nested, sizes)` -- the explicit inverse of
  `reshape_nrrd_array`, a host-order nested list back to NRRD's own flat,
  fastest-first order.
- `NrrdDocument.with_array(nested)` -- a document-level convenience pairing
  `to_array()`'s own existing forward conversion with an explicit reverse.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import (
    AxisOrderReport,
    NrrdDocument,
    axis_order_report,
    flatten_nrrd_array,
    reshape_nrrd_array,
)


# ── axis_order_report: the mapping is explicit and inspectable on its own ──


def test_axis_order_report_for_a_two_dimensional_shape() -> None:
    """sizes=[2, 3]: axis 0 (fastest, size 2) is innermost; axis 1
    (slowest, size 3) is outermost -- matching to_array()'s own observed
    [[..], [..], [..]] shape (3 outer groups of 2)."""
    report = axis_order_report([2, 3])

    assert isinstance(report, AxisOrderReport)
    assert report.sizes == (2, 3)
    assert report.strides == (1, 2)
    assert report.nesting_order == (1, 0)


def test_axis_order_report_for_a_three_dimensional_shape() -> None:
    report = axis_order_report([2, 3, 4])

    assert report.strides == (1, 2, 6)
    assert report.nesting_order == (2, 1, 0)


def test_axis_order_report_for_a_one_dimensional_shape() -> None:
    report = axis_order_report([5])

    assert report.sizes == (5,)
    assert report.nesting_order == (0,)


def test_axis_order_report_does_not_require_an_actual_array() -> None:
    """Callable purely from `sizes` -- a caller can inspect the mapping a
    conversion WOULD use without performing one."""
    report = axis_order_report([4, 4, 4])

    assert report.sizes == (4, 4, 4)


# ── flatten_nrrd_array: the explicit inverse of reshape_nrrd_array ─────────


@pytest.mark.parametrize(
    "sizes,flat",
    [
        ([5], [1, 2, 3, 4, 5]),
        ([2, 3], [1, 2, 3, 4, 5, 6]),
        ([2, 3, 2], list(range(12))),
        ([1, 1], [42]),
    ],
)
def test_flatten_is_the_exact_inverse_of_reshape(sizes: list[int], flat: list[int]) -> None:
    nested = reshape_nrrd_array(flat, sizes)

    recovered = flatten_nrrd_array(nested, sizes)

    assert recovered == flat


def test_flatten_matches_the_obligations_own_worked_example() -> None:
    """The exact fixture test_obligation_shape_production.py already
    proves for reshape: sizes=[2, 3], flat=[1..6] -> [[1,2],[3,4],[5,6]]."""
    nested = [[1, 2], [3, 4], [5, 6]]

    flat = flatten_nrrd_array(nested, [2, 3])

    assert flat == [1, 2, 3, 4, 5, 6]


def test_flatten_rejects_a_nested_list_with_the_wrong_outer_length() -> None:
    with pytest.raises(ValueError, match="expected 3"):
        flatten_nrrd_array([[1, 2], [3, 4]], [2, 3])


def test_flatten_rejects_a_nested_list_with_the_wrong_inner_length() -> None:
    """Outer length (3) is correct; the last inner group has 3 entries
    instead of the expected 2."""
    with pytest.raises(ValueError, match="expected 2"):
        flatten_nrrd_array([[1, 2], [3, 4], [5, 6, 7]], [2, 3])


# ── NrrdDocument.with_array: the document-level explicit round trip ────────


def test_with_array_replaces_the_flat_array_from_a_host_order_nested_list() -> None:
    document = NrrdDocument(
        version=4,
        header={"type": "uint8", "dimension": "2", "sizes": "2 3", "encoding": "raw"},
        payload=b"",
        array=[0, 0, 0, 0, 0, 0],
    )

    edited = document.with_array([[1, 2], [3, 4], [5, 6]])

    assert edited.array == [1, 2, 3, 4, 5, 6]


def test_with_array_round_trips_through_to_array() -> None:
    document = NrrdDocument(
        version=4,
        header={"type": "uint8", "dimension": "2", "sizes": "2 3", "encoding": "raw"},
        payload=b"",
        array=[1, 2, 3, 4, 5, 6],
    )

    nested = document.to_array()
    edited = document.with_array(nested)

    assert edited.array == document.array


def test_with_array_does_not_mutate_the_original_document() -> None:
    document = NrrdDocument(
        version=4,
        header={"type": "uint8", "dimension": "1", "sizes": "3", "encoding": "raw"},
        payload=b"",
        array=[1, 2, 3],
    )

    document.with_array([9, 8, 7])

    assert document.array == [1, 2, 3]
