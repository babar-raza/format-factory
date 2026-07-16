"""SafeTensors dtype codec — decode raw tensor bytes into a real numpy.ndarray.

Single responsibility: translate a safetensors dtype string + raw bytes into
a numpy array with the correct shape/dtype (FACT-SAFETENSORS-102). BF16 and
the fp8 variants (F8_E4M3 / F8_E5M2, FACT-SAFETENSORS-106) have no native
numpy dtype, so this module decodes them via a real bit-level
reinterpretation into float32 rather than depending on the optional
`ml_dtypes` package.

Spec reference: FACT-SAFETENSORS-102, FACT-SAFETENSORS-106
"""

from __future__ import annotations

import numpy as np

from safetensors.exceptions import SafetensorsParseError

# Dtype string -> numpy dtype spec, for dtypes numpy supports natively.
_NUMPY_DTYPE_MAP: dict[str, str] = {
    "F16": "<f2",
    "F32": "<f4",
    "F64": "<f8",
    "I8": "i1",
    "I16": "<i2",
    "I32": "<i4",
    "I64": "<i8",
    "U8": "u1",
    "U16": "<u2",
    "U32": "<u4",
    "U64": "<u8",
    "BOOL": "?",
}

BF16_DTYPE = "BF16"
FP8_E4M3_DTYPE = "F8_E4M3"
FP8_E5M2_DTYPE = "F8_E5M2"


def _decode_minifloat_value(byte_val: int, exp_bits: int, mantissa_bits: int, bias: int) -> float:
    """Decode one IEEE-754-style minifloat byte into a Python float.

    Real bit-level reinterpretation (sign / exponent / mantissa), including
    zero, subnormal, normal, infinity, and NaN handling.
    """
    sign_shift = exp_bits + mantissa_bits
    sign = -1.0 if (byte_val >> sign_shift) & 0x1 else 1.0
    exp_mask = (1 << exp_bits) - 1
    mantissa_mask = (1 << mantissa_bits) - 1
    exponent = (byte_val >> mantissa_bits) & exp_mask
    mantissa = byte_val & mantissa_mask

    if exponent == exp_mask:
        # All exponent bits set: infinity (zero mantissa) or NaN, IEEE-754 style.
        if mantissa == 0:
            return sign * float("inf")
        return float("nan")
    if exponent == 0:
        if mantissa == 0:
            return sign * 0.0
        # Subnormal: no implicit leading 1 bit, minimum exponent (1 - bias).
        return sign * (mantissa / (1 << mantissa_bits)) * (2.0 ** (1 - bias))
    # Normal: implicit leading 1 bit.
    return sign * (1.0 + mantissa / (1 << mantissa_bits)) * (2.0 ** (exponent - bias))


def _build_fp8_lookup_table(exp_bits: int, mantissa_bits: int, bias: int) -> np.ndarray:
    """Precompute all 256 possible 1-byte values into a float32 lookup table."""
    table = np.empty(256, dtype=np.float32)
    for byte_val in range(256):
        table[byte_val] = _decode_minifloat_value(byte_val, exp_bits, mantissa_bits, bias)
    return table


# F8_E4M3: 1 sign + 4 exponent + 3 mantissa bits, bias 7.
_FP8_E4M3_TABLE = _build_fp8_lookup_table(exp_bits=4, mantissa_bits=3, bias=7)
# F8_E5M2: 1 sign + 5 exponent + 2 mantissa bits, bias 15.
_FP8_E5M2_TABLE = _build_fp8_lookup_table(exp_bits=5, mantissa_bits=2, bias=15)


def _decode_bf16(raw: bytes) -> np.ndarray:
    """Upcast bfloat16 bytes to float32 via the standard bit-shift widening.

    bfloat16 shares float32's sign/exponent layout with a truncated 7-bit
    mantissa, so left-shifting each 16-bit word by 16 bits and reinterpreting
    the result as float32 is an exact, well-defined decode — no precision is
    invented, this is the real bfloat16 -> float32 upcast.
    """
    u16 = np.frombuffer(raw, dtype="<u2")
    u32 = u16.astype(np.uint32) << 16
    return u32.view(np.float32)


def _decode_fp8(raw: bytes, table: np.ndarray) -> np.ndarray:
    """Decode 1-byte fp8 values to float32 via the precomputed lookup table."""
    indices = np.frombuffer(raw, dtype=np.uint8)
    return table[indices]


def numpy_dtype_for(dtype: str) -> str | None:
    """Return the numpy dtype spec string for a safetensors dtype, if native."""
    return _NUMPY_DTYPE_MAP.get(dtype)


def decode_tensor_array(raw: bytes, dtype: str, shape: list[int]) -> np.ndarray:
    """Decode raw tensor bytes into a numpy.ndarray using the descriptor's dtype/shape.

    FACT-SAFETENSORS-102: standard dtypes decode via numpy directly. BF16 and
    the fp8 dtypes have no native numpy dtype, so they go through a real
    bit-level reinterpretation (see `_decode_bf16` / `_decode_fp8`).
    """
    if dtype == BF16_DTYPE:
        arr = _decode_bf16(raw)
    elif dtype == FP8_E4M3_DTYPE:
        arr = _decode_fp8(raw, _FP8_E4M3_TABLE)
    elif dtype == FP8_E5M2_DTYPE:
        arr = _decode_fp8(raw, _FP8_E5M2_TABLE)
    elif dtype in _NUMPY_DTYPE_MAP:
        arr = np.frombuffer(raw, dtype=_NUMPY_DTYPE_MAP[dtype])
    else:
        raise SafetensorsParseError(f"Unsupported dtype for array decode: {dtype!r}")

    return arr.reshape(tuple(shape)) if shape else arr.reshape(())
