"""NRRD-CONVERT-001 against the shipped namespace.

POL-SCR-CONVERT-01 (SHOULD): dtype/encoding/endian/layout conversions run
with explicit overflow/clipping/scaling/rounding policies and produce a
conversion report; semantics never change silently.

Scope of this obligation's evidence here: dtype conversion (including the
obligation's own worked example -- converting float data to a narrower type
under an explicit clipping policy with a report of affected values) and
endian conversion. Encoding conversion and attached/detached form conversion
are not covered -- see convert.py's own module docstring for why.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import (
    NrrdWriteError,
    OverflowPolicy,
    RoundingPolicy,
    convert_dtype,
    convert_endian,
)


# ── Dtype conversion: the obligation's own worked example ──────────────────


def test_narrowing_conversion_clips_out_of_range_values_and_reports_them() -> None:
    """"A developer converts float data to a narrower type under an explicit
    clipping policy with a report of affected values." """
    values = [10.0, 300.0, -50.0, 127.0]

    converted, report = convert_dtype(
        values,
        source_type="float",
        target_type="int8",
        overflow=OverflowPolicy.CLIP,
        rounding=RoundingPolicy.TRUNCATE,
    )

    assert converted == [10, 127, -50, 127]
    assert report.clipped_indices == (1,)
    assert report.is_lossless is False


def test_in_range_conversion_reports_lossless() -> None:
    converted, report = convert_dtype(
        [1.0, 2.0, 3.0],
        source_type="float",
        target_type="int8",
        overflow=OverflowPolicy.CLIP,
        rounding=RoundingPolicy.TRUNCATE,
    )

    assert converted == [1, 2, 3]
    assert report.is_lossless is True


def test_overflow_policy_raise_refuses_out_of_range_conversion() -> None:
    with pytest.raises(NrrdWriteError, match="does not fit"):
        convert_dtype(
            [300.0],
            source_type="float",
            target_type="int8",
            overflow=OverflowPolicy.RAISE,
            rounding=RoundingPolicy.TRUNCATE,
        )


def test_negative_overflow_is_clipped_to_the_lower_bound() -> None:
    converted, report = convert_dtype(
        [-500.0],
        source_type="float",
        target_type="int8",
        overflow=OverflowPolicy.CLIP,
        rounding=RoundingPolicy.TRUNCATE,
    )

    assert converted == [-128]
    assert report.clipped_indices == (0,)


def test_unsigned_target_clips_negative_values_to_zero() -> None:
    converted, report = convert_dtype(
        [-5.0, 10.0],
        source_type="float",
        target_type="uint8",
        overflow=OverflowPolicy.CLIP,
        rounding=RoundingPolicy.TRUNCATE,
    )

    assert converted == [0, 10]
    assert report.clipped_indices == (0,)


# ── Rounding is explicit, not defaulted ─────────────────────────────────────


def test_float_to_integer_conversion_requires_an_explicit_rounding_policy() -> None:
    """"There is no default: a caller must choose." Omitting rounding when
    converting a float source to an integer target is refused, not defaulted
    to truncation or any other behavior."""
    with pytest.raises(NrrdWriteError, match="RoundingPolicy"):
        convert_dtype(
            [1.5],
            source_type="float",
            target_type="int8",
            overflow=OverflowPolicy.CLIP,
        )


def test_truncate_and_round_half_up_disagree_and_both_are_honored() -> None:
    truncated, truncate_report = convert_dtype(
        [1.9], source_type="float", target_type="int8",
        overflow=OverflowPolicy.RAISE, rounding=RoundingPolicy.TRUNCATE,
    )
    rounded, round_report = convert_dtype(
        [1.9], source_type="float", target_type="int8",
        overflow=OverflowPolicy.RAISE, rounding=RoundingPolicy.ROUND_HALF_UP,
    )

    assert truncated == [1]
    assert rounded == [2]
    assert truncate_report.rounded_indices == (0,)
    assert round_report.rounded_indices == (0,)


def test_integer_to_integer_conversion_does_not_require_rounding() -> None:
    """No source value can be non-integral when the source type is itself an
    integer type, so rounding is genuinely optional here, not silently
    skipped."""
    converted, report = convert_dtype(
        [1, 2, 3],
        source_type="int16",
        target_type="int8",
        overflow=OverflowPolicy.CLIP,
    )

    assert converted == [1, 2, 3]
    assert report.rounding_policy is None


def test_widening_integer_conversion_needs_no_rounding_or_clipping() -> None:
    converted, report = convert_dtype(
        [100, -100],
        source_type="int8",
        target_type="int32",
        overflow=OverflowPolicy.RAISE,
    )

    assert converted == [100, -100]
    assert report.is_lossless is True


# ── Endian conversion ────────────────────────────────────────────────────────


def test_endian_conversion_byte_swaps_multibyte_elements() -> None:
    import struct

    little = struct.pack("<2H", 1, 256)

    swapped = convert_endian(little, type_name="uint16")

    assert struct.unpack(">2H", swapped) == (1, 256)
    assert swapped != little


def test_endian_conversion_round_trips() -> None:
    import struct

    original = struct.pack("<3i", 1, -2, 3)

    swapped_once = convert_endian(original, type_name="int32")
    swapped_twice = convert_endian(swapped_once, type_name="int32")

    assert swapped_twice == original
    assert swapped_once != original


def test_endian_conversion_is_a_documented_no_op_for_single_byte_types() -> None:
    payload = bytes([1, 2, 3, 4])

    result = convert_endian(payload, type_name="uint8")

    assert result == payload


def test_endian_conversion_rejects_a_payload_not_a_multiple_of_element_size() -> None:
    with pytest.raises(NrrdWriteError, match="multiple"):
        convert_endian(b"\x01\x02\x03", type_name="uint16")
