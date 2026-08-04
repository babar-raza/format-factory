"""Bounded integer arithmetic shared by format readers.

visibility: generated
generated_by: claude

Extracted under TC-FF6-SHARED-CHECKED-ARITHMETIC-001 (directive GAP-010) after
two independent product archetypes -- NRRD and SafeTensors -- were each found to
hand-roll the same bounded multiply, and to have already diverged on how they do
it (NRRD checked the running product *after* each multiply, SafeTensors
*before*).

Deliberately narrow. The comparison in that taskcard found that almost
everything surrounding this multiply is legitimately format-specific: what the
ceiling *means* (a configurable memory budget for NRRD, a representational u64
limit for SafeTensors), whether a zero dimension is valid (it is for
SafeTensors, it is not for NRRD), and which exception type each format's callers
depend on. Only the bounded multiply itself is genuinely shared, so only the
bounded multiply is here. Callers keep their own validation and translate
``CheckedArithmeticError`` into their own public error type.
"""

from __future__ import annotations

from collections.abc import Iterable

from .errors import FormatFactoryError


class CheckedArithmeticError(FormatFactoryError):
    """A bounded arithmetic operation would exceed its declared ceiling."""

    code = "checked_arithmetic_error"


def checked_product(
    values: Iterable[int], *, ceiling: int, label: str = "product"
) -> int:
    """Multiply ``values``, refusing to exceed ``ceiling``.

    The ceiling is tested *before* each multiplication, so no intermediate
    larger than ``ceiling`` is ever formed. That matters for hostile input:
    a header declaring a handful of enormous dimensions is rejected from the
    dimensions themselves rather than after materializing their product.

    Zero is permitted and makes the product ``0`` -- whether a zero dimension is
    *meaningful* is a format question, so callers that forbid it must reject it
    before calling. A zero does **not** short-circuit: every remaining factor is
    still validated, so a malformed factor after a zero is still reported rather
    than masked. An empty ``values`` yields ``1``, the empty product.

    Args:
        values: Non-negative integers to multiply.
        ceiling: Inclusive upper bound for both each value and the product.
        label: Noun used in the error message, e.g. ``"NRRD element count"``.

    Returns:
        The product, guaranteed ``<= ceiling``.

    Raises:
        CheckedArithmeticError: A value or the running product exceeds
            ``ceiling``.
        ValueError: ``ceiling`` is negative, or a value is negative or not an
            integer. These are caller bugs rather than bad input.
    """
    if ceiling < 0:
        raise ValueError(f"ceiling must be non-negative, got {ceiling}")

    total = 1
    saw_zero = False
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"{label} factor {index} must be an integer, "
                f"not {type(value).__name__}"
            )
        if value < 0:
            raise ValueError(f"{label} factor {index} must be non-negative")
        if value > ceiling:
            raise CheckedArithmeticError(
                f"{label} factor {index} exceeds its limit: {value} > {ceiling}",
                context={"reason": "factor_exceeds_ceiling", "label": label,
                         "index": index, "value": value, "ceiling": ceiling},
            )
        if value == 0:
            # Keep validating the remaining factors rather than short-circuiting,
            # so a malformed factor after a zero is still reported.
            saw_zero = True
            continue
        if saw_zero:
            continue
        # Tested before multiplying, so `total` never exceeds `ceiling`.
        if total > ceiling // value:
            raise CheckedArithmeticError(
                f"{label} exceeds its limit at factor {index}: "
                f"{total} * {value} > {ceiling}",
                context={"reason": "product_exceeds_ceiling", "label": label,
                         "index": index, "value": value,
                         "running_total": total, "ceiling": ceiling},
            )
        total *= value
    return 0 if saw_zero else total
