"""TC-FF6-SHARED-CHECKED-ARITHMETIC-001: the shared bounded multiply.

Extracted from NRRD and SafeTensors under directive GAP-010. These tests pin
the behavior both archetypes now depend on -- particularly the
check-before-multiply property, which is the half of the divergence that was
worth keeping.
"""

from __future__ import annotations

import pytest

from format_factory.core import CheckedArithmeticError, checked_product


# ── Ordinary results ────────────────────────────────────────────────────────


@pytest.mark.parametrize("values,expected", [
    ([], 1),                 # empty product
    ([7], 7),
    ([2, 3, 4], 24),
    ([1, 1, 1, 1], 1),
])
def test_products(values: list[int], expected: int) -> None:
    assert checked_product(values, ceiling=1000) == expected


def test_product_exactly_at_ceiling_is_allowed() -> None:
    """The ceiling is inclusive; boundary values are valid, boundary+1 is not."""
    assert checked_product([10, 10], ceiling=100) == 100
    with pytest.raises(CheckedArithmeticError):
        checked_product([10, 11], ceiling=100)


def test_single_factor_exactly_at_ceiling_is_allowed() -> None:
    assert checked_product([100], ceiling=100) == 100


# ── Zero handling: valid for some formats, not others ───────────────────────


def test_zero_makes_the_product_zero() -> None:
    """SafeTensors has legal zero-element tensors; NRRD rejects zero itself."""
    assert checked_product([3, 0, 5], ceiling=10) == 0


def test_zero_does_not_mask_a_later_malformed_factor() -> None:
    """A short-circuit on zero would silently accept invalid trailing input."""
    with pytest.raises(ValueError, match="non-negative"):
        checked_product([0, -5], ceiling=10)


def test_zero_does_not_mask_a_later_oversized_factor() -> None:
    with pytest.raises(CheckedArithmeticError, match="factor 1 exceeds"):
        checked_product([0, 99], ceiling=10)


def test_zero_with_otherwise_huge_factors_is_still_zero() -> None:
    assert checked_product([5, 5, 0], ceiling=1000) == 0


# ── The check-before-multiply property ──────────────────────────────────────


def test_no_intermediate_larger_than_the_ceiling_is_formed() -> None:
    """The reason this primitive exists rather than two hand-rolled loops.

    A huge trailing factor must be refused from the factor itself, without
    first materializing the product. Verified by bit_length: a computed
    product of these values would be astronomically large, so if the
    implementation multiplied first the ceiling check would come too late.
    """
    huge = 10**400
    with pytest.raises(CheckedArithmeticError) as excinfo:
        checked_product([huge, huge, huge], ceiling=1000)
    context = excinfo.value.context
    assert context["reason"] == "factor_exceeds_ceiling"
    assert context["index"] == 0, "must fail on the first oversized factor"


def test_running_product_is_checked_before_each_multiply() -> None:
    with pytest.raises(CheckedArithmeticError) as excinfo:
        checked_product([10, 10, 10], ceiling=150)
    context = excinfo.value.context
    assert context["reason"] == "product_exceeds_ceiling"
    assert context["index"] == 2, "100 is fine; the third factor is what breaks"
    assert context["running_total"] == 100


def test_failure_context_identifies_the_offending_factor() -> None:
    with pytest.raises(CheckedArithmeticError) as excinfo:
        checked_product([2, 3, 500], ceiling=100)
    context = excinfo.value.context
    assert context["index"] == 2
    assert context["value"] == 500
    assert context["ceiling"] == 100


# ── The two failure reasons are distinguishable ─────────────────────────────


def test_reasons_are_distinguishable_so_callers_can_map_their_own_messages() -> None:
    """SafeTensors maps these to two distinct published ValueError messages."""
    with pytest.raises(CheckedArithmeticError) as factor_case:
        checked_product([500], ceiling=100)
    with pytest.raises(CheckedArithmeticError) as product_case:
        checked_product([50, 50], ceiling=100)
    assert factor_case.value.context["reason"] == "factor_exceeds_ceiling"
    assert product_case.value.context["reason"] == "product_exceeds_ceiling"


def test_label_appears_in_the_message() -> None:
    with pytest.raises(CheckedArithmeticError, match="NRRD element count"):
        checked_product([50, 50], ceiling=100, label="NRRD element count")


# ── Caller bugs are ValueError, not CheckedArithmeticError ──────────────────


def test_negative_factor_is_a_caller_bug() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        checked_product([2, -1], ceiling=100)


def test_negative_ceiling_is_a_caller_bug() -> None:
    with pytest.raises(ValueError, match="ceiling must be non-negative"):
        checked_product([2], ceiling=-1)


@pytest.mark.parametrize("bad", [1.5, "3", None, True])
def test_non_integer_factor_is_a_caller_bug(bad: object) -> None:
    """bool is rejected too: True would silently behave as 1."""
    with pytest.raises(ValueError, match="must be an integer"):
        checked_product([2, bad], ceiling=100)  # type: ignore[list-item]


def test_zero_ceiling_admits_only_zero() -> None:
    assert checked_product([0], ceiling=0) == 0
    with pytest.raises(CheckedArithmeticError):
        checked_product([1], ceiling=0)


# ── The extraction did not change either archetype's contract ───────────────


def test_nrrd_still_raises_its_own_error_type() -> None:
    from format_factory.core import ResourceLimits
    from format_factory.nrrd.codec.payload import checked_element_count
    from format_factory.nrrd.errors import NrrdParseError

    limits = ResourceLimits()
    assert checked_element_count([2, 3], limits) == 6
    with pytest.raises(NrrdParseError, match="positive"):
        checked_element_count([2, 0], limits)


def test_safetensors_still_raises_valueerror_with_its_published_messages() -> None:
    from format_factory.safetensors import DType, TensorDescriptor

    with pytest.raises(ValueError, match="shape dimension exceeds unsigned 64-bit"):
        TensorDescriptor(
            name="t", dtype=DType.U8, shape=[1 << 65], data_offsets=(0, 0)
        )
    with pytest.raises(ValueError, match="shape element count overflows"):
        TensorDescriptor(
            name="t",
            dtype=DType.U8,
            shape=[1 << 40, 1 << 40],
            data_offsets=(0, 0),
        )
