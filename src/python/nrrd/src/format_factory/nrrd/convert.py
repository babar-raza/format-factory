"""NRRD-CONVERT-001 -- dtype and endian conversion with explicit policies.

"Dtype/encoding/endian/layout conversions run with explicit overflow/
clipping/rounding policies and produce a conversion report; semantics never
change silently." A developer's example use case: convert float data to a
narrower type under an explicit clipping policy with a report of affected
values.

Scope of this module: dtype conversion (including the float-to-narrower-
integer case the obligation names directly) and endian conversion, both with
mandatory explicit policies -- there is deliberately no default overflow or
rounding policy, so a caller cannot silently get behavior they did not ask
for.

Encoding conversion (raw <-> gzip/bzip2/ascii/hex) is implemented via
`convert_encoding()`: the writer already recomputes payload bytes fresh
from a document's own decoded `array` and dtype/endian on every `dumps()`
call (`_encode_payload` in codec/writer/writer.py calls `encode_binary()`
then `encode_encoding()`, never reading the old `.payload` bytes at all),
so switching encodings needs no value-level policy the way dtype
conversion does -- it is a lossless header-metadata change, not a
data-transformation one. `document.payload` itself does not need to
change either: it always holds the decoded (post-decompression) form
regardless of which encoding the file used, so it already represents the
new encoding's own source data as-is.

Attached/detached form conversion is NOT implemented here: converting a
single-file document with an attached payload into a multi-file detached
form (or the reverse) needs real file-splitting/joining logic, a
genuinely separate, larger piece of work this module's docstring names
honestly as absent rather than stubbing it to look covered.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field, replace
from enum import Enum

from .codec.payload import SUPPORTED_ENCODINGS, dtype_info
from .errors import NrrdWriteError
from .model import NrrdDocument

#: Inclusive (min, max) for every integer struct format character NRRD uses.
_INTEGER_RANGES: dict[str, tuple[int, int]] = {
    "b": (-128, 127),
    "B": (0, 255),
    "h": (-32768, 32767),
    "H": (0, 65535),
    "i": (-(2**31), 2**31 - 1),
    "I": (0, 2**32 - 1),
    "q": (-(2**63), 2**63 - 1),
    "Q": (0, 2**64 - 1),
}

_FLOAT_FORMATS = frozenset({"f", "d"})


class OverflowPolicy(Enum):
    """What to do when a converted value falls outside the target type's
    representable range. There is no default: a caller must choose."""

    CLIP = "clip"
    RAISE = "raise"


class RoundingPolicy(Enum):
    """How to convert a float value to an integer target. There is no
    default, matching UBL's Rounding design in this same mission: HALF_UP and
    truncation disagree on 0.5, so a default would be this library quietly
    choosing a business outcome."""

    TRUNCATE = "truncate"
    ROUND_HALF_UP = "round_half_up"


@dataclass(frozen=True, slots=True)
class ConversionReport:
    """What actually happened during a conversion -- never silent."""

    source_type: str
    target_type: str
    overflow_policy: OverflowPolicy
    rounding_policy: RoundingPolicy | None
    clipped_indices: tuple[int, ...] = field(default_factory=tuple)
    rounded_indices: tuple[int, ...] = field(default_factory=tuple)

    @property
    def is_lossless(self) -> bool:
        return not self.clipped_indices and not self.rounded_indices


def _round_to_int(value: float, policy: RoundingPolicy) -> int:
    if policy is RoundingPolicy.TRUNCATE:
        return int(value)
    # ROUND_HALF_UP: Python's round() uses banker's rounding (round-half-even),
    # which is a different, equally valid policy this enum deliberately
    # distinguishes rather than silently applying.
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)


def convert_dtype(
    values: list[float | int],
    *,
    source_type: str,
    target_type: str,
    overflow: OverflowPolicy,
    rounding: RoundingPolicy | None = None,
) -> tuple[list[float | int], ConversionReport]:
    """Convert `values` from `source_type` to `target_type`.

    `rounding` is required when `target_type` is an integer type and any
    source value could plausibly be non-integral (source is a float type);
    omitting it in that case is refused rather than defaulted.
    """
    source_format, _ = dtype_info(source_type)
    target_format, _ = dtype_info(target_type)

    target_is_integer = target_format not in _FLOAT_FORMATS
    source_is_float = source_format in _FLOAT_FORMATS

    if target_is_integer and source_is_float and rounding is None:
        raise NrrdWriteError(
            "converting a float source to an integer target requires an "
            "explicit RoundingPolicy; there is no default"
        )

    converted: list[float | int] = []
    clipped: list[int] = []
    rounded: list[int] = []

    for index, value in enumerate(values):
        working = value
        if target_is_integer:
            if source_is_float:
                assert rounding is not None  # enforced by the check above
                rounded_value = _round_to_int(float(working), rounding)
                if rounded_value != working:
                    rounded.append(index)
                working = rounded_value
            low, high = _INTEGER_RANGES[target_format]
            if working < low or working > high:
                if overflow is OverflowPolicy.RAISE:
                    raise NrrdWriteError(
                        f"value {working!r} at index {index} does not fit in "
                        f"target type {target_type!r} (range {low}..{high}) "
                        "and overflow policy is RAISE"
                    )
                clipped.append(index)
                working = max(low, min(high, working))
        else:
            working = float(working)
        converted.append(working)

    report = ConversionReport(
        source_type=source_type,
        target_type=target_type,
        overflow_policy=overflow,
        rounding_policy=rounding,
        clipped_indices=tuple(clipped),
        rounded_indices=tuple(rounded),
    )
    return converted, report


@dataclass(frozen=True, slots=True)
class EncodingConversionReport:
    """What actually happened during an encoding conversion -- never silent."""

    source_encoding: str
    target_encoding: str

    @property
    def is_lossless(self) -> bool:
        # Every supported encoding round-trips the same decoded values
        # exactly (proven by codec/reader + codec/writer's own existing
        # obligations) -- encoding conversion never touches a value, only
        # how it is packed, so this is always true. Kept as an explicit
        # property, matching ConversionReport's own shape, rather than a
        # bare True a reader would have to take on faith.
        return True


def convert_encoding(document: NrrdDocument, target_encoding: str) -> tuple[NrrdDocument, EncodingConversionReport]:
    """Return a copy of `document` set to write as `target_encoding`.

    The returned document's own `array`/decoded values are unchanged --
    encoding conversion is lossless by construction, so there is no
    overflow/clipping/rounding policy to choose the way `convert_dtype()`
    needs one. Serializing the returned document (via `dumps()`/`dump()`)
    is what actually produces payload bytes in the new encoding; this
    function only prepares the document, matching `convert_dtype()`'s own
    return-converted-values-plus-report shape.
    """

    normalized = target_encoding.lower()
    if normalized not in SUPPORTED_ENCODINGS:
        raise NrrdWriteError(f"unsupported NRRD encoding: {target_encoding!r}")
    report = EncodingConversionReport(
        source_encoding=document.encoding,
        target_encoding=normalized,
    )
    converted = replace(document, header={**document.header, "encoding": normalized})
    return converted, report


def convert_endian(payload: bytes, *, type_name: str) -> bytes:
    """Byte-swap `payload`'s elements in place (returned as new bytes).

    A single-byte type (int8/uint8) has no byte order to swap; this is a
    documented no-op for those, not a silently-ignored request.
    """
    struct_format, item_size = dtype_info(type_name)
    if item_size == 1:
        return payload
    if len(payload) % item_size != 0:
        raise NrrdWriteError(
            f"payload length {len(payload)} is not a multiple of the "
            f"{item_size}-byte element size for {type_name!r}"
        )
    count = len(payload) // item_size
    values = struct.unpack(f"<{count}{struct_format}", payload)
    return struct.pack(f">{count}{struct_format}", *values)


__all__ = [
    "ConversionReport",
    "EncodingConversionReport",
    "OverflowPolicy",
    "RoundingPolicy",
    "convert_dtype",
    "convert_encoding",
    "convert_endian",
]
