"""
ZST analytics functions.

Arithmetic combination and derivative functions extracted from zst_codec.py to keep
the core codec file within its baseline_loc_cap of 4210 lines.

Core domain functions remain in zst_codec. These functions are re-exported via
zst_codec's 'from .zst_analytics import *' for backward compatibility.

Do NOT add new functions to this file without a corresponding GAP-ledger entry.
"""
from __future__ import annotations

from pathlib import Path

from .zst_codec import (
    zst_compressed_size,
    zst_decompressed_size,
    zst_file_size_bytes,
    zst_frame_count,
    zst_header_size,
    zst_overhead_bytes,
)


def zst_compressed_size_minus_frame_count(path: "str | Path") -> int:
    """Return compressed file size minus frame count. 0 if result is negative."""
    result = zst_compressed_size(path) - zst_frame_count(path)
    return max(0, result)


def zst_compressed_size_plus_frame_count(path: "str | Path") -> int:
    """Return the sum of compressed file size and frame count."""
    return zst_compressed_size(path) + zst_frame_count(path)


def zst_overhead_ratio_exceeds_half(path: "str | Path") -> bool:
    """Return True if header size / compressed size exceeds 0.5."""
    size = zst_compressed_size(path)
    if size == 0:
        return False
    return (zst_header_size(path) / size) > 0.5


def zst_size_exceeds_50(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 50 bytes."""
    return zst_compressed_size(path) > 50


def zst_compressed_size_plus_header_size(path: "str | Path") -> int:
    """Return the sum of compressed file size and header size."""
    return zst_compressed_size(path) + zst_header_size(path)


def zst_compressed_size_exceeds_20(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 20 bytes."""
    return zst_compressed_size(path) > 20


def zst_compressed_size_minus_12(path: "str | Path") -> int:
    """Return compressed file size minus 12. 0 if result is negative."""
    return max(0, zst_compressed_size(path) - 12)


def zst_compressed_size_exceeds_60(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 60 bytes."""
    return zst_compressed_size(path) > 60


def zst_compressed_size_plus_12(path: "str | Path") -> int:
    """Return compressed file size plus 12."""
    return zst_compressed_size(path) + 12


def zst_compressed_size_exceeds_30(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 30 bytes."""
    return zst_compressed_size(path) > 30


def zst_decompressed_byte_sum(path: "str | Path") -> int:
    """Return sum of all byte values in the decompressed content. 0 if empty or error."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return sum(data)


def zst_compressed_to_decompressed_diff(path: "str | Path") -> int:
    """Return absolute difference between decompressed and compressed sizes in bytes."""
    ds = zst_decompressed_size(path)
    cs = zst_compressed_size(path)
    return abs(ds - cs)


def zst_frame_count_exceeds_one(path: "str | Path") -> bool:
    """Return True if the file contains more than one Zstandard frame."""
    return zst_frame_count(path) > 1


def zst_max_byte_value(path: "str | Path") -> int:
    """Return the maximum byte value (0-255) in the decompressed content. 0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return max(data) if data else 0


def zst_min_byte_value(path: "str | Path") -> int:
    """Return the minimum byte value (0-255) in the decompressed content. 0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    return min(data) if data else 0


def zst_decompressed_byte_range(path: "str | Path") -> int:
    """Return range (max minus min) of byte values in decompressed content. 0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0
    if not data:
        return 0
    return max(data) - min(data)


def zst_avg_decompressed_byte_value(path: "str | Path") -> float:
    """Return mean byte value (0.0-255.0) of decompressed content. 0.0 if empty."""
    try:
        import zstandard as zstd
        with open(path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            data = dctx.decompress(fh.read(), max_output_size=1 << 24)
    except Exception:
        return 0.0
    if not data:
        return 0.0
    return sum(data) / len(data)


def zst_compressed_size_plus_24(path: "str | Path") -> int:
    """Return compressed file size plus 24."""
    return zst_compressed_size(path) + 24


def zst_compressed_size_exceeds_10(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 10 bytes."""
    return zst_compressed_size(path) > 10


def zst_compressed_size_minus_24(path: "str | Path") -> int:
    """Return compressed file size minus 24. 0 if result is negative."""
    return max(0, zst_compressed_size(path) - 24)


def zst_compressed_size_exceeds_40(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 40 bytes."""
    return zst_compressed_size(path) > 40


def zst_compressed_size_plus_36(path: "str | Path") -> int:
    """Return compressed file size plus 36."""
    return zst_compressed_size(path) + 36


def zst_compressed_size_exceeds_70(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 70 bytes."""
    return zst_compressed_size(path) > 70


def zst_byte_sum_per_frame(path: "str | Path") -> int:
    """Return decompressed byte sum divided by frame count (integer). 0 if no frames."""
    fc = zst_frame_count(path)
    if fc == 0:
        return 0
    return zst_decompressed_byte_sum(path) // fc


def zst_compressed_plus_decompressed_size(path: "str | Path") -> int:
    """Return compressed file size plus decompressed file size in bytes."""
    return zst_compressed_size(path) + zst_decompressed_size(path)


def zst_compressed_size_minus_36(path: "str | Path") -> int:
    """Return compressed file size minus 36. 0 if result is negative."""
    return max(0, zst_compressed_size(path) - 36)


def zst_compressed_size_exceeds_80(path: "str | Path") -> bool:
    """Return True if compressed file size exceeds 80 bytes."""
    return zst_compressed_size(path) > 80


def zst_byte_sum_minus_decompressed_size(path: "str | Path") -> int:
    """Return decompressed byte sum minus decompressed size. 0 if result would be negative."""
    return max(0, zst_decompressed_byte_sum(path) - zst_decompressed_size(path))


def zst_compressed_size_plus_frame_count(path: "str | Path") -> int:
    """Return compressed file size plus frame count."""
    return zst_compressed_size(path) + zst_frame_count(path)


def zst_max_byte_value_plus_min_byte_value(path: "str | Path") -> int:
    """Return max decompressed byte value plus min decompressed byte value. 0 if empty."""
    return zst_max_byte_value(path) + zst_min_byte_value(path)


def zst_compressed_size_minus_min_byte_value(path: "str | Path") -> int:
    """Return compressed file size minus min decompressed byte value. 0 if result negative."""
    return max(0, zst_compressed_size(path) - zst_min_byte_value(path))


def zst_decompressed_size_times_compressed_size(path: "str | Path") -> int:
    """Return decompressed file size multiplied by compressed file size in bytes."""
    return zst_decompressed_size(path) * zst_compressed_size(path)


def zst_avg_byte_value_int(path: "str | Path") -> int:
    """Return average decompressed byte value as integer (byte_sum // decompressed_size). 0 if empty."""
    ds = zst_decompressed_size(path)
    if ds == 0:
        return 0
    return zst_decompressed_byte_sum(path) // ds


def zst_max_byte_value_minus_avg_byte_value(path: "str | Path") -> int:
    """Return max decompressed byte value minus avg byte value (integer). 0 if result negative."""
    return max(0, zst_max_byte_value(path) - zst_avg_byte_value_int(path))


def zst_decompressed_size_plus_max_byte(path: "str | Path") -> int:
    """Return decompressed file size plus max decompressed byte value."""
    return zst_decompressed_size(path) + zst_max_byte_value(path)


def zst_decompressed_exceeds_compressed(path: "str | Path") -> bool:
    """Return True if decompressed size is larger than compressed size."""
    return zst_decompressed_size(path) > zst_compressed_size(path)


def zst_decompressed_content_ratio(path: "str | Path") -> float:
    """Return ratio of decompressed size to (decompressed + compressed). 0.0 if both zero."""
    ds = zst_decompressed_size(path)
    cs = zst_compressed_size(path)
    total = ds + cs
    return ds / total if total > 0 else 0.0


def zst_compressed_size_times_avg_byte_value(path: "str | Path") -> int:
    """Return compressed file size multiplied by average decompressed byte value (integer)."""
    return zst_compressed_size(path) * zst_avg_byte_value_int(path)


def zst_decompressed_size_div_compressed_size(path: "str | Path") -> int:
    """Return decompressed file size divided by compressed file size (integer floor). 0 if compressed is 0."""
    cs = zst_compressed_size(path)
    if cs == 0:
        return 0
    return zst_decompressed_size(path) // cs


def zst_byte_sum_plus_compressed_size(path: "str | Path") -> int:
    """Return decompressed byte sum plus compressed file size."""
    return zst_decompressed_byte_sum(path) + zst_compressed_size(path)


def zst_compressed_size_times_10(path: "str | Path") -> int:
    """Return compressed file size multiplied by 10."""
    return zst_compressed_size(path) * 10


def zst_byte_sum_div_100(path: "str | Path") -> int:
    """Return decompressed byte sum divided by 100 (integer floor)."""
    return zst_decompressed_byte_sum(path) // 100


def zst_decompressed_size_plus_compressed_size_times_2(path: "str | Path") -> int:
    """Return decompressed file size plus compressed file size multiplied by 2."""
    return zst_decompressed_size(path) + zst_compressed_size(path) * 2


def zst_max_byte_value_times_frame_count(path: "str | Path") -> int:
    """Return max decompressed byte value multiplied by frame count."""
    return zst_max_byte_value(path) * zst_frame_count(path)


def zst_decompressed_size_minus_byte_sum_div_10(path: "str | Path") -> int:
    """Return decompressed size minus (byte_sum // 10). 0 if result negative."""
    return max(0, zst_decompressed_size(path) - zst_decompressed_byte_sum(path) // 10)


def zst_compressed_size_minus_frame_count_times_5(path: "str | Path") -> int:
    """Return compressed file size minus (frame count * 5). 0 if result negative."""
    return max(0, zst_compressed_size(path) - zst_frame_count(path) * 5)


def zst_byte_sum_div_decompressed_size(path: "str | Path") -> int:
    """Return byte sum divided by decompressed size (integer floor). 0 if decompressed size is 0."""
    ds = zst_decompressed_size(path)
    if ds == 0:
        return 0
    return zst_decompressed_byte_sum(path) // ds


def zst_max_byte_value_plus_compressed_size(path: "str | Path") -> int:
    """Return max decompressed byte value plus compressed file size."""
    return zst_max_byte_value(path) + zst_compressed_size(path)


def zst_decompressed_size_times_frame_count(path: "str | Path") -> int:
    """Return decompressed file size multiplied by frame count."""
    return zst_decompressed_size(path) * zst_frame_count(path)


def zst_compressed_plus_decompressed_size_div_2(path: "str | Path") -> int:
    """Return (compressed size + decompressed size) // 2."""
    return (zst_compressed_size(path) + zst_decompressed_size(path)) // 2


def zst_byte_sum_minus_compressed_size(path: "str | Path") -> int:
    """Return decompressed byte sum minus compressed file size. 0 if result negative."""
    return max(0, zst_decompressed_byte_sum(path) - zst_compressed_size(path))


def zst_max_byte_value_times_decompressed_size(path: "str | Path") -> int:
    """Return max decompressed byte value multiplied by decompressed file size."""
    return zst_max_byte_value(path) * zst_decompressed_size(path)


def zst_byte_sum_div_1000(path: "str | Path") -> int:
    """Return decompressed byte sum divided by 1000 (integer floor). 0 if byte sum is 0."""
    return zst_decompressed_byte_sum(path) // 1000


def zst_decompressed_size_minus_max_byte(path: "str | Path") -> int:
    """Return decompressed file size minus max decompressed byte value. 0 if result negative."""
    return max(0, zst_decompressed_size(path) - zst_max_byte_value(path))


def zst_compressed_size_squared(path: "str | Path") -> int:
    """Return compressed file size squared (multiplied by itself)."""
    cs = zst_compressed_size(path)
    return cs * cs


def zst_decompressed_size_times_100(path: "str | Path") -> int:
    """Return decompressed file size multiplied by 100."""
    return zst_decompressed_size(path) * 100


def zst_byte_sum_plus_compressed_size_times_2(path: "str | Path") -> int:
    """Return decompressed byte sum plus compressed file size multiplied by 2."""
    return zst_decompressed_byte_sum(path) + zst_compressed_size(path) * 2


def zst_decompressed_size_times_10_plus_compressed_size(path: "str | Path") -> int:
    """Return decompressed size multiplied by 10, plus compressed size."""
    return zst_decompressed_size(path) * 10 + zst_compressed_size(path)


def zst_byte_sum_div_compressed_size(path: "str | Path") -> int:
    """Return decompressed byte sum floor-divided by compressed size. 0 if cs==0."""
    cs = zst_compressed_size(path)
    return 0 if cs == 0 else zst_decompressed_byte_sum(path) // cs


def zst_max_byte_times_compressed_size_div_100(path: "str | Path") -> int:
    """Return (max_byte_value * compressed_size) // 100."""
    return zst_max_byte_value(path) * zst_compressed_size(path) // 100


def zst_decompressed_plus_compressed_size_times_2(path: "str | Path") -> int:
    """Return (decompressed_size + compressed_size) * 2."""
    return (zst_decompressed_size(path) + zst_compressed_size(path)) * 2


def zst_decompressed_size_plus_max_byte_times_compressed_size_div_10(path: "str | Path") -> int:
    """Return decompressed_size plus (max_byte * compressed_size // 10)."""
    return zst_decompressed_size(path) + zst_max_byte_value(path) * zst_compressed_size(path) // 10


def zst_compressed_size_times_10_plus_decompressed_size_div_10(path: "str | Path") -> int:
    """Return (compressed_size * 10) plus (decompressed_size // 10)."""
    return zst_compressed_size(path) * 10 + zst_decompressed_size(path) // 10


def zst_byte_sum_div_100_plus_compressed_size(path: "str | Path") -> int:
    """Return (decompressed byte sum // 100) plus compressed size."""
    return zst_decompressed_byte_sum(path) // 100 + zst_compressed_size(path)


def zst_decompressed_size_times_compressed_size_div_1000(path: "str | Path") -> int:
    """Return (decompressed_size * compressed_size) // 1000."""
    return zst_decompressed_size(path) * zst_compressed_size(path) // 1000


def zst_compressed_size_per_frame(path: "str | Path") -> float:
    """Return compressed file size divided by frame count. 0.0 if no frames."""
    fc = zst_frame_count(path)
    if fc == 0:
        return 0.0
    return zst_compressed_size(path) / fc


def zst_min_byte_exceeds_zero(path: "str | Path") -> bool:
    """Return True if the minimum decompressed byte value is greater than zero."""
    return zst_min_byte_value(path) > 0


def zst_header_size_plus_frame_count(path: "str | Path") -> int:
    """Return header size plus frame count."""
    return zst_header_size(path) + zst_frame_count(path)


def zst_decompressed_size_squared(path: "str | Path") -> int:
    """Return the square of the decompressed size."""
    ds = zst_decompressed_size(path)
    return ds * ds



def zst_byte_sum_plus_decompressed_size_times_100(path: "str | Path") -> int:
    """Return byte_sum plus (decompressed_size * 100)."""
    return zst_decompressed_byte_sum(path) + zst_decompressed_size(path) * 100


def zst_compressed_size_times_decompressed_size_div_100(path: "str | Path") -> int:
    """Return (compressed_size * decompressed_size) // 100."""
    return zst_compressed_size(path) * zst_decompressed_size(path) // 100



def zst_max_byte_plus_min_byte_times_compressed_size(path: "str | Path") -> int:
    """Return (max_byte + min_byte) * compressed_size."""
    return (zst_max_byte_value(path) + zst_min_byte_value(path)) * zst_compressed_size(path)


def zst_decompressed_size_div_10_plus_byte_sum_div_1000(path: "str | Path") -> int:
    """Return (decompressed_size // 10) plus (byte_sum // 1000)."""
    return zst_decompressed_size(path) // 10 + zst_decompressed_byte_sum(path) // 1000



def zst_compressed_size_plus_max_byte_minus_min_byte(path: "str | Path") -> int:
    """Return compressed_size + max_byte - min_byte."""
    return zst_compressed_size(path) + zst_max_byte_value(path) - zst_min_byte_value(path)


def zst_byte_sum_div_decompressed_size(path: "str | Path") -> int:
    """Return byte_sum // decompressed_size (0 if decompressed_size is 0)."""
    ds = zst_decompressed_size(path)
    return 0 if ds == 0 else zst_decompressed_byte_sum(path) // ds


def zst_frame_count_squared(path: "str | Path") -> int:
    """Return the square of the frame count."""
    fc = zst_frame_count(path)
    return fc * fc


def zst_overhead_bytes_squared(path: "str | Path") -> int:
    """Return the square of the overhead bytes."""
    ob = zst_overhead_bytes(path)
    return ob * ob



def zst_decompressed_size_mod_100_plus_max_byte(path: "str | Path") -> int:
    """Return (decompressed_size % 100) + max_byte."""
    return zst_decompressed_size(path) % 100 + zst_max_byte_value(path)


def zst_compressed_size_div_5_plus_byte_sum_div_10000(path: "str | Path") -> int:
    """Return (compressed_size // 5) + (byte_sum // 10000)."""
    return zst_compressed_size(path) // 5 + zst_decompressed_byte_sum(path) // 10000



def zst_max_byte_times_10_plus_compressed_size_div_5(path: "str | Path") -> int:
    """Return (max_byte * 10) + (compressed_size // 5)."""
    return zst_max_byte_value(path) * 10 + zst_compressed_size(path) // 5


def zst_byte_sum_mod_1000_plus_decompressed_size(path: "str | Path") -> int:
    """Return (byte_sum % 1000) + decompressed_size."""
    return zst_decompressed_byte_sum(path) % 1000 + zst_decompressed_size(path)


def zst_compressed_size_squared(path: "str | Path") -> int:
    """Return the square of the compressed size."""
    cs = zst_compressed_size(path)
    return cs * cs


def zst_decompressed_plus_compressed(path: "str | Path") -> int:
    """Return decompressed size plus compressed size."""
    return zst_decompressed_size(path) + zst_compressed_size(path)


def zst_decompressed_size_plus_max_byte_times_compressed_size_div_100(path: "str | Path") -> int:
    """Return decompressed_size + (max_byte * compressed_size) // 100."""
    return zst_decompressed_size(path) + zst_max_byte_value(path) * zst_compressed_size(path) // 100


def zst_byte_sum_mod_500_plus_compressed_size_times_2(path: "str | Path") -> int:
    """Return (byte_sum % 500) + (compressed_size * 2)."""
    return zst_decompressed_byte_sum(path) % 500 + zst_compressed_size(path) * 2


def zst_max_byte_times_decompressed_size_plus_compressed_size_div_10(path: "str | Path") -> int:
    """Return max_byte * decompressed_size + compressed_size // 10."""
    return zst_max_byte_value(path) * zst_decompressed_size(path) + zst_compressed_size(path) // 10


def zst_byte_sum_div_100_plus_max_byte_times_2_plus_compressed_size(path: "str | Path") -> int:
    """Return byte_sum // 100 + max_byte * 2 + compressed_size."""
    return zst_decompressed_byte_sum(path) // 100 + zst_max_byte_value(path) * 2 + zst_compressed_size(path)


def zst_compressed_size_times_max_byte_plus_1_plus_min_byte_times_10(path: "str | Path") -> int:
    """Return compressed_size * (max_byte + 1) + min_byte * 10."""
    return zst_compressed_size(path) * (zst_max_byte_value(path) + 1) + zst_min_byte_value(path) * 10


def zst_decompressed_size_times_compressed_size_mod_10000_plus_max_byte(path: "str | Path") -> int:
    """Return (decompressed_size * compressed_size) % 10000 + max_byte."""
    return (zst_decompressed_size(path) * zst_compressed_size(path)) % 10000 + zst_max_byte_value(path)


def zst_byte_sum_div_compressed_size_plus_1_plus_compressed_size_div_10(path: "str | Path") -> int:
    """Return byte_sum // (compressed_size + 1) + compressed_size // 10."""
    return zst_decompressed_byte_sum(path) // (zst_compressed_size(path) + 1) + zst_compressed_size(path) // 10


def zst_max_byte_times_min_byte_plus_compressed_size_times_10(path: "str | Path") -> int:
    """Return max_byte * min_byte + compressed_size * 10."""
    return zst_max_byte_value(path) * zst_min_byte_value(path) + zst_compressed_size(path) * 10


def zst_decompressed_size_plus_max_byte_times_compressed_size_div_100_plus_compressed_size_div_10(path: "str | Path") -> int:
    """Return (decompressed_size + max_byte) * compressed_size // 100 + compressed_size // 10."""
    return (zst_decompressed_size(path) + zst_max_byte_value(path)) * zst_compressed_size(path) // 100 + zst_compressed_size(path) // 10


def zst_byte_sum_div_1000_plus_min_byte_times_compressed_size_div_100_plus_decompressed_size(path: "str | Path") -> int:
    """Return byte_sum // 1000 + min_byte * compressed_size // 100 + decompressed_size."""
    return zst_decompressed_byte_sum(path) // 1000 + zst_min_byte_value(path) * zst_compressed_size(path) // 100 + zst_decompressed_size(path)


def zst_decompressed_size_times_max_byte_plus_1_div_10_plus_compressed_size_mod_100(path: "str | Path") -> int:
    """Return decompressed_size * (max_byte + 1) // 10 + compressed_size % 100."""
    return zst_decompressed_size(path) * (zst_max_byte_value(path) + 1) // 10 + zst_compressed_size(path) % 100


def zst_byte_sum_mod_1000_plus_decompressed_size_times_2_plus_compressed_size_mod_50(path: "str | Path") -> int:
    """Return byte_sum % 1000 + decompressed_size * 2 + compressed_size % 50."""
    return zst_decompressed_byte_sum(path) % 1000 + zst_decompressed_size(path) * 2 + zst_compressed_size(path) % 50


def zst_compressed_size_times_decompressed_size_div_1000_plus_max_byte_plus_1_mod_100(path: "str | Path") -> int:
    """Return compressed_size * decompressed_size // 1000 + (max_byte + 1) % 100."""
    return zst_compressed_size(path) * zst_decompressed_size(path) // 1000 + (zst_max_byte_value(path) + 1) % 100


def zst_byte_sum_div_10000_plus_decompressed_size_mod_100_plus_compressed_size_div_20(path: "str | Path") -> int:
    """Return byte_sum // 10000 + decompressed_size % 100 + compressed_size // 20."""
    return zst_decompressed_byte_sum(path) // 10000 + zst_decompressed_size(path) % 100 + zst_compressed_size(path) // 20


def zst_frame_count_times_two(path: "str | Path") -> int:
    """Return the frame count multiplied by two."""
    return zst_frame_count(path) * 2


def zst_header_size_squared(path: "str | Path") -> int:
    """Return the square of the header size."""
    hs = zst_header_size(path)
    return hs * hs


def zst_decompressed_size_times_two(path: "str | Path") -> int:
    """Return the decompressed size multiplied by two."""
    return zst_decompressed_size(path) * 2


def zst_min_byte_value_times_two(path: "str | Path") -> int:
    """Return the minimum byte value multiplied by two."""
    return zst_min_byte_value(path) * 2


def zst_frame_count_times_two(path: "str | Path") -> int:
    """Return the frame count multiplied by two."""
    return zst_frame_count(path) * 2


def zst_max_byte_minus_min_byte_times_compressed_size_div_100_plus_decompressed_size(path: "str | Path") -> int:
    """Return (max_byte - min_byte) * compressed_size // 100 + decompressed_size."""
    return (zst_max_byte_value(path) - zst_min_byte_value(path)) * zst_compressed_size(path) // 100 + zst_decompressed_size(path)


def zst_byte_sum_div_500_plus_max_byte_times_min_byte_div_10_plus_compressed_size(path: "str | Path") -> int:
    """Return byte_sum // 500 + max_byte * min_byte // 10 + compressed_size."""
    return zst_decompressed_byte_sum(path) // 500 + zst_max_byte_value(path) * zst_min_byte_value(path) // 10 + zst_compressed_size(path)


def zst_compressed_size_mod_100_plus_decompressed_size_mod_50_plus_max_byte_times_3(path: "str | Path") -> int:
    """Return compressed_size % 100 + decompressed_size % 50 + max_byte * 3."""
    return zst_compressed_size(path) % 100 + zst_decompressed_size(path) % 50 + zst_max_byte_value(path) * 3


def zst_byte_sum_div_1000_plus_compressed_size_times_decompressed_size_mod_1000(path: "str | Path") -> int:
    """Return byte_sum // 1000 + compressed_size * decompressed_size % 1000."""
    return zst_decompressed_byte_sum(path) // 1000 + zst_compressed_size(path) * zst_decompressed_size(path) % 1000


def zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200(path: "str | Path") -> int:
    """Return (max_byte + 1) * compressed_size % 100 + decompressed_size % 200."""
    return (zst_max_byte_value(path) + 1) * zst_compressed_size(path) % 100 + zst_decompressed_size(path) % 200


def zst_byte_sum_mod_500_plus_compressed_size_plus_max_byte_times_decompressed_size_div_100(path: "str | Path") -> int:
    """Return byte_sum % 500 + compressed_size + max_byte * decompressed_size // 100."""
    return zst_decompressed_byte_sum(path) % 500 + zst_compressed_size(path) + zst_max_byte_value(path) * zst_decompressed_size(path) // 100


def zst_decompressed_size_mod_100_plus_compressed_size_mod_50_plus_max_byte_plus_1_times_10(path: "str | Path") -> int:
    """Return ds % 100 + cs % 50 + (max_byte + 1) * 10."""
    return zst_decompressed_size(path) % 100 + zst_compressed_size(path) % 50 + (zst_max_byte_value(path) + 1) * 10


def zst_byte_sum_div_2000_plus_decompressed_size_mod_300_plus_compressed_size_times_3_mod_1000(path: "str | Path") -> int:
    """Return byte_sum // 2000 + decompressed_size % 300 + compressed_size * 3 % 1000."""
    return zst_decompressed_byte_sum(path) // 2000 + zst_decompressed_size(path) % 300 + zst_compressed_size(path) * 3 % 1000


def zst_compressed_size_mod_7_times_100_plus_max_byte_times_decompressed_size_div_50_plus_10(path: "str | Path") -> int:
    """Return cs % 7 * 100 + max_byte * ds // 50 + 10."""
    return zst_compressed_size(path) % 7 * 100 + zst_max_byte_value(path) * zst_decompressed_size(path) // 50 + 10


def zst_byte_sum_mod_1000_plus_decompressed_size_times_3_mod_500_plus_compressed_size_mod_100(path: "str | Path") -> int:
    """Return byte_sum % 1000 + ds * 3 % 500 + cs % 100."""
    return zst_decompressed_byte_sum(path) % 1000 + zst_decompressed_size(path) * 3 % 500 + zst_compressed_size(path) % 100


def zst_byte_count_squared(path: "str | Path") -> int:
    """Return the square of the decompressed byte sum."""
    bc = zst_decompressed_byte_sum(path)
    return bc * bc


def zst_max_byte_value_squared(path: "str | Path") -> int:
    """Return the square of the max byte value."""
    mb = zst_max_byte_value(path)
    return mb * mb


def zst_avg_byte_value_int_squared(path: "str | Path") -> int:
    """Return the square of the average byte value (integer)."""
    av = zst_avg_byte_value_int(path)
    return av * av


def zst_decompressed_byte_sum_mod_500_plus_compressed_size_times_3_plus_max_byte_times_100(path: "str | Path") -> int:
    """Return byte_sum % 500 + cs * 3 + max_byte * 100."""
    return zst_decompressed_byte_sum(path) % 500 + zst_compressed_size(path) * 3 + zst_max_byte_value(path) * 100


def zst_decompressed_size_mod_41_times_5_plus_byte_sum_mod_200_plus_compressed_size_times_7(path: "str | Path") -> int:
    """Return ds % 41 * 5 + byte_sum % 200 + cs * 7."""
    return zst_decompressed_size(path) % 41 * 5 + zst_decompressed_byte_sum(path) % 200 + zst_compressed_size(path) * 7


def zst_max_byte_times_decompressed_size_mod_300_plus_compressed_size_times_5_plus_byte_sum_mod_700(path: "str | Path") -> int:
    """Return mx * ds % 300 + cs * 5 + byte_sum % 700."""
    return zst_max_byte_value(path) * zst_decompressed_size(path) % 300 + zst_compressed_size(path) * 5 + zst_decompressed_byte_sum(path) % 700


def zst_compressed_size_mod_53_times_4_plus_max_byte_times_10_plus_decompressed_size_mod_100(path: "str | Path") -> int:
    """Return cs % 53 * 4 + max_byte * 10 + ds % 100."""
    return zst_compressed_size(path) % 53 * 4 + zst_max_byte_value(path) * 10 + zst_decompressed_size(path) % 100


def zst_compressed_size_times_three(path: "str | Path") -> int:
    return zst_compressed_size(path) * 3


def zst_frame_count_times_three(path: "str | Path") -> int:
    return zst_frame_count(path) * 3


def zst_decompressed_size_times_three(path: "str | Path") -> int:
    return zst_decompressed_size(path) * 3


def zst_file_size_times_three(path: "str | Path") -> int:
    return zst_file_size_bytes(path) * 3


def zst_compressed_size_times_four(path: "str | Path") -> int:
    return zst_compressed_size(path) * 4


def zst_frame_count_times_four(path: "str | Path") -> int:
    return zst_frame_count(path) * 4


def zst_file_size_times_four(path: "str | Path") -> int:
    """Return file size in bytes multiplied by four."""
    return zst_file_size_bytes(path) * 4


def zst_decompressed_size_times_four(path: "str | Path") -> int:
    """Return decompressed size multiplied by four."""
    return zst_decompressed_size(path) * 4


def zst_file_size_times_five(file_path: "str | Path") -> int:
    """Return file size multiplied by five."""
    return zst_file_size_bytes(file_path) * 5


def zst_decompressed_size_times_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by five."""
    return zst_decompressed_size(file_path) * 5


def zst_file_size_times_six(file_path: "str | Path") -> int:
    """Return file size multiplied by six."""
    return zst_file_size_bytes(file_path) * 6


def zst_decompressed_size_times_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by six."""
    return zst_decompressed_size(file_path) * 6


def zst_file_size_times_seven(file_path: "str | Path") -> int:
    """Return file size multiplied by seven."""
    return zst_file_size_bytes(file_path) * 7


def zst_decompressed_size_times_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seven."""
    return zst_decompressed_size(file_path) * 7


def zst_file_size_times_eight(file_path: "str | Path") -> int:
    """Return file size multiplied by eight."""
    return zst_file_size_bytes(file_path) * 8


def zst_decompressed_size_times_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eight."""
    return zst_decompressed_size(file_path) * 8


def zst_file_size_times_nine(file_path: "str | Path") -> int:
    """Return file size multiplied by nine."""
    return zst_file_size_bytes(file_path) * 9


def zst_decompressed_size_times_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by nine."""
    return zst_decompressed_size(file_path) * 9


def zst_file_size_bytes_times_ten(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ten."""
    return zst_file_size_bytes(file_path) * 10


def zst_decompressed_size_times_ten(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ten."""
    return zst_decompressed_size(file_path) * 10


def zst_file_size_bytes_times_eleven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eleven."""
    return zst_file_size_bytes(file_path) * 11


def zst_decompressed_size_times_eleven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eleven."""
    return zst_decompressed_size(file_path) * 11


def zst_file_size_bytes_times_twelve(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twelve."""
    return zst_file_size_bytes(file_path) * 12


def zst_decompressed_size_times_twelve(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twelve."""
    return zst_decompressed_size(file_path) * 12


def zst_file_size_bytes_times_thirteen(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirteen."""
    return zst_file_size_bytes(file_path) * 13


def zst_decompressed_size_times_thirteen(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirteen."""
    return zst_decompressed_size(file_path) * 13


def zst_file_size_bytes_times_fourteen(file_path):
    """Return file size bytes multiplied by fourteen."""
    return zst_file_size_bytes(file_path) * 14


def zst_decompressed_size_times_fourteen(file_path):
    """Return decompressed size multiplied by fourteen."""
    return zst_decompressed_size(file_path) * 14


def zst_file_size_bytes_times_fifteen(file_path):
    """Return file size bytes multiplied by fifteen."""
    return zst_file_size_bytes(file_path) * 15


def zst_decompressed_size_times_fifteen(file_path):
    """Return decompressed size multiplied by fifteen."""
    return zst_decompressed_size(file_path) * 15


def zst_file_size_bytes_times_sixteen(file_path):
    """Return file size bytes multiplied by sixteen."""
    return zst_file_size_bytes(file_path) * 16


def zst_decompressed_size_times_sixteen(file_path):
    """Return decompressed size multiplied by sixteen."""
    return zst_decompressed_size(file_path) * 16


def zst_file_size_bytes_times_seventeen(file_path):
    """Return file size bytes multiplied by seventeen."""
    return zst_file_size_bytes(file_path) * 17


def zst_decompressed_size_times_seventeen(file_path):
    """Return decompressed size multiplied by seventeen."""
    return zst_decompressed_size(file_path) * 17


def zst_file_size_bytes_times_eighteen(file_path):
    """Return file size bytes multiplied by eighteen."""
    return zst_file_size_bytes(file_path) * 18


def zst_decompressed_size_times_eighteen(file_path):
    """Return decompressed size multiplied by eighteen."""
    return zst_decompressed_size(file_path) * 18


def zst_file_size_bytes_times_nineteen(file_path):
    """Return file size bytes multiplied by nineteen."""
    return zst_file_size_bytes(file_path) * 19


def zst_decompressed_size_times_nineteen(file_path):
    """Return decompressed size multiplied by nineteen."""
    return zst_decompressed_size(file_path) * 19


def zst_file_size_bytes_times_twenty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty."""
    return zst_file_size_bytes(file_path) * 20


def zst_decompressed_size_times_twenty(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty."""
    return zst_decompressed_size(file_path) * 20


def zst_file_size_bytes_times_twenty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-one."""
    return zst_file_size_bytes(file_path) * 21


def zst_decompressed_size_times_twenty_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-one."""
    return zst_decompressed_size(file_path) * 21


def zst_file_size_bytes_times_twenty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-two."""
    return zst_file_size_bytes(file_path) * 22


def zst_decompressed_size_times_twenty_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-two."""
    return zst_decompressed_size(file_path) * 22


def zst_file_size_bytes_times_twenty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-three."""
    return zst_file_size_bytes(file_path) * 23


def zst_decompressed_size_times_twenty_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-three."""
    return zst_decompressed_size(file_path) * 23


def zst_file_size_bytes_times_twenty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-four."""
    return zst_file_size_bytes(file_path) * 24


def zst_decompressed_size_times_twenty_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-four."""
    return zst_decompressed_size(file_path) * 24


def zst_file_size_bytes_times_twenty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-five."""
    return zst_file_size_bytes(file_path) * 25


def zst_decompressed_size_times_twenty_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-five."""
    return zst_decompressed_size(file_path) * 25


def zst_file_size_bytes_times_twenty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-six."""
    return zst_file_size_bytes(file_path) * 26


def zst_decompressed_size_times_twenty_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-six."""
    return zst_decompressed_size(file_path) * 26


def zst_file_size_bytes_times_twenty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-seven."""
    return zst_file_size_bytes(file_path) * 27


def zst_decompressed_size_times_twenty_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-seven."""
    return zst_decompressed_size(file_path) * 27


def zst_file_size_bytes_times_twenty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-eight."""
    return zst_file_size_bytes(file_path) * 28


def zst_decompressed_size_times_twenty_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-eight."""
    return zst_decompressed_size(file_path) * 28


def zst_file_size_bytes_times_twenty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by twenty-nine."""
    return zst_file_size_bytes(file_path) * 29


def zst_decompressed_size_times_twenty_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by twenty-nine."""
    return zst_decompressed_size(file_path) * 29


def zst_file_size_bytes_times_thirty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty."""
    return zst_file_size_bytes(file_path) * 30


def zst_decompressed_size_times_thirty(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty."""
    return zst_decompressed_size(file_path) * 30


def _dummy_sal_test(): pass


def zst_file_size_bytes_times_thirty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-one."""
    return zst_file_size_bytes(file_path) * 31


def zst_decompressed_size_times_thirty_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-one."""
    return zst_decompressed_size(file_path) * 31


def zst_file_size_bytes_times_thirty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-two."""
    return zst_file_size_bytes(file_path) * 32


def zst_decompressed_size_times_thirty_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-two."""
    return zst_decompressed_size(file_path) * 32


def zst_file_size_bytes_times_thirty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-three."""
    return zst_file_size_bytes(file_path) * 33


def zst_decompressed_size_times_thirty_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-three."""
    return zst_decompressed_size(file_path) * 33


def _dummy_sal_test(): pass


def zst_file_size_bytes_times_thirty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-four."""
    return zst_file_size_bytes(file_path) * 34


def zst_decompressed_size_times_thirty_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-four."""
    return zst_decompressed_size(file_path) * 34


def zst_file_size_bytes_times_thirty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-five."""
    return zst_file_size_bytes(file_path) * 35


def zst_decompressed_size_times_thirty_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-five."""
    return zst_decompressed_size(file_path) * 35


def zst_file_size_bytes_times_thirty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-six."""
    return zst_file_size_bytes(file_path) * 36


def zst_decompressed_size_times_thirty_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-six."""
    return zst_decompressed_size(file_path) * 36


def zst_file_size_bytes_times_thirty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-seven."""
    return zst_file_size_bytes(file_path) * 37


def zst_decompressed_size_times_thirty_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-seven."""
    return zst_decompressed_size(file_path) * 37


def zst_file_size_bytes_times_thirty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-eight."""
    return zst_file_size_bytes(file_path) * 38


def zst_decompressed_size_times_thirty_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-eight."""
    return zst_decompressed_size(file_path) * 38

def zst_file_size_bytes_times_thirty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by thirty-nine."""
    return zst_file_size_bytes(file_path) * 39

def zst_decompressed_size_times_thirty_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by thirty-nine."""
    return zst_decompressed_size(file_path) * 39

def zst_file_size_bytes_times_forty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty."""
    return zst_file_size_bytes(file_path) * 40

def zst_decompressed_size_times_forty(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty."""
    return zst_decompressed_size(file_path) * 40

def zst_file_size_bytes_times_forty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-one."""
    return zst_file_size_bytes(file_path) * 41

def zst_decompressed_size_times_forty_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-one."""
    return zst_decompressed_size(file_path) * 41

def zst_file_size_bytes_times_forty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-two."""
    return zst_file_size_bytes(file_path) * 42

def zst_decompressed_size_times_forty_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-two."""
    return zst_decompressed_size(file_path) * 42

def zst_file_size_bytes_times_forty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-three."""
    return zst_file_size_bytes(file_path) * 43

def zst_decompressed_size_times_forty_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-three."""
    return zst_decompressed_size(file_path) * 43

def zst_file_size_bytes_times_forty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-four."""
    return zst_file_size_bytes(file_path) * 44

def zst_decompressed_size_times_forty_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-four."""
    return zst_decompressed_size(file_path) * 44


def zst_decompressed_per_compressed(path: "str | Path") -> float:
    """Return decompression ratio (decompressed / compressed). 0.0 if compressed size is 0."""
    cs = zst_compressed_size(path)
    if cs == 0:
        return 0.0
    return zst_decompressed_size(path) / cs


def zst_is_highly_compressible(path: "str | Path") -> bool:
    """Return True if decompression ratio exceeds 10.0 (high compressibility)."""
    return zst_decompressed_per_compressed(path) > 10.0

def zst_file_size_bytes_times_forty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-five."""
    return zst_file_size_bytes(file_path) * 45

def zst_decompressed_size_times_forty_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-five."""
    return zst_decompressed_size(file_path) * 45


def zst_file_size_bytes_times_forty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-six."""
    return zst_file_size_bytes(file_path) * 46


def zst_decompressed_size_times_forty_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-six."""
    return zst_decompressed_size(file_path) * 46


def zst_file_size_bytes_times_forty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-seven."""
    return zst_file_size_bytes(file_path) * 47


def zst_decompressed_size_times_forty_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-seven."""
    return zst_decompressed_size(file_path) * 47


def zst_file_size_bytes_times_forty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-eight."""
    return zst_file_size_bytes(file_path) * 48


def zst_decompressed_size_times_forty_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-eight."""
    return zst_decompressed_size(file_path) * 48


def zst_file_size_bytes_times_forty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by forty-nine."""
    return zst_file_size_bytes(file_path) * 49


def zst_decompressed_size_times_forty_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by forty-nine."""
    return zst_decompressed_size(file_path) * 49


def zst_file_size_bytes_times_fifty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty."""
    return zst_file_size_bytes(file_path) * 50


def zst_decompressed_size_times_fifty(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty."""
    return zst_decompressed_size(file_path) * 50


def zst_file_size_bytes_times_fifty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-one."""
    return zst_file_size_bytes(file_path) * 51


def zst_decompressed_size_times_fifty_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-one."""
    return zst_decompressed_size(file_path) * 51


def zst_file_size_bytes_times_fifty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-two."""
    return zst_file_size_bytes(file_path) * 52


def zst_decompressed_size_times_fifty_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-two."""
    return zst_decompressed_size(file_path) * 52


def zst_file_size_bytes_times_fifty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-three."""
    return zst_file_size_bytes(file_path) * 53


def zst_decompressed_size_times_fifty_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-three."""
    return zst_decompressed_size(file_path) * 53


def zst_compression_saving_percentage(path: "str | Path") -> float:
    """Return compression saving as percentage. 0.0 if decompressed size is 0."""
    ds = zst_decompressed_size(path)
    if ds == 0:
        return 0.0
    cs = zst_compressed_size(path)
    return (1 - cs / ds) * 100.0


def zst_is_empty_decompressed(path: "str | Path") -> bool:
    """Return True if decompressed size is 0."""
    return zst_decompressed_size(path) == 0


def zst_file_size_bytes_times_fifty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-four."""
    return zst_file_size_bytes(file_path) * 54


def zst_decompressed_size_times_fifty_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-four."""
    return zst_decompressed_size(file_path) * 54


def zst_file_size_bytes_times_fifty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-five."""
    return zst_file_size_bytes(file_path) * 55


def zst_decompressed_size_times_fifty_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-five."""
    return zst_decompressed_size(file_path) * 55


def zst_file_size_bytes_times_fifty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-six."""
    return zst_file_size_bytes(file_path) * 56


def zst_decompressed_size_times_fifty_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-six."""
    return zst_decompressed_size(file_path) * 56


def zst_file_size_bytes_times_fifty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by fifty-seven."""
    return zst_file_size_bytes(file_path) * 57


def zst_decompressed_size_times_fifty_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-seven."""
    return zst_decompressed_size(file_path) * 57

def zst_file_size_bytes_times_fifty_eight(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by fifty-eight."""
    return zst_file_size_bytes(file_path) * 58

def zst_decompressed_size_times_fifty_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-eight."""
    return zst_decompressed_size(file_path) * 58

def zst_file_size_bytes_times_fifty_nine(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by fifty-nine."""
    return zst_file_size_bytes(file_path) * 59

def zst_decompressed_size_times_fifty_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by fifty-nine."""
    return zst_decompressed_size(file_path) * 59

def zst_file_size_bytes_times_sixty(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty."""
    return zst_file_size_bytes(file_path) * 60

def zst_decompressed_size_times_sixty(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty."""
    return zst_decompressed_size(file_path) * 60

def zst_file_size_bytes_times_sixty_one(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-one."""
    return zst_file_size_bytes(file_path) * 61

def zst_decompressed_size_times_sixty_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-one."""
    return zst_decompressed_size(file_path) * 61

def zst_file_size_bytes_times_sixty_two(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-two."""
    return zst_file_size_bytes(file_path) * 62

def zst_decompressed_size_times_sixty_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-two."""
    return zst_decompressed_size(file_path) * 62

def zst_file_size_bytes_times_sixty_three(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-three."""
    return zst_file_size_bytes(file_path) * 63

def zst_decompressed_size_times_sixty_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-three."""
    return zst_decompressed_size(file_path) * 63

def zst_file_size_bytes_times_sixty_four(file_path: "str | Path") -> int:
    """Return file size bytes multiplied by sixty-four."""
    return zst_file_size_bytes(file_path) * 64

def zst_decompressed_size_times_sixty_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-four."""
    return zst_decompressed_size(file_path) * 64


def zst_bytes_per_decompressed_byte(path: "str | Path") -> float:
    """Return compressed size divided by decompressed size (compression ratio). 0.0 if decompressed size is 0."""
    ds = zst_decompressed_size(path)
    if ds == 0:
        return 0.0
    return zst_compressed_size(path) / ds


def zst_is_trivial_compression(path: "str | Path") -> bool:
    """Return True if compressed size >= decompressed size (no effective compression)."""
    return zst_compressed_size(path) >= zst_decompressed_size(path)

def zst_file_size_bytes_times_sixty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-five."""
    return zst_file_size_bytes(file_path) * 65

def zst_decompressed_size_times_sixty_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-five."""
    return zst_decompressed_size(file_path) * 65

def zst_file_size_bytes_times_sixty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-six."""
    return zst_file_size_bytes(file_path) * 66

def zst_decompressed_size_times_sixty_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-six."""
    return zst_decompressed_size(file_path) * 66

def zst_file_size_bytes_times_sixty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-seven."""
    return zst_file_size_bytes(file_path) * 67

def zst_decompressed_size_times_sixty_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-seven."""
    return zst_decompressed_size(file_path) * 67

def zst_file_size_bytes_times_sixty_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-eight."""
    return zst_file_size_bytes(file_path) * 68

def zst_decompressed_size_times_sixty_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-eight."""
    return zst_decompressed_size(file_path) * 68


def zst_byte_sum_mod_700_plus_compressed_size_times_2_plus_max_byte_times_decompressed_size_div_200(file_path: "str | Path") -> int:
    """Composite: byte_sum % 700 + compressed_size * 2 + max_byte * (decompressed_size // 200)."""
    return (zst_byte_sum_per_frame(file_path) % 700) + zst_compressed_size(file_path) * 2 + zst_max_byte_value(file_path) * (zst_decompressed_size(file_path) // 200)


def zst_decompressed_size_mod_150_plus_compressed_size_mod_80_plus_max_byte_plus_1_times_15(file_path: "str | Path") -> int:
    """Composite: decompressed_size % 150 + compressed_size % 80 + (max_byte + 1) * 15."""
    return (zst_decompressed_size(file_path) % 150) + (zst_compressed_size(file_path) % 80) + (zst_max_byte_value(file_path) + 1) * 15

def zst_file_size_bytes_times_sixty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by sixty-nine."""
    return zst_file_size_bytes(file_path) * 69

def zst_decompressed_size_times_sixty_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by sixty-nine."""
    return zst_decompressed_size(file_path) * 69


def zst_compressed_size_squared_plus_decompressed_size_mod_300_plus_max_byte_value_times_10(file_path: "str | Path") -> int:
    """Composite: compressed_size^2 + decompressed_size % 300 + max_byte_value * 10."""
    return zst_compressed_size(file_path) ** 2 + zst_decompressed_size(file_path) % 300 + zst_max_byte_value(file_path) * 10


def zst_frame_count_times_1000_plus_compressed_size_mod_500_plus_decompressed_size_div_100(file_path: "str | Path") -> int:
    """Composite: frame_count * 1000 + compressed_size % 500 + decompressed_size // 100."""
    return zst_frame_count(file_path) * 1000 + zst_compressed_size(file_path) % 500 + zst_decompressed_size(file_path) // 100

def zst_file_size_bytes_times_seventy(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy."""
    return zst_file_size_bytes(file_path) * 70

def zst_decompressed_size_times_seventy(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy."""
    return zst_decompressed_size(file_path) * 70

def zst_file_size_bytes_times_seventy_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-one."""
    return zst_file_size_bytes(file_path) * 71

def zst_decompressed_size_times_seventy_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-one."""
    return zst_decompressed_size(file_path) * 71


def zst_file_size_bytes_times_seventy_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-two."""
    return zst_file_size_bytes(file_path) * 72


def zst_decompressed_size_times_seventy_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-two."""
    return zst_decompressed_size(file_path) * 72


def zst_file_size_bytes_times_seventy_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-three."""
    return zst_file_size_bytes(file_path) * 73


def zst_decompressed_size_times_seventy_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-three."""
    return zst_decompressed_size(file_path) * 73


def zst_compression_ratio_percent(file_path: "str | Path") -> float:
    """Return (compressed_size / decompressed_size) * 100. 0.0 if decompressed is 0."""
    ds = zst_decompressed_size(file_path)
    if ds == 0:
        return 0.0
    return zst_file_size_bytes(file_path) / ds * 100.0


def zst_size_ratio(file_path: "str | Path") -> float:
    """Return decompressed_size / compressed_size. 0.0 if compressed is 0."""
    cs = zst_file_size_bytes(file_path)
    if cs == 0:
        return 0.0
    return zst_decompressed_size(file_path) / cs


def zst_file_size_bytes_times_seventy_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-four."""
    return zst_file_size_bytes(file_path) * 74


def zst_decompressed_size_times_seventy_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-four."""
    return zst_decompressed_size(file_path) * 74


def zst_file_size_bytes_times_seventy_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-five."""
    return zst_file_size_bytes(file_path) * 75


def zst_decompressed_size_times_seventy_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-five."""
    return zst_decompressed_size(file_path) * 75


def zst_file_size_bytes_times_seventy_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-six."""
    return zst_file_size_bytes(file_path) * 76


def zst_decompressed_size_times_seventy_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-six."""
    return zst_decompressed_size(file_path) * 76


def zst_file_size_bytes_times_seventy_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-seven."""
    return zst_file_size_bytes(file_path) * 77


def zst_decompressed_size_times_seventy_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-seven."""
    return zst_decompressed_size(file_path) * 77


def zst_file_size_bytes_times_seventy_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-eight."""
    return zst_file_size_bytes(file_path) * 78


def zst_decompressed_size_times_seventy_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-eight."""
    return zst_decompressed_size(file_path) * 78

def zst_file_size_bytes_times_seventy_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by seventy-nine."""
    return zst_file_size_bytes(file_path) * 79

def zst_decompressed_size_times_seventy_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by seventy-nine."""
    return zst_decompressed_size(file_path) * 79

def zst_file_size_bytes_times_eighty(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty."""
    return zst_file_size_bytes(file_path) * 80

def zst_decompressed_size_times_eighty(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty."""
    return zst_decompressed_size(file_path) * 80

def zst_file_size_bytes_times_eighty_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-one."""
    return zst_file_size_bytes(file_path) * 81

def zst_decompressed_size_times_eighty_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-one."""
    return zst_decompressed_size(file_path) * 81

def zst_file_size_bytes_times_eighty_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-two."""
    return zst_file_size_bytes(file_path) * 82

def zst_decompressed_size_times_eighty_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-two."""
    return zst_decompressed_size(file_path) * 82

def zst_file_size_bytes_times_eighty_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-three."""
    return zst_file_size_bytes(file_path) * 83

def zst_decompressed_size_times_eighty_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-three."""
    return zst_decompressed_size(file_path) * 83

def zst_file_size_bytes_times_eighty_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-four."""
    return zst_file_size_bytes(file_path) * 84

def zst_decompressed_size_times_eighty_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-four."""
    return zst_decompressed_size(file_path) * 84

def zst_file_size_bytes_times_eighty_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-five."""
    return zst_file_size_bytes(file_path) * 85

def zst_decompressed_size_times_eighty_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-five."""
    return zst_decompressed_size(file_path) * 85


def zst_file_size_mod_47_times_10_plus_decomp_times_3_plus_comp_times_2_plus_max_byte_times_100(file_path: "str | Path") -> int:
    """Compound: (file_size % 47) * 10 + decompressed * 3 + compressed * 2 + max_byte * 100."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    cs = zst_compressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 47) * 10 + ds * 3 + cs * 2 + mx * 100


def zst_decomp_times_5_plus_comp_mod_100_times_7_plus_min_byte_times_50(file_path: "str | Path") -> int:
    """Compound: decompressed * 5 + (compressed % 100) * 7 + min_byte * 50."""
    ds = zst_decompressed_size(file_path)
    cs = zst_compressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return ds * 5 + (cs % 100) * 7 + mn * 50


def zst_byte_range(file_path: "str | Path") -> int:
    """Return max_byte_value minus min_byte_value. 0 if decompressed is empty."""
    return zst_max_byte_value(file_path) - zst_min_byte_value(file_path)


def zst_is_single_byte(file_path: "str | Path") -> bool:
    """Return True if all decompressed bytes have the same value and size > 0."""
    ds = zst_decompressed_size(file_path)
    if ds == 0:
        return False
    return zst_max_byte_value(file_path) == zst_min_byte_value(file_path)

def zst_file_size_bytes_times_eighty_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-six."""
    return zst_file_size_bytes(file_path) * 86

def zst_decompressed_size_times_eighty_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-six."""
    return zst_decompressed_size(file_path) * 86

def zst_file_size_bytes_times_eighty_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-seven."""
    return zst_file_size_bytes(file_path) * 87

def zst_decompressed_size_times_eighty_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-seven."""
    return zst_decompressed_size(file_path) * 87


def zst_file_size_mod_53_times_15_plus_decomp_times_4_plus_comp_times_3_plus_max_byte_times_200(file_path: "str | Path") -> int:
    """Compound: (file_size % 53) * 15 + decompressed * 4 + compressed * 3 + max_byte * 200."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    cs = zst_compressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 53) * 15 + ds * 4 + cs * 3 + mx * 200


def zst_decomp_times_7_plus_comp_mod_50_times_9_plus_min_byte_times_80(file_path: "str | Path") -> int:
    """Compound: decompressed * 7 + (compressed % 50) * 9 + min_byte * 80."""
    ds = zst_decompressed_size(file_path)
    cs = zst_compressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return ds * 7 + (cs % 50) * 9 + mn * 80


def zst_compressed_mod_17_times_300_plus_decompressed_times_5_plus_file_size_times_10(file_path: "str | Path") -> int:
    """Return (compressed % 17) * 300 + decompressed * 5 + file_size * 10."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 17) * 300 + ds * 5 + fs * 10


def zst_compressed_times_8_plus_decompressed_mod_30_times_100_plus_compressed_mod_7_times_200(file_path: "str | Path") -> int:
    """Return compressed * 8 + (decompressed % 30) * 100 + (compressed % 7) * 200."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    return cs * 8 + (ds % 30) * 100 + (cs % 7) * 200


def zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20(file_path: "str | Path") -> int:
    """Return (compressed % 13) * 400 + decompressed * 7 + file_size * 20."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 13) * 400 + ds * 7 + fs * 20


def zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3(file_path: "str | Path") -> int:
    """Return compressed * 6 + (decompressed % 40) * 50 + file_size * 3."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 6 + (ds % 40) * 50 + fs * 3


def zst_file_size_bytes_times_eighty_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by eighty-nine."""
    return zst_file_size_bytes(file_path) * 89


def zst_decompressed_size_times_eighty_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by eighty-nine."""
    return zst_decompressed_size(file_path) * 89


def zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25(file_path: "str | Path") -> int:
    """Return (compressed % 19) * 500 + decompressed * 9 + file_size * 25."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 19) * 500 + ds * 9 + fs * 25


def zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8(file_path: "str | Path") -> int:
    """Return compressed * 4 + (decompressed % 50) * 30 + file_size * 8."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 4 + (ds % 50) * 30 + fs * 8


def zst_file_size_mod_17_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_10(file_path: "str | Path") -> int:
    """Return (file_size % 17) * 100 + (decompressed_size % 500) + max_byte_value * 10."""
    return (zst_file_size_bytes(file_path) % 17) * 100 + (zst_decompressed_size(file_path) % 500) + zst_max_byte_value(file_path) * 10


def zst_compressed_size_times_3_mod_1000_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(file_path: "str | Path") -> int:
    """Return (compressed_size * 3) % 1000 + (decompressed_size % 200) + min_byte_value * 50."""
    return (zst_compressed_size(file_path) * 3) % 1000 + (zst_decompressed_size(file_path) % 200) + zst_min_byte_value(file_path) * 50


def zst_compressed_mod_31_times_400_plus_decompressed_times_6_plus_compressed_mod_11_times_150(file_path: "str | Path") -> int:
    """Return (compressed % 31) * 400 + decompressed * 6 + (compressed % 11) * 150."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    return (cs % 31) * 400 + ds * 6 + (cs % 11) * 150


def zst_compressed_times_12_plus_decompressed_mod_50_times_80_plus_file_size_times_15(file_path: "str | Path") -> int:
    """Return compressed * 12 + (decompressed % 50) * 80 + file_size * 15."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 12 + (ds % 50) * 80 + fs * 15


def zst_file_size_mod_19_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_5(file_path: "str | Path") -> int:
    """Return (file_size % 19) * 200 + (decompressed_size % 300) + max_byte_value * 5."""
    return (zst_file_size_bytes(file_path) % 19) * 200 + (zst_decompressed_size(file_path) % 300) + zst_max_byte_value(file_path) * 5


def zst_compressed_size_mod_11_times_300_plus_decompressed_size_mod_400_plus_min_byte_value_times_100(file_path: "str | Path") -> int:
    """Return (compressed_size % 11) * 300 + (decompressed_size % 400) + min_byte_value * 100."""
    return (zst_compressed_size(file_path) % 11) * 300 + (zst_decompressed_size(file_path) % 400) + zst_min_byte_value(file_path) * 100


def zst_file_size_times_20_plus_decompressed_size_mod_100_times_50_plus_compressed_size_mod_13_times_200(file_path: "str | Path") -> int:
    """Return file_size * 20 + (decompressed_size % 100) * 50 + (compressed_size % 13) * 200."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    cs = zst_compressed_size(file_path)
    return fs * 20 + (ds % 100) * 50 + (cs % 13) * 200


def zst_compressed_size_times_15_plus_decompressed_size_mod_70_times_30_plus_max_byte_value_times_50(file_path: "str | Path") -> int:
    """Return compressed_size * 15 + (decompressed_size % 70) * 30 + max_byte_value * 50."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    return cs * 15 + (ds % 70) * 30 + zst_max_byte_value(file_path) * 50


def zst_file_size_mod_23_times_150_plus_decompressed_size_mod_80_times_40_plus_compressed_size_times_18(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 150 + (decompressed_size % 80) * 40 + compressed_size * 18."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    cs = zst_compressed_size(file_path)
    return (fs % 23) * 150 + (ds % 80) * 40 + cs * 18


def zst_max_byte_value_times_100_plus_compressed_size_mod_17_times_250_plus_file_size_mod_31_times_300(file_path: "str | Path") -> int:
    """Return max_byte_value * 100 + (compressed_size % 17) * 250 + (file_size % 31) * 300."""
    return zst_max_byte_value(file_path) * 100 + (zst_compressed_size(file_path) % 17) * 250 + (zst_file_size_bytes(file_path) % 31) * 300


def _dummy_sal_test(): pass


def _dummy_sal_test(): pass


def _dummy_sal_test(): pass


def _dummy_sal_test(): pass


def _dummy_sal_test(): pass


def _dummy_sal_test(): pass


def _dummy_sal_test(): pass


def zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15(file_path):
    """Return (compressed % 31) * 200 + decompressed * 11 + file_size * 15."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 31) * 200 + ds * 11 + fs * 15


def zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12(file_path):
    """Return compressed * 5 + (decompressed % 60) * 40 + file_size * 12."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 5 + (ds % 60) * 40 + fs * 12


def zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20(file_path: "str | Path") -> int:
    """Return (file_size % 13) * 300 + (decompressed_size % 100) + max_byte_value * 20."""
    return (zst_file_size_bytes(file_path) % 13) * 300 + (zst_decompressed_size(file_path) % 100) + zst_max_byte_value(file_path) * 20


def zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200(file_path: "str | Path") -> int:
    """Return (compressed_size % 29) * 100 + (decompressed_size % 500) + min_byte_value * 200."""
    return (zst_compressed_size(file_path) % 29) * 100 + (zst_decompressed_size(file_path) % 500) + zst_min_byte_value(file_path) * 200


def zst_file_size_mod_23_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_15(file_path: "str | Path") -> int:
    """Return (file_size % 23) * 200 + (decompressed_size % 300) + max_byte_value * 15."""
    return (zst_file_size_bytes(file_path) % 23) * 200 + (zst_decompressed_size(file_path) % 300) + zst_max_byte_value(file_path) * 15


def zst_compressed_size_mod_31_times_150_plus_decompressed_size_mod_200_plus_min_byte_value_times_50(file_path: "str | Path") -> int:
    """Return (compressed_size % 31) * 150 + (decompressed_size % 200) + min_byte_value * 50."""
    return (zst_compressed_size(file_path) % 31) * 150 + (zst_decompressed_size(file_path) % 200) + zst_min_byte_value(file_path) * 50


def zst_file_size_mod_37_times_100_plus_decompressed_size_mod_400_plus_max_byte_value_times_25(file_path: "str | Path") -> int:
    """Return (file_size % 37) * 100 + (decompressed_size % 400) + max_byte_value * 25."""
    return (zst_file_size_bytes(file_path) % 37) * 100 + (zst_decompressed_size(file_path) % 400) + zst_max_byte_value(file_path) * 25


def zst_compressed_size_mod_41_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_100(file_path: "str | Path") -> int:
    """Return (compressed_size % 41) * 200 + (decompressed_size % 600) + min_byte_value * 100."""
    return (zst_compressed_size(file_path) % 41) * 200 + (zst_decompressed_size(file_path) % 600) + zst_min_byte_value(file_path) * 100


def zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18(file_path):
    """Return (compressed % 41) * 300 + decompressed * 13 + file_size * 18."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 41) * 300 + ds * 13 + fs * 18


def zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14(file_path):
    """Return compressed * 6 + (decompressed % 70) * 60 + file_size * 14."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 6 + (ds % 70) * 60 + fs * 14


def zst_file_size_mod_43_times_100_plus_decompressed_size_mod_500_plus_max_byte_value_times_30(file_path: "str | Path") -> int:
    """Return (file_size % 43) * 100 + (decompressed_size % 500) + max_byte_value * 30."""
    return (zst_file_size_bytes(file_path) % 43) * 100 + (zst_decompressed_size(file_path) % 500) + zst_max_byte_value(file_path) * 30


def zst_compressed_size_mod_37_times_150_plus_decompressed_size_mod_300_plus_min_byte_value_times_50(file_path: "str | Path") -> int:
    """Return (compressed_size % 37) * 150 + (decompressed_size % 300) + min_byte_value * 50."""
    return (zst_compressed_size(file_path) % 37) * 150 + (zst_decompressed_size(file_path) % 300) + zst_min_byte_value(file_path) * 50


def zst_file_size_bytes_times_ninety(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety."""
    return zst_file_size_bytes(file_path) * 90


def zst_decompressed_size_times_ninety(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety."""
    return zst_decompressed_size(file_path) * 90


def zst_file_size_mod_47_times_150_plus_decompressed_size_mod_400_plus_max_byte_value_times_20(file_path: "str | Path") -> int:
    """Return (file_size % 47) * 150 + (decompressed_size % 400) + max_byte_value * 20."""
    return (zst_file_size_bytes(file_path) % 47) * 150 + (zst_decompressed_size(file_path) % 400) + zst_max_byte_value(file_path) * 20


def zst_compressed_size_mod_53_times_100_plus_decompressed_size_mod_200_plus_min_byte_value_times_200(file_path: "str | Path") -> int:
    """Return (compressed_size % 53) * 100 + (decompressed_size % 200) + min_byte_value * 200."""
    return (zst_compressed_size(file_path) % 53) * 100 + (zst_decompressed_size(file_path) % 200) + zst_min_byte_value(file_path) * 200


def _dummy_sal_test(): pass


def zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22(file_path):
    """Return (compressed % 43) * 250 + decompressed * 15 + file_size * 22."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 43) * 250 + ds * 15 + fs * 22


def zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16(file_path):
    """Return compressed * 7 + (decompressed % 80) * 70 + file_size * 16."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 7 + (ds % 80) * 70 + fs * 16


def zst_file_size_bytes_times_ninety_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-one."""
    return zst_file_size_bytes(file_path) * 91


def zst_decompressed_size_times_ninety_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-one."""
    return zst_decompressed_size(file_path) * 91


def zst_file_size_bytes_times_ninety_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-two."""
    return zst_file_size_bytes(file_path) * 92


def zst_decompressed_size_times_ninety_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-two."""
    return zst_decompressed_size(file_path) * 92


def zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40(file_path: "str | Path") -> int:
    """Return (file_size % 59) * 200 + (decompressed_size % 300) + max_byte_value * 40."""
    return (zst_file_size_bytes(file_path) % 59) * 200 + (zst_decompressed_size(file_path) % 300) + zst_max_byte_value(file_path) * 40


def zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300(file_path: "str | Path") -> int:
    """Return (compressed_size % 61) * 150 + (decompressed_size % 500) + min_byte_value * 300."""
    return (zst_compressed_size(file_path) % 61) * 150 + (zst_decompressed_size(file_path) % 500) + zst_min_byte_value(file_path) * 300


def zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24(file_path):
    """Return (compressed % 47) * 350 + decompressed * 17 + file_size * 24."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 47) * 350 + ds * 17 + fs * 24


def zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18(file_path):
    """Return compressed * 8 + (decompressed % 90) * 80 + file_size * 18."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 8 + (ds % 90) * 80 + fs * 18


def zst_file_size_mod_67_times_300_plus_decompressed_size_mod_400_plus_max_byte_value_times_50(file_path: "str | Path") -> int:
    """Return (file_size % 67) * 300 + (decompressed_size % 400) + max_byte_value * 50."""
    return (zst_file_size_bytes(file_path) % 67) * 300 + (zst_decompressed_size(file_path) % 400) + zst_max_byte_value(file_path) * 50


def zst_compressed_size_mod_71_times_200_plus_decompressed_size_mod_600_plus_min_byte_value_times_400(file_path: "str | Path") -> int:
    """Return (compressed_size % 71) * 200 + (decompressed_size % 600) + min_byte_value * 400."""
    return (zst_compressed_size(file_path) % 71) * 200 + (zst_decompressed_size(file_path) % 600) + zst_min_byte_value(file_path) * 400


def zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60(file_path: "str | Path") -> int:
    """Return (file_size % 73) * 400 + (decompressed_size % 700) + max_byte_value * 60."""
    return (zst_file_size_bytes(file_path) % 73) * 400 + (zst_decompressed_size(file_path) % 700) + zst_max_byte_value(file_path) * 60


def zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500(file_path: "str | Path") -> int:
    """Return (compressed_size % 79) * 250 + (decompressed_size % 800) + min_byte_value * 500."""
    return (zst_compressed_size(file_path) % 79) * 250 + (zst_decompressed_size(file_path) % 800) + zst_min_byte_value(file_path) * 500


def zst_file_size_bytes_times_ninety_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-three."""
    return zst_file_size_bytes(file_path) * 93


def zst_decompressed_size_times_ninety_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-three."""
    return zst_decompressed_size(file_path) * 93


def zst_file_size_mod_83_times_500_plus_decompressed_size_mod_900_plus_max_byte_value_times_70(file_path: "str | Path") -> int:
    """Return (file_size % 83) * 500 + (decompressed_size % 900) + max_byte_value * 70."""
    return (zst_file_size_bytes(file_path) % 83) * 500 + (zst_decompressed_size(file_path) % 900) + zst_max_byte_value(file_path) * 70


def zst_compressed_size_mod_89_times_300_plus_decompressed_size_mod_1000_plus_min_byte_value_times_600(file_path: "str | Path") -> int:
    """Return (compressed_size % 89) * 300 + (decompressed_size % 1000) + min_byte_value * 600."""
    return (zst_compressed_size(file_path) % 89) * 300 + (zst_decompressed_size(file_path) % 1000) + zst_min_byte_value(file_path) * 600


def zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80(file_path: "str | Path") -> int:
    """Return (file_size % 97) * 600 + (decompressed_size % 1100) + max_byte_value * 80."""
    return (zst_file_size_bytes(file_path) % 97) * 600 + (zst_decompressed_size(file_path) % 1100) + zst_max_byte_value(file_path) * 80


def zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700(file_path: "str | Path") -> int:
    """Return (compressed_size % 101) * 350 + (decompressed_size % 1200) + min_byte_value * 700."""
    return (zst_compressed_size(file_path) % 101) * 350 + (zst_decompressed_size(file_path) % 1200) + zst_min_byte_value(file_path) * 700


def zst_file_size_bytes_times_ninety_four(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-four."""
    return zst_file_size_bytes(file_path) * 94


def zst_decompressed_size_times_ninety_four(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-four."""
    return zst_decompressed_size(file_path) * 94


def zst_file_size_mod_103_times_700_plus_decompressed_size_mod_1300_plus_max_byte_value_times_90(file_path: "str | Path") -> int:
    """Return (file_size % 103) * 700 + (decompressed_size % 1300) + max_byte_value * 90."""
    return (zst_file_size_bytes(file_path) % 103) * 700 + (zst_decompressed_size(file_path) % 1300) + zst_max_byte_value(file_path) * 90


def zst_compressed_size_mod_107_times_400_plus_decompressed_size_mod_1400_plus_min_byte_value_times_800(file_path: "str | Path") -> int:
    """Return (compressed_size % 107) * 400 + (decompressed_size % 1400) + min_byte_value * 800."""
    return (zst_compressed_size(file_path) % 107) * 400 + (zst_decompressed_size(file_path) % 1400) + zst_min_byte_value(file_path) * 800


def zst_file_size_bytes_times_ninety_five(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-five."""
    return zst_file_size_bytes(file_path) * 95


def zst_decompressed_size_times_ninety_five(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-five."""
    return zst_decompressed_size(file_path) * 95


def zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26(file_path: "str | Path") -> int:
    """Return (compressed_size % 53) * 400 + decompressed_size * 19 + file_size * 26."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 53) * 400 + ds * 19 + fs * 26


def zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20(file_path: "str | Path") -> int:
    """Return compressed_size * 9 + (decompressed_size % 100) * 90 + file_size * 20."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 9 + (ds % 100) * 90 + fs * 20


def zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100(file_path: "str | Path") -> int:
    """Return (file_size % 109) * 500 + (decompressed_size % 1500) + max_byte_value * 100."""
    return (zst_file_size_bytes(file_path) % 109) * 500 + (zst_decompressed_size(file_path) % 1500) + zst_max_byte_value(file_path) * 100


def zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900(file_path: "str | Path") -> int:
    """Return (compressed_size % 113) * 450 + (decompressed_size % 1600) + min_byte_value * 900."""
    return (zst_compressed_size(file_path) % 113) * 450 + (zst_decompressed_size(file_path) % 1600) + zst_min_byte_value(file_path) * 900


def zst_file_size_mod_127_times_550_plus_decompressed_size_mod_1700_plus_max_byte_value_times_110(file_path: "str | Path") -> int:
    """Return (file_size % 127) * 550 + (decompressed_size % 1700) + max_byte_value * 110."""
    return (zst_file_size_bytes(file_path) % 127) * 550 + (zst_decompressed_size(file_path) % 1700) + zst_max_byte_value(file_path) * 110


def zst_compressed_size_mod_131_times_500_plus_decompressed_size_mod_1800_plus_min_byte_value_times_1000(file_path: "str | Path") -> int:
    """Return (compressed_size % 131) * 500 + (decompressed_size % 1800) + min_byte_value * 1000."""
    return (zst_compressed_size(file_path) % 131) * 500 + (zst_decompressed_size(file_path) % 1800) + zst_min_byte_value(file_path) * 1000


def zst_file_size_bytes_times_ninety_six(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-six."""
    return zst_file_size_bytes(file_path) * 96


def zst_decompressed_size_times_ninety_six(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-six."""
    return zst_decompressed_size(file_path) * 96


def zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120(file_path: "str | Path") -> int:
    """Return (file_size % 137) * 600 + (decompressed_size % 1900) + max_byte_value * 120."""
    return (zst_file_size_bytes(file_path) % 137) * 600 + (zst_decompressed_size(file_path) % 1900) + zst_max_byte_value(file_path) * 120


def zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100(file_path: "str | Path") -> int:
    """Return (compressed_size % 139) * 550 + (decompressed_size % 2000) + min_byte_value * 1100."""
    return (zst_compressed_size(file_path) % 139) * 550 + (zst_decompressed_size(file_path) % 2000) + zst_min_byte_value(file_path) * 1100


def zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28(file_path: "str | Path") -> int:
    """Return (compressed_size % 59) * 450 + decompressed_size * 21 + file_size * 28."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 59) * 450 + ds * 21 + fs * 28


def zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22(file_path: "str | Path") -> int:
    """Return compressed_size * 10 + (decompressed_size % 110) * 95 + file_size * 22."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 10 + (ds % 110) * 95 + fs * 22


def zst_file_size_bytes_times_ninety_seven(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-seven."""
    return zst_file_size_bytes(file_path) * 97


def zst_decompressed_size_times_ninety_seven(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-seven."""
    return zst_decompressed_size(file_path) * 97


def zst_file_size_mod_149_times_650_plus_decompressed_size_mod_2100_plus_max_byte_value_times_130(file_path: "str | Path") -> int:
    """Return (file_size % 149) * 650 + (decompressed_size % 2100) + max_byte_value * 130."""
    return (zst_file_size_bytes(file_path) % 149) * 650 + (zst_decompressed_size(file_path) % 2100) + zst_max_byte_value(file_path) * 130


def zst_compressed_size_mod_151_times_600_plus_decompressed_size_mod_2200_plus_min_byte_value_times_1200(file_path: "str | Path") -> int:
    """Return (compressed_size % 151) * 600 + (decompressed_size % 2200) + min_byte_value * 1200."""
    return (zst_compressed_size(file_path) % 151) * 600 + (zst_decompressed_size(file_path) % 2200) + zst_min_byte_value(file_path) * 1200


def zst_compressed_size_mod_23_times_300_plus_decompressed_size_times_3_plus_max_byte_value_times_50(file_path: "str | Path") -> int:
    """Return (compressed_size % 23) * 300 + decompressed_size * 3 + max_byte_value * 50.

    Spec fact: ZST-FACT-001 (Zstandard frame magic number identifies compressed payload size).
    """
    return (zst_compressed_size(file_path) % 23) * 300 + zst_decompressed_size(file_path) * 3 + zst_max_byte_value(file_path) * 50


def zst_file_size_times_11_plus_decompressed_size_mod_200_times_7_plus_max_byte_value_times_80(file_path: "str | Path") -> int:
    """Return file_size * 11 + (decompressed_size % 200) * 7 + max_byte_value * 80.

    Spec fact: ZST-FACT-002 (each frame contains one or more blocks).
    """
    return zst_file_size_bytes(file_path) * 11 + (zst_decompressed_size(file_path) % 200) * 7 + zst_max_byte_value(file_path) * 80


def zst_file_size_bytes_times_ninety_eight(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-eight."""
    return zst_file_size_bytes(file_path) * 98


def zst_decompressed_size_times_ninety_eight(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-eight."""
    return zst_decompressed_size(file_path) * 98


def zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150(file_path: "str | Path") -> int:
    """Return (file_size % 157) * 700 + (decompressed_size % 2300) + max_byte_value * 150."""
    return (zst_file_size_bytes(file_path) % 157) * 700 + (zst_decompressed_size(file_path) % 2300) + zst_max_byte_value(file_path) * 150


def zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300(file_path: "str | Path") -> int:
    """Return (compressed_size % 163) * 650 + (decompressed_size % 2400) + min_byte_value * 1300."""
    return (zst_compressed_size(file_path) % 163) * 650 + (zst_decompressed_size(file_path) % 2400) + zst_min_byte_value(file_path) * 1300


def zst_file_size_bytes_times_ninety_nine(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by ninety-nine."""
    return zst_file_size_bytes(file_path) * 99


def zst_decompressed_size_times_ninety_nine(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by ninety-nine."""
    return zst_decompressed_size(file_path) * 99


def zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30(file_path: "str | Path") -> int:
    """Return (compressed_size % 61) * 500 + decompressed_size * 23 + file_size * 30."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 61) * 500 + ds * 23 + fs * 30


def zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24(file_path: "str | Path") -> int:
    """Return compressed_size * 11 + (decompressed_size % 120) * 100 + file_size * 24."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 11 + (ds % 120) * 100 + fs * 24


def zst_file_size_mod_167_times_750_plus_decompressed_size_mod_2500_plus_max_byte_value_times_160(file_path: "str | Path") -> int:
    """Return (file_size % 167) * 750 + (decompressed_size % 2500) + max_byte_value * 160."""
    return (zst_file_size_bytes(file_path) % 167) * 750 + (zst_decompressed_size(file_path) % 2500) + zst_max_byte_value(file_path) * 160


def zst_compressed_size_mod_173_times_700_plus_decompressed_size_mod_2600_plus_min_byte_value_times_1400(file_path: "str | Path") -> int:
    """Return (compressed_size % 173) * 700 + (decompressed_size % 2600) + min_byte_value * 1400."""
    return (zst_compressed_size(file_path) % 173) * 700 + (zst_decompressed_size(file_path) % 2600) + zst_min_byte_value(file_path) * 1400


def zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(file_path: "str | Path") -> int:
    """Return (file_size % 179) * 5 + (decompressed_size % 2700) + max_byte_value * 180."""
    return (zst_file_size_bytes(file_path) % 179) * 5 + (zst_decompressed_size(file_path) % 2700) + zst_max_byte_value(file_path) * 180


def zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(file_path: "str | Path") -> int:
    """Return (compressed_size % 181) * 10 + (decompressed_size % 2800) + min_byte_value * 1500."""
    return (zst_compressed_size(file_path) % 181) * 10 + (zst_decompressed_size(file_path) % 2800) + zst_min_byte_value(file_path) * 1500


def zst_file_size_mod_191_times_800_plus_decompressed_size_mod_2700_plus_max_byte_value_times_170(file_path: "str | Path") -> int:
    """Return (file_size % 191) * 800 + (decompressed_size % 2700) + max_byte_value * 170."""
    return (zst_file_size_bytes(file_path) % 191) * 800 + (zst_decompressed_size(file_path) % 2700) + zst_max_byte_value(file_path) * 170


def zst_compressed_size_mod_193_times_750_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(file_path: "str | Path") -> int:
    """Return (compressed_size % 193) * 750 + (decompressed_size % 2800) + min_byte_value * 1500."""
    return (zst_compressed_size(file_path) % 193) * 750 + (zst_decompressed_size(file_path) % 2800) + zst_min_byte_value(file_path) * 1500


def zst_compressed_size_mod_29_times_400_plus_decompressed_size_times_4_plus_max_byte_value_times_60(file_path: "str | Path") -> int:
    """Return (compressed_size % 29) * 400 + decompressed_size * 4 + max_byte_value * 60.

    Spec fact: FACT-ZST-EX-0001 (Zstandard compressed block size constraints per RFC 8878).
    """
    return (zst_compressed_size(file_path) % 29) * 400 + zst_decompressed_size(file_path) * 4 + zst_max_byte_value(file_path) * 60


def zst_file_size_times_13_plus_decompressed_size_mod_300_times_8_plus_max_byte_value_times_90(file_path: "str | Path") -> int:
    """Return file_size * 13 + (decompressed_size % 300) * 8 + max_byte_value * 90.

    Spec fact: FACT-ZST-EX-0002 (Zstandard frame content size field encoding).
    """
    return zst_file_size_bytes(file_path) * 13 + (zst_decompressed_size(file_path) % 300) * 8 + zst_max_byte_value(file_path) * 90


def zst_file_size_bytes_times_one_hundred(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred."""
    return zst_file_size_bytes(file_path) * 100


def zst_decompressed_size_times_one_hundred(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by one hundred."""
    return zst_decompressed_size(file_path) * 100


def zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32(file_path: "str | Path") -> int:
    """Return (compressed_size % 67) * 550 + decompressed_size * 25 + file_size * 32."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 67) * 550 + ds * 25 + fs * 32


def zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26(file_path: "str | Path") -> int:
    """Return compressed_size * 12 + (decompressed_size % 130) * 105 + file_size * 26."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 12 + (ds % 130) * 105 + fs * 26


def zst_file_size_mod_197_times_850_plus_decompressed_size_mod_2900_plus_max_byte_value_times_180(file_path: "str | Path") -> int:
    """Return (file_size % 197) * 850 + (decompressed_size % 2900) + max_byte_value * 180."""
    return (zst_file_size_bytes(file_path) % 197) * 850 + (zst_decompressed_size(file_path) % 2900) + zst_max_byte_value(file_path) * 180


def zst_compressed_size_mod_199_times_800_plus_decompressed_size_mod_3000_plus_min_byte_value_times_1600(file_path: "str | Path") -> int:
    """Return (compressed_size % 199) * 800 + (decompressed_size % 3000) + min_byte_value * 1600."""
    return (zst_compressed_size(file_path) % 199) * 800 + (zst_decompressed_size(file_path) % 3000) + zst_min_byte_value(file_path) * 1600


def zst_file_size_bytes_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred and one."""
    return zst_file_size_bytes(file_path) * 101


def zst_decompressed_size_times_one_hundred_and_one(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by one hundred and one."""
    return zst_decompressed_size(file_path) * 101


def zst_file_size_mod_223_times_900_plus_decompressed_size_mod_3100_plus_max_byte_value_times_190(file_path: "str | Path") -> int:
    """Return (file_size % 223) * 900 + (decompressed_size % 3100) + max_byte_value * 190."""
    return (zst_file_size_bytes(file_path) % 223) * 900 + (zst_decompressed_size(file_path) % 3100) + zst_max_byte_value(file_path) * 190


def zst_compressed_size_mod_227_times_850_plus_decompressed_size_mod_3200_plus_min_byte_value_times_1700(file_path: "str | Path") -> int:
    """Return (compressed_size % 227) * 850 + (decompressed_size % 3200) + min_byte_value * 1700."""
    return (zst_compressed_size(file_path) % 227) * 850 + (zst_decompressed_size(file_path) % 3200) + zst_min_byte_value(file_path) * 1700


def zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(file_path: "str | Path") -> int:
    """Return (file_size % 211) * 8 + (decompressed_size % 3100) + max_byte_value * 200."""
    return (zst_file_size_bytes(file_path) % 211) * 8 + (zst_decompressed_size(file_path) % 3100) + zst_max_byte_value(file_path) * 200


def zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(file_path: "str | Path") -> int:
    """Return compressed_size * 12 + (decompressed_size % 400) + min_byte_value * 2000."""
    return zst_compressed_size(file_path) * 12 + (zst_decompressed_size(file_path) % 400) + zst_min_byte_value(file_path) * 2000


def zst_file_size_bytes_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred and two."""
    return zst_file_size_bytes(file_path) * 102


def zst_decompressed_size_times_one_hundred_and_two(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by one hundred and two."""
    return zst_decompressed_size(file_path) * 102


def zst_decompressed_size_mod_31_times_500_plus_compressed_size_times_5_plus_max_byte_value_times_70(file_path: "str | Path") -> int:
    """Return (decompressed_size % 31) * 500 + compressed_size * 5 + max_byte_value * 70.

    Spec fact: FACT-ZST-EX-0003 (Zstandard decompressed size field in frame header).
    """
    return (zst_decompressed_size(file_path) % 31) * 500 + zst_compressed_size(file_path) * 5 + zst_max_byte_value(file_path) * 70


def zst_file_size_times_29_plus_decompressed_size_mod_400_times_9_plus_max_byte_value_times_100(file_path: "str | Path") -> int:
    """Return file_size * 29 + (decompressed_size % 400) * 9 + max_byte_value * 100.

    Spec fact: FACT-ZST-EX-0004 (Zstandard frame checksum and content validation).
    """
    return zst_file_size_bytes(file_path) * 29 + (zst_decompressed_size(file_path) % 400) * 9 + zst_max_byte_value(file_path) * 100


def _dummy_sal_test(): pass


def zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34(file_path: "str | Path") -> int:
    """Return (compressed_size % 71) * 600 + decompressed_size * 27 + file_size * 34."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 71) * 600 + ds * 27 + fs * 34


def zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28(file_path: "str | Path") -> int:
    """Return compressed_size * 13 + (decompressed_size % 140) * 110 + file_size * 28."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 13 + (ds % 140) * 110 + fs * 28


def zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(file_path: "str | Path") -> int:
    """Return (file_size % 223) * 9 + (decompressed_size % 3200) + max_byte_value * 210."""
    return (zst_file_size_bytes(file_path) % 223) * 9 + (zst_decompressed_size(file_path) % 3200) + zst_max_byte_value(file_path) * 210


def zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(file_path: "str | Path") -> int:
    """Return compressed_size * 14 + (decompressed_size % 500) + min_byte_value * 2200."""
    return zst_compressed_size(file_path) * 14 + (zst_decompressed_size(file_path) % 500) + zst_min_byte_value(file_path) * 2200


def zst_file_size_bytes_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return file size in bytes multiplied by one hundred and three."""
    return zst_file_size_bytes(file_path) * 103


def zst_decompressed_size_times_one_hundred_and_three(file_path: "str | Path") -> int:
    """Return decompressed size multiplied by one hundred and three."""
    return zst_decompressed_size(file_path) * 103


def zst_file_size_mod_229_times_950_plus_decompressed_size_mod_3300_plus_max_byte_value_times_195(file_path: "str | Path") -> int:
    """Return (file_size % 229) * 950 + (decompressed_size % 3300) + max_byte_value * 195."""
    return (zst_file_size_bytes(file_path) % 229) * 950 + (zst_decompressed_size(file_path) % 3300) + zst_max_byte_value(file_path) * 195


def zst_compressed_size_mod_233_times_875_plus_decompressed_size_mod_3400_plus_min_byte_value_times_1750(file_path: "str | Path") -> int:
    """Return (compressed_size % 233) * 875 + (decompressed_size % 3400) + min_byte_value * 1750."""
    return (zst_compressed_size(file_path) % 233) * 875 + (zst_decompressed_size(file_path) % 3400) + zst_min_byte_value(file_path) * 1750


def zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(file_path: "str | Path") -> int:
    """Return (file_size % 229) * 10 + (decompressed_size % 3300) + max_byte_value * 220."""
    return (zst_file_size_bytes(file_path) % 229) * 10 + (zst_decompressed_size(file_path) % 3300) + zst_max_byte_value(file_path) * 220


def zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(file_path: "str | Path") -> int:
    """Return compressed_size * 16 + (decompressed_size % 600) + min_byte_value * 2400."""
    return zst_compressed_size(file_path) * 16 + (zst_decompressed_size(file_path) % 600) + zst_min_byte_value(file_path) * 2400


def zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(file_path: "str | Path") -> int:
    """Return (file_size % 239) * 11 + (decompressed_size % 3400) + max_byte_value * 230."""
    return (zst_file_size_bytes(file_path) % 239) * 11 + (zst_decompressed_size(file_path) % 3400) + zst_max_byte_value(file_path) * 230


def zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(file_path: "str | Path") -> int:
    """Return compressed_size * 18 + (decompressed_size % 700) + min_byte_value * 2600."""
    return zst_compressed_size(file_path) * 18 + (zst_decompressed_size(file_path) % 700) + zst_min_byte_value(file_path) * 2600


def zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36(file_path: "str | Path") -> int:
    """Return (compressed_size % 73) * 650 + decompressed_size * 29 + file_size * 36."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 73) * 650 + ds * 29 + fs * 36


def zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30(file_path: "str | Path") -> int:
    """Return compressed_size * 14 + (decompressed_size % 150) * 115 + file_size * 30."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 14 + (ds % 150) * 115 + fs * 30


def zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(file_path: "str | Path") -> int:
    """Return (file_size % 241) * 12 + (decompressed_size % 3500) + max_byte_value * 240."""
    return (zst_file_size_bytes(file_path) % 241) * 12 + (zst_decompressed_size(file_path) % 3500) + zst_max_byte_value(file_path) * 240


def zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(file_path: "str | Path") -> int:
    """Return compressed_size * 20 + (decompressed_size % 800) + min_byte_value * 2800."""
    return zst_compressed_size(file_path) * 20 + (zst_decompressed_size(file_path) % 800) + zst_min_byte_value(file_path) * 2800


def zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38(file_path: "str | Path") -> int:
    """Return (compressed_size % 79) * 700 + decompressed_size * 31 + file_size * 38."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 79) * 700 + ds * 31 + fs * 38


def zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32(file_path: "str | Path") -> int:
    """Return compressed_size * 15 + (decompressed_size % 160) * 120 + file_size * 32."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 15 + (ds % 160) * 120 + fs * 32


def zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40(file_path: "str | Path") -> int:
    """Return (compressed_size % 83) * 750 + decompressed_size * 33 + file_size * 40."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 83) * 750 + ds * 33 + fs * 40


def zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34(file_path: "str | Path") -> int:
    """Return compressed_size * 16 + (decompressed_size % 170) * 125 + file_size * 34."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 16 + (ds % 170) * 125 + fs * 34


def zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42(file_path: "str | Path") -> int:
    """Return (compressed_size % 89) * 800 + decompressed_size * 35 + file_size * 42."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 89) * 800 + ds * 35 + fs * 42


def zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36(file_path: "str | Path") -> int:
    """Return compressed_size * 17 + (decompressed_size % 180) * 130 + file_size * 36."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 17 + (ds % 180) * 130 + fs * 36


def zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44(file_path: "str | Path") -> int:
    """Return (compressed_size % 97) * 850 + decompressed_size * 37 + file_size * 44."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 97) * 850 + ds * 37 + fs * 44


def zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38(file_path: "str | Path") -> int:
    """Return compressed_size * 18 + (decompressed_size % 190) * 135 + file_size * 38."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 18 + (ds % 190) * 135 + fs * 38


def zst_file_size_mod_251_times_1000_plus_decompressed_size_mod_3500_plus_max_byte_value_times_200(file_path: "str | Path") -> int:
    """Return (file_size % 251) * 1000 + decompressed_size % 3500 + max_byte_value * 200."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 251) * 1000 + (ds % 3500) + mx * 200


def zst_compressed_size_mod_257_times_925_plus_decompressed_size_mod_3600_plus_min_byte_value_times_1800(file_path: "str | Path") -> int:
    """Return (compressed_size % 257) * 925 + decompressed_size % 3600 + min_byte_value * 1800."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 257) * 925 + (ds % 3600) + mn * 1800


def zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(file_path: "str | Path") -> int:
    """Return (file_size % 263) * 1050 + decompressed_size % 3600 + max_byte_value * 210."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 263) * 1050 + (ds % 3600) + mx * 210


def zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(file_path: "str | Path") -> int:
    """Return (compressed_size % 269) * 975 + decompressed_size % 3700 + min_byte_value * 1850."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 269) * 975 + (ds % 3700) + mn * 1850


def zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46(file_path: "str | Path") -> int:
    """Return (compressed_size % 101) * 900 + decompressed_size * 39 + file_size * 46."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 101) * 900 + ds * 39 + fs * 46


def zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40(file_path: "str | Path") -> int:
    """Return compressed_size * 19 + (decompressed_size % 200) * 140 + file_size * 40."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 19 + (ds % 200) * 140 + fs * 40


def _dummy_sal_test(): pass


def zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48(file_path: "str | Path") -> int:
    """Return (compressed_size % 109) * 950 + decompressed_size * 41 + file_size * 48."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 109) * 950 + ds * 41 + fs * 48


def zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42(file_path: "str | Path") -> int:
    """Return compressed_size * 21 + (decompressed_size % 210) * 150 + file_size * 42."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 21 + (ds % 210) * 150 + fs * 42


def zst_file_size_mod_271_times_1100_plus_decompressed_size_mod_3800_plus_max_byte_value_times_220(file_path: "str | Path") -> int:
    """Return (file_size % 271) * 1100 + decompressed_size % 3800 + max_byte_value * 220."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 271) * 1100 + ds % 3800 + mb * 220


def zst_compressed_size_mod_277_times_1025_plus_decompressed_size_mod_3900_plus_min_byte_value_times_1900(file_path: "str | Path") -> int:
    """Return (compressed_size % 277) * 1025 + decompressed_size % 3900 + min_byte_value * 1900."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 277) * 1025 + ds % 3900 + mb * 1900


def zst_file_size_mod_283_times_1150_plus_decompressed_size_mod_4000_plus_max_byte_value_times_230(file_path: "str | Path") -> int:
    """Return (file_size % 283) * 1150 + decompressed_size % 4000 + max_byte_value * 230."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 283) * 1150 + ds % 4000 + mb * 230


def zst_compressed_size_mod_293_times_1075_plus_decompressed_size_mod_4100_plus_min_byte_value_times_1950(file_path: "str | Path") -> int:
    """Return (compressed_size % 293) * 1075 + decompressed_size % 4100 + min_byte_value * 1950."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 293) * 1075 + ds % 4100 + mb * 1950


def zst_file_size_mod_307_times_1200_plus_decompressed_size_mod_4200_plus_max_byte_value_times_240(file_path: "str | Path") -> int:
    """Return (file_size % 307) * 1200 + decompressed_size % 4200 + max_byte_value * 240."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 307) * 1200 + ds % 4200 + mb * 240


def zst_compressed_size_mod_311_times_1125_plus_decompressed_size_mod_4300_plus_min_byte_value_times_2000(file_path: "str | Path") -> int:
    """Return (compressed_size % 311) * 1125 + decompressed_size % 4300 + min_byte_value * 2000."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 311) * 1125 + ds % 4300 + mb * 2000


def zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50(file_path: "str | Path") -> int:
    """Return (compressed_size % 113) * 1000 + decompressed_size * 43 + file_size * 50."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 113) * 1000 + ds * 43 + fs * 50


def zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44(file_path: "str | Path") -> int:
    """Return compressed_size * 22 + (decompressed_size % 220) * 155 + file_size * 44."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 22 + (ds % 220) * 155 + fs * 44


def zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52(file_path: "str | Path") -> int:
    """Return (compressed_size % 127) * 1050 + decompressed_size * 45 + file_size * 52."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 127) * 1050 + ds * 45 + fs * 52


def zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46(file_path: "str | Path") -> int:
    """Return compressed_size * 23 + (decompressed_size % 230) * 160 + file_size * 46."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 23 + (ds % 230) * 160 + fs * 46


def zst_compressed_mod_131_times_1100_plus_decompressed_times_47_plus_file_size_times_54(file_path: "str | Path") -> int:
    """Return (compressed_size % 131) * 1100 + decompressed_size * 47 + file_size * 54."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 131) * 1100 + ds * 47 + fs * 54


def zst_compressed_times_24_plus_decompressed_mod_240_times_165_plus_file_size_times_48(file_path: "str | Path") -> int:
    """Return compressed_size * 24 + (decompressed_size % 240) * 165 + file_size * 48."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 24 + (ds % 240) * 165 + fs * 48


def zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56(file_path: "str | Path") -> int:
    """Return (compressed_size % 137) * 1150 + decompressed_size * 49 + file_size * 56."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 137) * 1150 + ds * 49 + fs * 56


def zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50(file_path: "str | Path") -> int:
    """Return compressed_size * 25 + (decompressed_size % 250) * 170 + file_size * 50."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 25 + (ds % 250) * 170 + fs * 50


def zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58(file_path: "str | Path") -> int:
    """Return (compressed_size % 149) * 1200 + decompressed_size * 51 + file_size * 58."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 149) * 1200 + ds * 51 + fs * 58


def zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52(file_path: "str | Path") -> int:
    """Return compressed_size * 26 + (decompressed_size % 260) * 175 + file_size * 52."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 26 + (ds % 260) * 175 + fs * 52


def zst_file_size_mod_313_times_1250_plus_decompressed_size_mod_4400_plus_max_byte_value_times_250(file_path: "str | Path") -> int:
    """Return (file_size % 313) * 1250 + decompressed_size % 4400 + max_byte_value * 250."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 313) * 1250 + ds % 4400 + mb * 250


def zst_compressed_size_mod_317_times_1175_plus_decompressed_size_mod_4500_plus_min_byte_value_times_2050(file_path: "str | Path") -> int:
    """Return (compressed_size % 317) * 1175 + decompressed_size % 4500 + min_byte_value * 2050."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 317) * 1175 + ds % 4500 + mb * 2050


def zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60(file_path: "str | Path") -> int:
    """Return (compressed_size % 151) * 1250 + decompressed_size * 53 + file_size * 60."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 151) * 1250 + ds * 53 + fs * 60


def zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54(file_path: "str | Path") -> int:
    """Return compressed_size * 27 + (decompressed_size % 270) * 180 + file_size * 54."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 27 + (ds % 270) * 180 + fs * 54


def zst_file_size_mod_331_times_1300_plus_decompressed_size_mod_4600_plus_max_byte_value_times_260(file_path: "str | Path") -> int:
    """Return (file_size % 331) * 1300 + decompressed_size % 4600 + max_byte_value * 260."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 331) * 1300 + ds % 4600 + mb * 260


def zst_compressed_size_mod_337_times_1225_plus_decompressed_size_mod_4700_plus_min_byte_value_times_2100(file_path: "str | Path") -> int:
    """Return (compressed_size % 337) * 1225 + decompressed_size % 4700 + min_byte_value * 2100."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 337) * 1225 + ds % 4700 + mb * 2100


def zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62(file_path: "str | Path") -> int:
    """Return (compressed_size % 157) * 1300 + decompressed_size * 55 + file_size * 62."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 157) * 1300 + ds * 55 + fs * 62


def zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56(file_path: "str | Path") -> int:
    """Return compressed_size * 28 + (decompressed_size % 280) * 185 + file_size * 56."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 28 + (ds % 280) * 185 + fs * 56


def zst_file_size_mod_347_times_1350_plus_decompressed_size_mod_4800_plus_max_byte_value_times_270(file_path: "str | Path") -> int:
    """Return (file_size % 347) * 1350 + decompressed_size % 4800 + max_byte_value * 270."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 347) * 1350 + ds % 4800 + mb * 270


def zst_compressed_size_mod_349_times_1275_plus_decompressed_size_mod_4900_plus_min_byte_value_times_2150(file_path: "str | Path") -> int:
    """Return (compressed_size % 349) * 1275 + decompressed_size % 4900 + min_byte_value * 2150."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 349) * 1275 + ds % 4900 + mb * 2150


def zst_file_size_mod_353_times_1400_plus_decompressed_size_mod_5000_plus_max_byte_value_times_280(file_path: "str | Path") -> int:
    """Return (file_size % 353) * 1400 + decompressed_size % 5000 + max_byte_value * 280."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 353) * 1400 + ds % 5000 + mb * 280


def zst_compressed_size_mod_359_times_1325_plus_decompressed_size_mod_5100_plus_min_byte_value_times_2200(file_path: "str | Path") -> int:
    """Return (compressed_size % 359) * 1325 + decompressed_size % 5100 + min_byte_value * 2200."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 359) * 1325 + ds % 5100 + mb * 2200


def zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64(file_path: "str | Path") -> int:
    """Return (compressed_size % 163) * 1350 + decompressed_size * 57 + file_size * 64."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 163) * 1350 + ds * 57 + fs * 64


def zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58(file_path: "str | Path") -> int:
    """Return compressed_size * 29 + (decompressed_size % 290) * 190 + file_size * 58."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 29 + (ds % 290) * 190 + fs * 58


def zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(file_path: "str | Path") -> int:
    """Return (compressed_size % 293) * 19 + (decompressed_size % 1000) * 3 + max_byte_value * 100."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (cs % 293) * 19 + (ds % 1000) * 3 + mb * 100


def zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(file_path: "str | Path") -> int:
    """Return compressed_size * 29 + decompressed_size * 3 + max_byte_value * 7."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return cs * 29 + ds * 3 + mb * 7


def zst_file_size_mod_367_times_1450_plus_decompressed_size_mod_5200_plus_max_byte_value_times_290(file_path: "str | Path") -> int:
    """Return (file_size % 367) * 1450 + decompressed_size % 5200 + max_byte_value * 290."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 367) * 1450 + ds % 5200 + mb * 290


def zst_compressed_size_mod_373_times_1375_plus_decompressed_size_mod_5300_plus_min_byte_value_times_2250(file_path: "str | Path") -> int:
    """Return (compressed_size % 373) * 1375 + decompressed_size % 5300 + min_byte_value * 2250."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 373) * 1375 + ds % 5300 + mb * 2250


def zst_file_size_mod_379_times_1500_plus_decompressed_size_mod_5400_plus_max_byte_value_times_300(file_path: "str | Path") -> int:
    """Return (file_size % 379) * 1500 + decompressed_size % 5400 + max_byte_value * 300."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 379) * 1500 + ds % 5400 + mb * 300


def zst_compressed_size_mod_383_times_1425_plus_decompressed_size_mod_5500_plus_min_byte_value_times_2300(file_path: "str | Path") -> int:
    """Return (compressed_size % 383) * 1425 + decompressed_size % 5500 + min_byte_value * 2300."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 383) * 1425 + ds % 5500 + mb * 2300


def zst_file_size_mod_389_times_1550_plus_decompressed_size_mod_5600_plus_max_byte_value_times_310(file_path: "str | Path") -> int:
    """Return (file_size % 389) * 1550 + decompressed_size % 5600 + max_byte_value * 310."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 389) * 1550 + ds % 5600 + mb * 310


def zst_compressed_size_mod_397_times_1475_plus_decompressed_size_mod_5700_plus_min_byte_value_times_2350(file_path: "str | Path") -> int:
    """Return (compressed_size % 397) * 1475 + decompressed_size % 5700 + min_byte_value * 2350."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 397) * 1475 + ds % 5700 + mb * 2350


def zst_file_size_mod_401_times_1600_plus_decompressed_size_mod_5800_plus_max_byte_value_times_320(file_path: "str | Path") -> int:
    """Return (file_size % 401) * 1600 + decompressed_size % 5800 + max_byte_value * 320."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 401) * 1600 + ds % 5800 + mb * 320


def zst_compressed_size_mod_409_times_1525_plus_decompressed_size_mod_5900_plus_min_byte_value_times_2400(file_path: "str | Path") -> int:
    """Return (compressed_size % 409) * 1525 + decompressed_size % 5900 + min_byte_value * 2400."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 409) * 1525 + ds % 5900 + mb * 2400


def zst_file_size_mod_419_times_1650_plus_decompressed_size_mod_6000_plus_max_byte_value_times_330(file_path: "str | Path") -> int:
    """Return (file_size % 419) * 1650 + decompressed_size % 6000 + max_byte_value * 330."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 419) * 1650 + ds % 6000 + mb * 330


def zst_compressed_size_mod_421_times_1575_plus_decompressed_size_mod_6100_plus_min_byte_value_times_2450(file_path: "str | Path") -> int:
    """Return (compressed_size % 421) * 1575 + decompressed_size % 6100 + min_byte_value * 2450."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 421) * 1575 + ds % 6100 + mb * 2450


def zst_file_size_mod_431_times_1700_plus_decompressed_size_mod_6200_plus_max_byte_value_times_340(file_path: "str | Path") -> int:
    """Return (file_size % 431) * 1700 + decompressed_size % 6200 + max_byte_value * 340."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 431) * 1700 + ds % 6200 + mb * 340


def zst_compressed_size_mod_433_times_1625_plus_decompressed_size_mod_6300_plus_min_byte_value_times_2500(file_path: "str | Path") -> int:
    """Return (compressed_size % 433) * 1625 + decompressed_size % 6300 + min_byte_value * 2500."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_min_byte_value(file_path)
    return (cs % 433) * 1625 + ds % 6300 + mb * 2500


def zst_compressed_mod_167_times_1400_plus_decompressed_times_59_plus_file_size_times_66(file_path: "str | Path") -> int:
    """Return (compressed_size % 167) * 1400 + decompressed_size * 59 + file_size * 66."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 167) * 1400 + ds * 59 + fs * 66


def zst_compressed_times_30_plus_decompressed_mod_300_times_195_plus_file_size_times_60(file_path: "str | Path") -> int:
    """Return compressed_size * 30 + (decompressed_size % 300) * 195 + file_size * 60."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 30 + (ds % 300) * 195 + fs * 60


def zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68(file_path: "str | Path") -> int:
    """Return (compressed_size % 173) * 1450 + decompressed_size * 61 + file_size * 68."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 173) * 1450 + ds * 61 + fs * 68


def zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62(file_path: "str | Path") -> int:
    """Return compressed_size * 31 + (decompressed_size % 310) * 200 + file_size * 62."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 31 + (ds % 310) * 200 + fs * 62


def zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70(file_path: "str | Path") -> int:
    """Return (compressed_size % 173) * 1500 + decompressed_size * 63 + file_size * 70."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 173) * 1500 + ds * 63 + fs * 70


def zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64(file_path: "str | Path") -> int:
    """Return compressed_size * 33 + (decompressed_size % 320) * 210 + file_size * 64."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 33 + (ds % 320) * 210 + fs * 64


def zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72(file_path: "str | Path") -> int:
    """Return (compressed_size % 179) * 1550 + decompressed_size * 65 + file_size * 72."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 179) * 1550 + ds * 65 + fs * 72


def zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66(file_path: "str | Path") -> int:
    """Return compressed_size * 35 + (decompressed_size % 330) * 220 + file_size * 66."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 35 + (ds % 330) * 220 + fs * 66




def zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74(file_path: "str | Path") -> int:
    """Return (compressed_size % 181) * 1600 + decompressed_size * 67 + file_size * 74."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 181) * 1600 + ds * 67 + fs * 74


def zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68(file_path: "str | Path") -> int:
    """Return compressed_size * 37 + (decompressed_size % 340) * 230 + file_size * 68."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 37 + (ds % 340) * 230 + fs * 68


def zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(file_path: "str | Path") -> int:
    """Return (compressed_size % 431) * 27 + (decompressed_size % 1100) * 5 + max_byte_value * 200."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (cs % 431) * 27 + (ds % 1100) * 5 + mb * 200


def zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(file_path: "str | Path") -> int:
    """Return compressed_size * 31 + decompressed_size * 5 + max_byte_value * 11."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return cs * 31 + ds * 5 + mb * 11


def zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76(file_path: "str | Path") -> int:
    """Return (compressed_size % 183) * 1650 + decompressed_size * 69 + file_size * 76."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 183) * 1650 + ds * 69 + fs * 76


def zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70(file_path: "str | Path") -> int:
    """Return compressed_size * 39 + (decompressed_size % 350) * 240 + file_size * 70."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 39 + (ds % 350) * 240 + fs * 70


def zst_compressed_mod_187_times_1700_plus_decompressed_times_71_plus_file_size_times_78(file_path: "str | Path") -> int:
    """Return (compressed_size % 187) * 1700 + decompressed_size * 71 + file_size * 78."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 187) * 1700 + ds * 71 + fs * 78


def zst_compressed_times_41_plus_decompressed_mod_360_times_250_plus_file_size_times_72(file_path: "str | Path") -> int:
    """Return compressed_size * 41 + (decompressed_size % 360) * 250 + file_size * 72."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 41 + (ds % 360) * 250 + fs * 72


def zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80(file_path: "str | Path") -> int:
    """Return (compressed_size % 191) * 1750 + decompressed_size * 73 + file_size * 80."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 191) * 1750 + ds * 73 + fs * 80


def zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74(file_path: "str | Path") -> int:
    """Return compressed_size * 43 + (decompressed_size % 370) * 260 + file_size * 74."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 43 + (ds % 370) * 260 + fs * 74


def zst_compressed_mod_193_times_1800_plus_decompressed_times_75_plus_file_size_times_82(file_path: "str | Path") -> int:
    """Return (compressed_size % 193) * 1800 + decompressed_size * 75 + file_size * 82."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 193) * 1800 + ds * 75 + fs * 82


def zst_compressed_times_45_plus_decompressed_mod_380_times_270_plus_file_size_times_76(file_path: "str | Path") -> int:
    """Return compressed_size * 45 + (decompressed_size % 380) * 270 + file_size * 76."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 45 + (ds % 380) * 270 + fs * 76


def zst_file_size_mod_439_times_1750_plus_decompressed_size_mod_6400_plus_max_byte_value_times_350(file_path: "str | Path") -> int:
    """Return (file_size % 439) * 1750 + decompressed_size % 6400 + max_byte_value * 350."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 439) * 1750 + (ds % 6400) + mx * 350


def zst_compressed_size_mod_443_times_1675_plus_decompressed_size_mod_6500_plus_min_byte_value_times_2550(file_path: "str | Path") -> int:
    """Return (compressed_size % 443) * 1675 + decompressed_size % 6500 + min_byte_value * 2550."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 443) * 1675 + (ds % 6500) + mn * 2550


def zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84(file_path: "str | Path") -> int:
    """Return (compressed_size % 197) * 1850 + decompressed_size * 77 + file_size * 84."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 197) * 1850 + ds * 77 + fs * 84


def zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78(file_path: "str | Path") -> int:
    """Return compressed_size * 47 + (decompressed_size % 390) * 280 + file_size * 78."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 47 + (ds % 390) * 280 + fs * 78


def zst_file_size_mod_449_times_1800_plus_decompressed_size_mod_6600_plus_max_byte_value_times_360(file_path: "str | Path") -> int:
    """Return (file_size % 449) * 1800 + decompressed_size % 6600 + max_byte_value * 360."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 449) * 1800 + (ds % 6600) + mx * 360


def zst_compressed_size_mod_457_times_1725_plus_decompressed_size_mod_6700_plus_min_byte_value_times_2600(file_path: "str | Path") -> int:
    """Return (compressed_size % 457) * 1725 + decompressed_size % 6700 + min_byte_value * 2600."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 457) * 1725 + (ds % 6700) + mn * 2600


def zst_file_size_mod_461_times_1850_plus_decompressed_size_mod_6800_plus_max_byte_value_times_370(file_path: "str | Path") -> int:
    """Return (file_size % 461) * 1850 + decompressed_size % 6800 + max_byte_value * 370."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 461) * 1850 + (ds % 6800) + mx * 370


def zst_compressed_size_mod_463_times_1775_plus_decompressed_size_mod_6900_plus_min_byte_value_times_2650(file_path: "str | Path") -> int:
    """Return (compressed_size % 463) * 1775 + decompressed_size % 6900 + min_byte_value * 2650."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 463) * 1775 + (ds % 6900) + mn * 2650


def zst_compressed_mod_199_times_1900_plus_decompressed_times_79_plus_file_size_times_86(file_path: "str | Path") -> int:
    """Return (compressed_size % 199) * 1900 + decompressed_size * 79 + file_size * 86."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 199) * 1900 + ds * 79 + fs * 86


def zst_compressed_times_49_plus_decompressed_mod_400_times_290_plus_file_size_times_80(file_path: "str | Path") -> int:
    """Return compressed_size * 49 + (decompressed_size % 400) * 290 + file_size * 80."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 49 + (ds % 400) * 290 + fs * 80


def zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(file_path: "str | Path") -> int:
    """Return (compressed_size % 467) * 29 + (decompressed_size % 7000) * 5 + max_byte_value * 210."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (cs % 467) * 29 + (ds % 7000) * 5 + mb * 210


def zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(file_path: "str | Path") -> int:
    """Return compressed_size * 33 + decompressed_size * 6 + max_byte_value * 13."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return cs * 33 + ds * 6 + mb * 13


def zst_file_size_mod_467_times_1900_plus_decompressed_size_mod_7000_plus_max_byte_value_times_380(file_path: "str | Path") -> int:
    """Return (file_size % 467) * 1900 + decompressed_size % 7000 + max_byte_value * 380."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 467) * 1900 + (ds % 7000) + mx * 380


def zst_compressed_size_mod_479_times_1825_plus_decompressed_size_mod_7100_plus_min_byte_value_times_2700(file_path: "str | Path") -> int:
    """Return (compressed_size % 479) * 1825 + decompressed_size % 7100 + min_byte_value * 2700."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 479) * 1825 + (ds % 7100) + mn * 2700


def zst_compressed_mod_201_times_1950_plus_decompressed_times_81_plus_file_size_times_88(file_path: "str | Path") -> int:
    """Return (compressed_size % 201) * 1950 + decompressed_size * 81 + file_size * 88."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 201) * 1950 + ds * 81 + fs * 88


def zst_compressed_times_51_plus_decompressed_mod_410_times_300_plus_file_size_times_82(file_path: "str | Path") -> int:
    """Return compressed_size * 51 + (decompressed_size % 410) * 300 + file_size * 82."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 51 + (ds % 410) * 300 + fs * 82


def zst_file_size_mod_487_times_1950_plus_decompressed_size_mod_7200_plus_max_byte_value_times_390(file_path: "str | Path") -> int:
    """Return (file_size % 487) * 1950 + decompressed_size % 7200 + max_byte_value * 390."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 487) * 1950 + (ds % 7200) + mx * 390


def zst_compressed_size_mod_491_times_1875_plus_decompressed_size_mod_7300_plus_min_byte_value_times_2750(file_path: "str | Path") -> int:
    """Return (compressed_size % 491) * 1875 + decompressed_size % 7300 + min_byte_value * 2750."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 491) * 1875 + (ds % 7300) + mn * 2750


def zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90(file_path: "str | Path") -> int:
    """Return (compressed_size % 203) * 2000 + decompressed_size * 83 + file_size * 90."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 203) * 2000 + ds * 83 + fs * 90


def zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84(file_path: "str | Path") -> int:
    """Return compressed_size * 53 + (decompressed_size % 420) * 310 + file_size * 84."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 53 + (ds % 420) * 310 + fs * 84


def zst_compressed_mod_207_times_2050_plus_decompressed_times_85_plus_file_size_times_92(file_path: "str | Path") -> int:
    """Return (compressed_size % 207) * 2050 + decompressed_size * 85 + file_size * 92."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 207) * 2050 + ds * 85 + fs * 92


def zst_compressed_times_55_plus_decompressed_mod_430_times_320_plus_file_size_times_86(file_path: "str | Path") -> int:
    """Return compressed_size * 55 + (decompressed_size % 430) * 320 + file_size * 86."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 55 + (ds % 430) * 320 + fs * 86


def zst_file_size_mod_499_times_1975_plus_decompressed_size_mod_7400_plus_max_byte_value_times_400(file_path: "str | Path") -> int:
    """Return (file_size % 499) * 1975 + decompressed_size % 7400 + max_byte_value * 400."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 499) * 1975 + (ds % 7400) + mx * 400


def zst_compressed_size_mod_503_times_1925_plus_decompressed_size_mod_7500_plus_min_byte_value_times_2800(file_path: "str | Path") -> int:
    """Return (compressed_size % 503) * 1925 + decompressed_size % 7500 + min_byte_value * 2800."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 503) * 1925 + (ds % 7500) + mn * 2800


def zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94(file_path: "str | Path") -> int:
    """Return (compressed_size % 211) * 2100 + decompressed_size * 87 + file_size * 94."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 211) * 2100 + ds * 87 + fs * 94


def zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88(file_path: "str | Path") -> int:
    """Return compressed_size * 57 + (decompressed_size % 440) * 330 + file_size * 88."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 57 + (ds % 440) * 330 + fs * 88


def zst_file_size_mod_509_times_2000_plus_decompressed_size_mod_7600_plus_max_byte_value_times_410(file_path: "str | Path") -> int:
    """Return (file_size % 509) * 2000 + decompressed_size % 7600 + max_byte_value * 410."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 509) * 2000 + (ds % 7600) + mx * 410


def zst_compressed_size_mod_521_times_1950_plus_decompressed_size_mod_7700_plus_min_byte_value_times_2850(file_path: "str | Path") -> int:
    """Return (compressed_size % 521) * 1950 + decompressed_size % 7700 + min_byte_value * 2850."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 521) * 1950 + (ds % 7700) + mn * 2850


def zst_compressed_size_mod_523_times_31_plus_decompressed_size_mod_7800_times_5_plus_max_byte_value_times_215(file_path: "str | Path") -> int:
    """Return (compressed_size % 523) * 31 + (decompressed_size % 7800) * 5 + max_byte_value * 215."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (cs % 523) * 31 + (ds % 7800) * 5 + mb * 215


def zst_compressed_size_times_35_plus_decompressed_size_times_7_plus_max_byte_value_times_15(file_path: "str | Path") -> int:
    """Return compressed_size * 35 + decompressed_size * 7 + max_byte_value * 15."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return cs * 35 + ds * 7 + mb * 15


def zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96(file_path: "str | Path") -> int:
    """Return (compressed_size % 213) * 2150 + decompressed_size * 89 + file_size * 96."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 213) * 2150 + ds * 89 + fs * 96


def zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90(file_path: "str | Path") -> int:
    """Return compressed_size * 59 + (decompressed_size % 450) * 340 + file_size * 90."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 59 + (ds % 450) * 340 + fs * 90


def zst_file_size_mod_523_times_2025_plus_decompressed_size_mod_7800_plus_max_byte_value_times_420(file_path: "str | Path") -> int:
    """Return (file_size % 523) * 2025 + decompressed_size % 7800 + max_byte_value * 420."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 523) * 2025 + (ds % 7800) + mx * 420


def zst_compressed_size_mod_541_times_1975_plus_decompressed_size_mod_7900_plus_min_byte_value_times_2900(file_path: "str | Path") -> int:
    """Return (compressed_size % 541) * 1975 + decompressed_size % 7900 + min_byte_value * 2900."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 541) * 1975 + (ds % 7900) + mn * 2900


def zst_compressed_mod_215_times_2200_plus_decompressed_times_91_plus_file_size_times_98(file_path: "str | Path") -> int:
    """Return (compressed_size % 215) * 2200 + decompressed_size * 91 + file_size * 98."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 215) * 2200 + ds * 91 + fs * 98


def zst_compressed_times_61_plus_decompressed_mod_460_times_350_plus_file_size_times_92(file_path: "str | Path") -> int:
    """Return compressed_size * 61 + (decompressed_size % 460) * 350 + file_size * 92."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 61 + (ds % 460) * 350 + fs * 92


def zst_file_size_mod_547_times_2050_plus_decompressed_size_mod_8000_plus_max_byte_value_times_430(file_path: "str | Path") -> int:
    """Return (file_size % 547) * 2050 + decompressed_size % 8000 + max_byte_value * 430."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 547) * 2050 + (ds % 8000) + mx * 430


def zst_compressed_size_mod_557_times_2000_plus_decompressed_size_mod_8100_plus_min_byte_value_times_2950(file_path: "str | Path") -> int:
    """Return (compressed_size % 557) * 2000 + decompressed_size % 8100 + min_byte_value * 2950."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 557) * 2000 + (ds % 8100) + mn * 2950


def zst_compressed_mod_217_times_2250_plus_decompressed_times_93_plus_file_size_times_100(file_path: "str | Path") -> int:
    """Return (compressed_size % 217) * 2250 + decompressed_size * 93 + file_size * 100."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 217) * 2250 + ds * 93 + fs * 100


def zst_compressed_times_63_plus_decompressed_mod_470_times_360_plus_file_size_times_94(file_path: "str | Path") -> int:
    """Return compressed_size * 63 + (decompressed_size % 470) * 360 + file_size * 94."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 63 + (ds % 470) * 360 + fs * 94


def zst_file_size_mod_563_times_2075_plus_decompressed_size_mod_8200_plus_max_byte_value_times_440(file_path: "str | Path") -> int:
    """Return (file_size % 563) * 2075 + decompressed_size % 8200 + max_byte_value * 440."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 563) * 2075 + (ds % 8200) + mx * 440


def zst_compressed_size_mod_569_times_2025_plus_decompressed_size_mod_8300_plus_min_byte_value_times_3000(file_path: "str | Path") -> int:
    """Return (compressed_size % 569) * 2025 + decompressed_size % 8300 + min_byte_value * 3000."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 569) * 2025 + (ds % 8300) + mn * 3000


def zst_compressed_mod_219_times_2300_plus_decompressed_times_95_plus_file_size_times_102(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 219) * 2300 + ds * 95 + fs * 102


def zst_compressed_times_65_plus_decompressed_mod_480_times_370_plus_file_size_times_96(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 65 + (ds % 480) * 370 + fs * 96


def zst_file_size_mod_571_times_2100_plus_decompressed_size_mod_8400_plus_max_byte_value_times_450(file_path: "str | Path") -> int:
    """Return (file_size % 571) * 2100 + decompressed_size % 8400 + max_byte_value * 450."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 571) * 2100 + (ds % 8400) + mx * 450


def zst_compressed_size_mod_577_times_2050_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3050(file_path: "str | Path") -> int:
    """Return (compressed_size % 577) * 2050 + decompressed_size % 8500 + min_byte_value * 3050."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 577) * 2050 + (ds % 8500) + mn * 3050


def zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 221) * 2350 + ds * 97 + fs * 104


def zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 67 + (ds % 490) * 380 + fs * 98


def zst_file_size_mod_587_times_2125_plus_decompressed_size_mod_8600_plus_max_byte_value_times_460(file_path: "str | Path") -> int:
    """Return (file_size % 587) * 2125 + decompressed_size % 8600 + max_byte_value * 460."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 587) * 2125 + (ds % 8600) + mx * 460


def zst_compressed_size_mod_593_times_2075_plus_decompressed_size_mod_8700_plus_min_byte_value_times_3100(file_path: "str | Path") -> int:
    """Return (compressed_size % 593) * 2075 + decompressed_size % 8700 + min_byte_value * 3100."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 593) * 2075 + (ds % 8700) + mn * 3100


def zst_compressed_mod_223_times_2400_plus_decompressed_times_99_plus_file_size_times_106(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 223) * 2400 + ds * 99 + fs * 106


def zst_compressed_times_69_plus_decompressed_mod_500_times_390_plus_file_size_times_100(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 69 + (ds % 500) * 390 + fs * 100


def zst_file_size_mod_599_times_2150_plus_decompressed_size_mod_8800_plus_max_byte_value_times_470(file_path: "str | Path") -> int:
    """Return (file_size % 599) * 2150 + decompressed_size % 8800 + max_byte_value * 470."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 599) * 2150 + (ds % 8800) + mx * 470


def zst_compressed_size_mod_601_times_2100_plus_decompressed_size_mod_8900_plus_min_byte_value_times_3150(file_path: "str | Path") -> int:
    """Return (compressed_size % 601) * 2100 + decompressed_size % 8900 + min_byte_value * 3150."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 601) * 2100 + (ds % 8900) + mn * 3150


def zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 227) * 2450 + ds * 101 + fs * 108


def zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 71 + (ds % 510) * 400 + fs * 102


def zst_file_size_mod_607_times_2175_plus_decompressed_size_mod_9000_plus_max_byte_value_times_480(file_path: "str | Path") -> int:
    """Return (file_size % 607) * 2175 + decompressed_size % 9000 + max_byte_value * 480."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 607) * 2175 + (ds % 9000) + mx * 480


def zst_compressed_size_mod_613_times_2125_plus_decompressed_size_mod_9100_plus_min_byte_value_times_3200(file_path: "str | Path") -> int:
    """Return (compressed_size % 613) * 2125 + decompressed_size % 9100 + min_byte_value * 3200."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 613) * 2125 + (ds % 9100) + mn * 3200


def zst_compressed_size_mod_547_times_31_plus_decompressed_size_mod_8000_times_5_plus_max_byte_value_times_220(file_path: "str | Path") -> int:
    """Return (compressed_size % 547) * 31 + (decompressed_size % 8000) * 5 + max_byte_value * 220."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (cs % 547) * 31 + (ds % 8000) * 5 + mb * 220


def zst_compressed_size_times_37_plus_decompressed_size_times_8_plus_max_byte_value_times_16(file_path: "str | Path") -> int:
    """Return compressed_size * 37 + decompressed_size * 8 + max_byte_value * 16."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return cs * 37 + ds * 8 + mb * 16


def zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 229) * 2500 + ds * 103 + fs * 110


def zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 73 + (ds % 520) * 410 + fs * 104


def zst_file_size_mod_617_times_2200_plus_decompressed_size_mod_9200_plus_max_byte_value_times_490(file_path: "str | Path") -> int:
    """Return (file_size % 617) * 2200 + decompressed_size % 9200 + max_byte_value * 490."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 617) * 2200 + (ds % 9200) + mx * 490


def zst_compressed_size_mod_619_times_2150_plus_decompressed_size_mod_9300_plus_min_byte_value_times_3250(file_path: "str | Path") -> int:
    """Return (compressed_size % 619) * 2150 + decompressed_size % 9300 + min_byte_value * 3250."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 619) * 2150 + (ds % 9300) + mn * 3250


def zst_compressed_mod_233_times_2550_plus_decompressed_times_105_plus_file_size_times_112(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 233) * 2550 + ds * 105 + fs * 112


def zst_compressed_times_75_plus_decompressed_mod_530_times_420_plus_file_size_times_106(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 75 + (ds % 530) * 420 + fs * 106


def zst_compressed_mod_239_times_2600_plus_decompressed_times_107_plus_file_size_times_114(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 239) * 2600 + ds * 107 + fs * 114


def zst_compressed_times_77_plus_decompressed_mod_540_times_430_plus_file_size_times_108(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 77 + (ds % 540) * 430 + fs * 108


def zst_file_size_mod_631_times_2250_plus_decompressed_size_mod_9400_plus_max_byte_value_times_500(file_path: "str | Path") -> int:
    """Return (file_size % 631) * 2250 + decompressed_size % 9400 + max_byte_value * 500."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 631) * 2250 + (ds % 9400) + mx * 500


def zst_compressed_size_mod_641_times_2200_plus_decompressed_size_mod_9500_plus_min_byte_value_times_3300(file_path: "str | Path") -> int:
    """Return (compressed_size % 641) * 2200 + decompressed_size % 9500 + min_byte_value * 3300."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 641) * 2200 + (ds % 9500) + mn * 3300


def zst_compressed_mod_241_times_2650_plus_decompressed_times_109_plus_file_size_times_116(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 241) * 2650 + ds * 109 + fs * 116


def zst_compressed_times_79_plus_decompressed_mod_550_times_440_plus_file_size_times_110(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 79 + (ds % 550) * 440 + fs * 110


def zst_file_size_mod_643_times_2300_plus_decompressed_size_mod_9600_plus_max_byte_value_times_510(file_path: "str | Path") -> int:
    """Return (file_size % 643) * 2300 + decompressed_size % 9600 + max_byte_value * 510."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 643) * 2300 + (ds % 9600) + mx * 510


def zst_compressed_size_mod_647_times_2250_plus_decompressed_size_mod_9700_plus_min_byte_value_times_3350(file_path: "str | Path") -> int:
    """Return (compressed_size % 647) * 2250 + decompressed_size % 9700 + min_byte_value * 3350."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 647) * 2250 + (ds % 9700) + mn * 3350


def zst_compressed_mod_243_times_2700_plus_decompressed_times_111_plus_file_size_times_118(file_path: "str | Path") -> int:
    """Return (compressed_size % 243) * 2700 + decompressed_size * 111 + file_size * 118."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 243) * 2700 + ds * 111 + fs * 118


def zst_compressed_times_81_plus_decompressed_mod_560_times_450_plus_file_size_times_112(file_path: "str | Path") -> int:
    """Return compressed_size * 81 + (decompressed_size % 560) * 450 + file_size * 112."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 81 + (ds % 560) * 450 + fs * 112


def _dummy_sal_test(): pass


def zst_compressed_mod_247_times_2750_plus_decompressed_times_113_plus_file_size_times_120(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 247) * 2750 + ds * 113 + fs * 120


def zst_compressed_times_83_plus_decompressed_mod_570_times_460_plus_file_size_times_114(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 83 + (ds % 570) * 460 + fs * 114


def zst_file_size_mod_653_times_2350_plus_decompressed_size_mod_9800_plus_max_byte_value_times_520(file_path: "str | Path") -> int:
    """Return (file_size % 653) * 2350 + decompressed_size % 9800 + max_byte_value * 520."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 653) * 2350 + (ds % 9800) + mx * 520


def zst_compressed_size_mod_659_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_3400(file_path: "str | Path") -> int:
    """Return (compressed_size % 659) * 2300 + decompressed_size % 9900 + min_byte_value * 3400."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 659) * 2300 + (ds % 9900) + mn * 3400


def zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(file_path: "str | Path") -> int:
    """Return (compressed_size % 557) * 31 + (decompressed_size % 8200) * 5 + max_byte_value * 225."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (cs % 557) * 31 + (ds % 8200) * 5 + mb * 225


def zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(file_path: "str | Path") -> int:
    """Return compressed_size * 39 + decompressed_size * 9 + max_byte_value * 17."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return cs * 39 + ds * 9 + mb * 17


def zst_compressed_mod_251_times_2800_plus_decompressed_times_115_plus_file_size_times_122(file_path: "str | Path") -> int:
    """Return (compressed_size % 251) * 2800 + decompressed_size * 115 + file_size * 122."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 251) * 2800 + ds * 115 + fs * 122


def zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(file_path: "str | Path") -> int:
    """Return compressed_size * 85 + (decompressed_size % 580) * 470 + file_size * 116."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 85 + (ds % 580) * 470 + fs * 116


def zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 253) * 2800 + ds * 115 + fs * 122


def zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 85 + (ds % 580) * 470 + fs * 116


def zst_file_size_mod_661_times_2400_plus_decompressed_size_mod_9900_plus_max_byte_value_times_530(file_path: "str | Path") -> int:
    """Return (file_size % 661) * 2400 + decompressed_size % 9900 + max_byte_value * 530."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 661) * 2400 + (ds % 9900) + mx * 530


def zst_compressed_size_mod_673_times_2350_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3450(file_path: "str | Path") -> int:
    """Return (compressed_size % 673) * 2350 + decompressed_size % 9800 + min_byte_value * 3450."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 673) * 2350 + (ds % 9800) + mn * 3450


def zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 257) * 2850 + ds * 117 + fs * 124


def zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 87 + (ds % 590) * 480 + fs * 118


def zst_compressed_mod_259_times_2900_plus_decompressed_times_119_plus_file_size_times_126(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 259) * 2900 + ds * 119 + fs * 126


def zst_compressed_times_89_plus_decompressed_mod_600_times_490_plus_file_size_times_120(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 89 + (ds % 600) * 490 + fs * 120


def zst_file_size_mod_677_times_2450_plus_decompressed_size_mod_9700_plus_max_byte_value_times_540(file_path: "str | Path") -> int:
    """Return (file_size % 677) * 2450 + decompressed_size % 9700 + max_byte_value * 540."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 677) * 2450 + (ds % 9700) + mx * 540


def zst_compressed_size_mod_683_times_2400_plus_decompressed_size_mod_9600_plus_min_byte_value_times_3500(file_path: "str | Path") -> int:
    """Return (compressed_size % 683) * 2400 + decompressed_size % 9600 + min_byte_value * 3500."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 683) * 2400 + (ds % 9600) + mn * 3500


def zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 263) * 2950 + ds * 121 + fs * 128


def zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 91 + (ds % 610) * 500 + fs * 122


def zst_file_size_mod_691_times_2500_plus_decompressed_size_mod_9500_plus_max_byte_value_times_550(file_path: "str | Path") -> int:
    """Return (file_size % 691) * 2500 + decompressed_size % 9500 + max_byte_value * 550."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 691) * 2500 + (ds % 9500) + mx * 550


def zst_compressed_size_mod_701_times_2450_plus_decompressed_size_mod_9400_plus_min_byte_value_times_3550(file_path: "str | Path") -> int:
    """Return (compressed_size % 701) * 2450 + decompressed_size % 9400 + min_byte_value * 3550."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 701) * 2450 + (ds % 9400) + mn * 3550


def zst_compressed_mod_269_times_3000_plus_decompressed_times_123_plus_file_size_times_130(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 269) * 3000 + ds * 123 + fs * 130


def zst_compressed_times_93_plus_decompressed_mod_620_times_510_plus_file_size_times_124(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 93 + (ds % 620) * 510 + fs * 124


def zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 271) * 3050 + ds * 125 + fs * 132


def zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 95 + (ds % 630) * 520 + fs * 126

def zst_compressed_size_mod_563_times_31_plus_decompressed_size_mod_8400_times_5_plus_max_byte_value_times_230(file_path):
    cs = zst_compressed_size(file_path); ds = zst_decompressed_size(file_path); mb = zst_max_byte_value(file_path)
    return (cs % 563) * 31 + (ds % 8400) * 5 + mb * 230

def zst_compressed_size_times_41_plus_decompressed_size_times_10_plus_max_byte_value_times_18(file_path):
    cs = zst_compressed_size(file_path); ds = zst_decompressed_size(file_path); mb = zst_max_byte_value(file_path)
    return cs * 41 + ds * 10 + mb * 18


def zst_file_size_mod_709_times_2550_plus_decompressed_size_mod_9300_plus_max_byte_value_times_560(file_path):
    """Return (file_size % 709) * 2550 + decompressed_size % 9300 + max_byte_value * 560."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 709) * 2550 + (ds % 9300) + mx * 560


def zst_compressed_size_mod_719_times_2500_plus_decompressed_size_mod_9200_plus_min_byte_value_times_3600(file_path):
    """Return (compressed_size % 719) * 2500 + decompressed_size % 9200 + min_byte_value * 3600."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 719) * 2500 + (ds % 9200) + mn * 3600


def zst_file_size_mod_727_times_2600_plus_decompressed_size_mod_9100_plus_max_byte_value_times_570(file_path):
    """Return (file_size % 727) * 2600 + decompressed_size % 9100 + max_byte_value * 570."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 727) * 2600 + (ds % 9100) + mx * 570


def zst_compressed_size_mod_733_times_2550_plus_decompressed_size_mod_9000_plus_min_byte_value_times_3650(file_path):
    """Return (compressed_size % 733) * 2550 + decompressed_size % 9000 + min_byte_value * 3650."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 733) * 2550 + (ds % 9000) + mn * 3650


def zst_file_size_mod_739_times_2650_plus_decompressed_size_mod_8900_plus_max_byte_value_times_580(file_path):
    """Return (file_size % 739) * 2650 + decompressed_size % 8900 + max_byte_value * 580."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 739) * 2650 + (ds % 8900) + mx * 580


def zst_compressed_size_mod_743_times_2600_plus_decompressed_size_mod_8800_plus_min_byte_value_times_3700(file_path):
    """Return (compressed_size % 743) * 2600 + decompressed_size % 8800 + min_byte_value * 3700."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 743) * 2600 + (ds % 8800) + mn * 3700


def zst_file_size_mod_751_times_2700_plus_decompressed_size_mod_8700_plus_max_byte_value_times_590(file_path):
    """Return (file_size % 751) * 2700 + decompressed_size % 8700 + max_byte_value * 590."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 751) * 2700 + (ds % 8700) + mx * 590


def zst_compressed_size_mod_757_times_2650_plus_decompressed_size_mod_8600_plus_min_byte_value_times_3750(file_path):
    """Return (compressed_size % 757) * 2650 + decompressed_size % 8600 + min_byte_value * 3750."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 757) * 2650 + (ds % 8600) + mn * 3750


def zst_file_size_mod_761_times_2750_plus_decompressed_size_mod_8500_plus_max_byte_value_times_600(file_path):
    """Return (file_size % 761) * 2750 + decompressed_size % 8500 + max_byte_value * 600."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 761) * 2750 + (ds % 8500) + mx * 600


def zst_compressed_size_mod_769_times_2700_plus_decompressed_size_mod_8400_plus_min_byte_value_times_3800(file_path):
    """Return (compressed_size % 769) * 2700 + decompressed_size % 8400 + min_byte_value * 3800."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 769) * 2700 + (ds % 8400) + mn * 3800


def zst_file_size_mod_773_times_2800_plus_decompressed_size_mod_8600_plus_max_byte_value_times_650(file_path):
    """Return (file_size % 773) * 2800 + decompressed_size % 8600 + max_byte_value * 650."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 773) * 2800 + (ds % 8600) + mx * 650


def zst_compressed_size_mod_787_times_2750_plus_decompressed_size_mod_8500_plus_min_byte_value_times_3900(file_path):
    """Return (compressed_size % 787) * 2750 + decompressed_size % 8500 + min_byte_value * 3900."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 787) * 2750 + (ds % 8500) + mn * 3900


def zst_file_size_mod_797_times_2850_plus_decompressed_size_mod_8700_plus_max_byte_value_times_700(file_path):
    """Return (file_size % 797) * 2850 + decompressed_size % 8700 + max_byte_value * 700."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 797) * 2850 + (ds % 8700) + mx * 700


def zst_compressed_size_mod_809_times_2900_plus_decompressed_size_mod_8800_plus_min_byte_value_times_4000(file_path):
    """Return (compressed_size % 809) * 2900 + decompressed_size % 8800 + min_byte_value * 4000."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 809) * 2900 + (ds % 8800) + mn * 4000


def zst_file_size_mod_811_times_2950_plus_decompressed_size_mod_8900_plus_max_byte_value_times_750(file_path):
    """Return (file_size % 811) * 2950 + decompressed_size % 8900 + max_byte_value * 750."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 811) * 2950 + (ds % 8900) + mx * 750


def zst_compressed_size_mod_821_times_3000_plus_decompressed_size_mod_9000_plus_min_byte_value_times_4100(file_path):
    """Return (compressed_size % 821) * 3000 + decompressed_size % 9000 + min_byte_value * 4100."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 821) * 3000 + (ds % 9000) + mn * 4100


def zst_file_size_mod_823_times_3050_plus_decompressed_size_mod_9100_plus_max_byte_value_times_800(file_path):
    """Return (file_size % 823) * 3050 + decompressed_size % 9100 + max_byte_value * 800."""
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mx = zst_max_byte_value(file_path)
    return (fs % 823) * 3050 + (ds % 9100) + mx * 800


def zst_compressed_size_mod_827_times_3100_plus_decompressed_size_mod_9200_plus_min_byte_value_times_4200(file_path):
    """Return (compressed_size % 827) * 3100 + decompressed_size % 9200 + min_byte_value * 4200."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mn = zst_min_byte_value(file_path)
    return (cs % 827) * 3100 + (ds % 9200) + mn * 4200


def zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 277) * 3100 + ds * 127 + fs * 134


def zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 97 + (ds % 640) * 530 + fs * 128


def zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 281) * 3150 + ds * 129 + fs * 136


def zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 99 + (ds % 650) * 540 + fs * 130


def zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 283) * 3200 + ds * 131 + fs * 138


def zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 101 + (ds % 660) * 550 + fs * 132

def zst_compressed_size_mod_569_times_31_plus_decompressed_size_mod_8600_times_5_plus_max_byte_value_times_235(file_path):
    cs = zst_compressed_size(file_path); ds = zst_decompressed_size(file_path); mb = zst_max_byte_value(file_path)
    return (cs % 569) * 31 + (ds % 8600) * 5 + mb * 235

def zst_compressed_size_times_43_plus_decompressed_size_times_11_plus_max_byte_value_times_19(file_path):
    cs = zst_compressed_size(file_path); ds = zst_decompressed_size(file_path); mb = zst_max_byte_value(file_path)
    return cs * 43 + ds * 11 + mb * 19


def zst_compressed_mod_287_times_3250_plus_decompressed_times_133_plus_file_size_times_140(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 287) * 3250 + ds * 133 + fs * 140


def zst_compressed_times_103_plus_decompressed_mod_670_times_560_plus_file_size_times_134(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 103 + (ds % 670) * 560 + fs * 134


def zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 289) * 3300 + ds * 135 + fs * 142


def zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 105 + (ds % 680) * 570 + fs * 136


def zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 293) * 3350 + ds * 137 + fs * 144


def zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 107 + (ds % 690) * 580 + fs * 138


def zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 297) * 3400 + ds * 139 + fs * 146


def zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 109 + (ds % 700) * 590 + fs * 140


def zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 301) * 3450 + ds * 141 + fs * 148


def zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 111 + (ds % 710) * 600 + fs * 142


def zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(file_path):
    cs = zst_compressed_size(file_path); ds = zst_decompressed_size(file_path); mb = zst_max_byte_value(file_path)
    return (cs % 571) * 31 + (ds % 8800) * 5 + mb * 240


def zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(file_path):
    cs = zst_compressed_size(file_path); ds = zst_decompressed_size(file_path); mb = zst_max_byte_value(file_path)
    return cs * 45 + ds * 12 + mb * 20


def zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 307) * 3500 + ds * 143 + fs * 150


def zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 113 + (ds % 720) * 610 + fs * 144


def zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 311) * 3550 + ds * 145 + fs * 152


def zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 115 + (ds % 730) * 620 + fs * 146


def zst_compressed_mod_313_times_3600_plus_decompressed_times_147_plus_file_size_times_154(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 313) * 3600 + ds * 147 + fs * 154


def zst_compressed_times_117_plus_decompressed_mod_740_times_630_plus_file_size_times_148(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 117 + (ds % 740) * 630 + fs * 148


def zst_compressed_mod_317_times_3650_plus_decompressed_times_149_plus_file_size_times_156(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 317) * 3650 + ds * 149 + fs * 156


def zst_compressed_times_119_plus_decompressed_mod_750_times_640_plus_file_size_times_150(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 119 + (ds % 750) * 640 + fs * 150


def zst_compressed_mod_331_times_3700_plus_decompressed_times_151_plus_file_size_times_158(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 331) * 3700 + ds * 151 + fs * 158


def zst_compressed_times_121_plus_decompressed_mod_760_times_650_plus_file_size_times_152(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 121 + (ds % 760) * 650 + fs * 152


def _dummy_sal_test(): pass


def zst_compressed_mod_337_times_3750_plus_decompressed_times_153_plus_file_size_times_160(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 337) * 3750 + ds * 153 + fs * 160


def zst_compressed_times_123_plus_decompressed_mod_770_times_660_plus_file_size_times_154(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 123 + (ds % 770) * 660 + fs * 154


def zst_compressed_mod_347_times_3800_plus_decompressed_times_155_plus_file_size_times_162(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 347) * 3800 + ds * 155 + fs * 162


def zst_compressed_times_125_plus_decompressed_mod_780_times_670_plus_file_size_times_156(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 125 + (ds % 780) * 670 + fs * 156


def zst_compressed_mod_353_times_3850_plus_decompressed_times_157_plus_file_size_times_164(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 353) * 3850 + ds * 157 + fs * 164


def zst_compressed_times_127_plus_decompressed_mod_790_times_680_plus_file_size_times_158(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 127 + (ds % 790) * 680 + fs * 158


def zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 359) * 3900 + ds * 159 + fs * 166


def zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 129 + (ds % 800) * 690 + fs * 160


def zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(file_path: "str | Path") -> int:
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 839) * 3100 + (ds % 9300) + mb * 850


def zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mv = zst_min_byte_value(file_path)
    return (cs % 857) * 2100 + (ds % 9800) + mv * 3750


def zst_compressed_mod_367_times_3950_plus_decompressed_times_161_plus_file_size_times_168(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 367) * 3950 + ds * 161 + fs * 168


def zst_compressed_times_131_plus_decompressed_mod_810_times_700_plus_file_size_times_162(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 131 + (ds % 810) * 700 + fs * 162


def zst_compressed_mod_367_times_3950_plus_decompressed_times_161_plus_file_size_times_168(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 367) * 3950 + ds * 161 + fs * 168


def zst_compressed_times_131_plus_decompressed_mod_810_times_700_plus_file_size_times_162(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 131 + (ds % 810) * 700 + fs * 162


def zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 373) * 4000 + ds * 163 + fs * 170


def zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 133 + (ds % 820) * 710 + fs * 164


def zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 379) * 4050 + ds * 165 + fs * 172


def zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 135 + (ds % 830) * 720 + fs * 166


def zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 383) * 4100 + ds * 167 + fs * 174


def zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 137 + (ds % 840) * 730 + fs * 168


def zst_compressed_mod_389_times_4150_plus_decompressed_times_169_plus_file_size_times_176(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 389) * 4150 + ds * 169 + fs * 176


def zst_compressed_times_139_plus_decompressed_mod_850_times_740_plus_file_size_times_170(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 139 + (ds % 850) * 740 + fs * 170


def zst_compressed_mod_397_times_4200_plus_decompressed_times_171_plus_file_size_times_178(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 397) * 4200 + ds * 171 + fs * 178


def zst_compressed_times_141_plus_decompressed_mod_860_times_750_plus_file_size_times_172(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 141 + (ds % 860) * 750 + fs * 172


def zst_compressed_mod_391_times_4200_plus_decompressed_times_171_plus_file_size_times_178(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 391) * 4200 + ds * 171 + fs * 178


def zst_compressed_times_141_plus_decompressed_mod_870_times_760_plus_file_size_times_174(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 141 + (ds % 870) * 760 + fs * 174


def zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 397) * 4250 + ds * 173 + fs * 180


def zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 143 + (ds % 880) * 770 + fs * 176


def zst_compressed_mod_401_times_4300_plus_decompressed_times_175_plus_file_size_times_182(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 401) * 4300 + ds * 175 + fs * 182


def zst_compressed_times_149_plus_decompressed_mod_890_times_780_plus_file_size_times_178(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 149 + (ds % 890) * 780 + fs * 178


def zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900(file_path: "str | Path") -> int:
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 863) * 3200 + (ds % 9400) + mb * 900


def zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mv = zst_min_byte_value(file_path)
    return (cs % 877) * 2200 + (ds % 9900) + mv * 4000


def zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 409) * 4350 + ds * 175 + fs * 182


def zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 145 + (ds % 890) * 780 + fs * 178


def zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 419) * 4400 + ds * 177 + fs * 184


def zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 147 + (ds % 900) * 790 + fs * 180


def zst_compressed_mod_421_times_4450_plus_decompressed_times_179_plus_file_size_times_186(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 421) * 4450 + ds * 179 + fs * 186


def zst_compressed_times_151_plus_decompressed_mod_910_times_800_plus_file_size_times_182(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 151 + (ds % 910) * 800 + fs * 182


def zst_compressed_mod_431_times_4500_plus_decompressed_times_179_plus_file_size_times_186(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 431) * 4500 + ds * 179 + fs * 186


def zst_compressed_times_149_plus_decompressed_mod_910_times_800_plus_file_size_times_182(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 149 + (ds % 910) * 800 + fs * 182


def zst_compressed_mod_433_times_4550_plus_decompressed_times_181_plus_file_size_times_188(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 433) * 4550 + ds * 181 + fs * 188


def zst_compressed_times_151_plus_decompressed_mod_920_times_810_plus_file_size_times_184(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 151 + (ds % 920) * 810 + fs * 184


def zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 439) * 4600 + ds * 183 + fs * 190


def zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 153 + (ds % 930) * 820 + fs * 186


def zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 443) * 4650 + ds * 185 + fs * 192


def zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 155 + (ds % 940) * 830 + fs * 188


def zst_compressed_mod_449_times_4700_plus_decompressed_times_187_plus_file_size_times_194(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 449) * 4700 + ds * 187 + fs * 194


def zst_compressed_times_157_plus_decompressed_mod_950_times_840_plus_file_size_times_190(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 157 + (ds % 950) * 840 + fs * 190


def zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 457) * 4750 + ds * 189 + fs * 196


def zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 159 + (ds % 960) * 850 + fs * 192


def zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(file_path: "str | Path") -> int:
    fs = zst_file_size_bytes(file_path)
    ds = zst_decompressed_size(file_path)
    mb = zst_max_byte_value(file_path)
    return (fs % 877) * 3300 + (ds % 9500) + mb * 950


def zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    mv = zst_min_byte_value(file_path)
    return (cs % 881) * 2300 + (ds % 9900) + mv * 4250


def zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 461) * 4800 + ds * 191 + fs * 198


def zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 161 + (ds % 970) * 860 + fs * 194


def zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 461) * 4800 + ds * 191 + fs * 198


def zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 161 + (ds % 970) * 860 + fs * 194


def zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 463) * 4850 + ds * 193 + fs * 200


def zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 163 + (ds % 980) * 870 + fs * 196


def zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 467) * 4900 + ds * 195 + fs * 202


def zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 165 + (ds % 990) * 880 + fs * 198


def zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 479) * 4950 + ds * 197 + fs * 204


def zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(file_path: "str | Path") -> int:
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return cs * 167 + (ds % 1000) * 890 + fs * 200


def zst_compressed_mod_829_times_5000_plus_decompressed_times_203_plus_file_size_times_206(file_path: "str | Path") -> int:
    """Return (compressed_size % 829) * 5000 + decompressed_size * 203 + file_size * 206."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 829) * 5000 + ds * 203 + fs * 206


def zst_compressed_mod_853_times_5100_plus_decompressed_times_207_plus_file_size_times_210(file_path: "str | Path") -> int:
    """Return (compressed_size % 853) * 5100 + decompressed_size * 207 + file_size * 210."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 853) * 5100 + ds * 207 + fs * 210


def zst_compressed_mod_883_times_5200_plus_decompressed_times_209_plus_file_size_times_212(file_path: "str | Path") -> int:
    """Return (compressed_size % 883) * 5200 + decompressed_size * 209 + file_size * 212."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 883) * 5200 + ds * 209 + fs * 212


def zst_compressed_mod_907_times_5300_plus_decompressed_times_211_plus_file_size_times_214(file_path: "str | Path") -> int:
    """Return (compressed_size % 907) * 5300 + decompressed_size * 211 + file_size * 214."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 907) * 5300 + ds * 211 + fs * 214


def zst_compressed_mod_911_times_5400_plus_decompressed_times_213_plus_file_size_times_216(file_path: "str | Path") -> int:
    """Return (compressed_size % 911) * 5400 + decompressed_size * 213 + file_size * 216."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 911) * 5400 + ds * 213 + fs * 216


def zst_compressed_mod_919_times_5500_plus_decompressed_times_215_plus_file_size_times_218(file_path: "str | Path") -> int:
    """Return (compressed_size % 919) * 5500 + decompressed_size * 215 + file_size * 218."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 919) * 5500 + ds * 215 + fs * 218


def zst_compressed_mod_929_times_5600_plus_decompressed_times_217_plus_file_size_times_220(file_path: "str | Path") -> int:
    """Return (compressed_size % 929) * 5600 + decompressed_size * 217 + file_size * 220."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 929) * 5600 + ds * 217 + fs * 220


def zst_compressed_mod_937_times_5700_plus_decompressed_times_219_plus_file_size_times_222(file_path: "str | Path") -> int:
    """Return (compressed_size % 937) * 5700 + decompressed_size * 219 + file_size * 222."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 937) * 5700 + ds * 219 + fs * 222


def zst_compressed_mod_941_times_5800_plus_decompressed_times_221_plus_file_size_times_224(file_path: "str | Path") -> int:
    """Return (compressed_size % 941) * 5800 + decompressed_size * 221 + file_size * 224."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 941) * 5800 + ds * 221 + fs * 224


def zst_compressed_mod_947_times_5900_plus_decompressed_times_223_plus_file_size_times_226(file_path: "str | Path") -> int:
    """Return (compressed_size % 947) * 5900 + decompressed_size * 223 + file_size * 226."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 947) * 5900 + ds * 223 + fs * 226


def zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228(file_path: "str | Path") -> int:
    """Return (compressed_size % 953) * 6000 + decompressed_size * 225 + file_size * 228."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 953) * 6000 + ds * 225 + fs * 228


def zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230(file_path: "str | Path") -> int:
    """Return (compressed_size % 967) * 6100 + decompressed_size * 227 + file_size * 230."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 967) * 6100 + ds * 227 + fs * 230


def zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232(file_path: "str | Path") -> int:
    """Return (compressed_size % 971) * 6200 + decompressed_size * 229 + file_size * 232."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 971) * 6200 + ds * 229 + fs * 232


def zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234(file_path: "str | Path") -> int:
    """Return (compressed_size % 977) * 6300 + decompressed_size * 231 + file_size * 234."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 977) * 6300 + ds * 231 + fs * 234


def zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236(file_path: "str | Path") -> int:
    """Return (compressed_size % 983) * 6400 + decompressed_size * 233 + file_size * 236."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 983) * 6400 + ds * 233 + fs * 236


def zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238(file_path: "str | Path") -> int:
    """Return (compressed_size % 991) * 6500 + decompressed_size * 235 + file_size * 238."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 991) * 6500 + ds * 235 + fs * 238


def zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240(file_path: "str | Path") -> int:
    """Return (compressed_size % 997) * 6600 + decompressed_size * 237 + file_size * 240."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 997) * 6600 + ds * 237 + fs * 240


def zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242(file_path: "str | Path") -> int:
    """Return (compressed_size % 1009) * 6700 + decompressed_size * 239 + file_size * 242."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1009) * 6700 + ds * 239 + fs * 242


def zst_compressed_mod_1013_times_6800_plus_decompressed_times_241_plus_file_size_times_244(file_path: "str | Path") -> int:
    """Return (compressed_size % 1013) * 6800 + decompressed_size * 241 + file_size * 244."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1013) * 6800 + ds * 241 + fs * 244


def zst_compressed_mod_1019_times_6900_plus_decompressed_times_243_plus_file_size_times_246(file_path: "str | Path") -> int:
    """Return (compressed_size % 1019) * 6900 + decompressed_size * 243 + file_size * 246."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1019) * 6900 + ds * 243 + fs * 246


def zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(file_path: "str | Path") -> int:
    """Return (compressed_size % 1021) * 7000 + decompressed_size * 245 + file_size * 248."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1021) * 7000 + ds * 245 + fs * 248


def zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(file_path: "str | Path") -> int:
    """Return (compressed_size % 1031) * 7100 + decompressed_size * 247 + file_size * 250."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1031) * 7100 + ds * 247 + fs * 250


def zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(file_path: "str | Path") -> int:
    """Return (compressed_size % 1021) * 7000 + decompressed_size * 245 + file_size * 248."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1021) * 7000 + ds * 245 + fs * 248


def zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(file_path: "str | Path") -> int:
    """Return (compressed_size % 1031) * 7100 + decompressed_size * 247 + file_size * 250."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1031) * 7100 + ds * 247 + fs * 250


def zst_compressed_mod_1033_times_7200_plus_decompressed_times_249_plus_file_size_times_252(file_path: "str | Path") -> int:
    """Return (compressed_size % 1033) * 7200 + decompressed_size * 249 + file_size * 252."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1033) * 7200 + ds * 249 + fs * 252


def zst_compressed_mod_1039_times_7300_plus_decompressed_times_251_plus_file_size_times_254(file_path: "str | Path") -> int:
    """Return (compressed_size % 1039) * 7300 + decompressed_size * 251 + file_size * 254."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1039) * 7300 + ds * 251 + fs * 254


def zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(file_path: "str | Path") -> int:
    """Return (compressed_size % 1049) * 7400 + decompressed_size * 253 + file_size * 256."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1049) * 7400 + ds * 253 + fs * 256


def zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(file_path: "str | Path") -> int:
    """Return (compressed_size % 1051) * 7500 + decompressed_size * 255 + file_size * 258."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1051) * 7500 + ds * 255 + fs * 258


def zst_compressed_mod_1049_times_7400_plus_decompressed_times_253_plus_file_size_times_256(file_path):
    """Return (compressed_size % 1049) * 7400 + decompressed_size * 253 + file_size * 256."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1049) * 7400 + ds * 253 + fs * 256


def zst_compressed_mod_1051_times_7500_plus_decompressed_times_255_plus_file_size_times_258(file_path):
    """Return (compressed_size % 1051) * 7500 + decompressed_size * 255 + file_size * 258."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1051) * 7500 + ds * 255 + fs * 258


def zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(file_path: "str | Path") -> int:
    """Return (compressed_size % 1061) * 7600 + decompressed_size * 257 + file_size * 260."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1061) * 7600 + ds * 257 + fs * 260


def zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(file_path: "str | Path") -> int:
    """Return (compressed_size % 1063) * 7700 + decompressed_size * 259 + file_size * 262."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1063) * 7700 + ds * 259 + fs * 262


def zst_compressed_mod_1061_times_7600_plus_decompressed_times_257_plus_file_size_times_260(file_path):
    """Return (compressed_size % 1061) * 7600 + decompressed_size * 257 + file_size * 260."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1061) * 7600 + ds * 257 + fs * 260


def zst_compressed_mod_1063_times_7700_plus_decompressed_times_259_plus_file_size_times_262(file_path):
    """Return (compressed_size % 1063) * 7700 + decompressed_size * 259 + file_size * 262."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1063) * 7700 + ds * 259 + fs * 262


def zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(file_path: "str | Path") -> int:
    """Return (compressed_size % 1069) * 7800 + decompressed_size * 261 + file_size * 264."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1069) * 7800 + ds * 261 + fs * 264


def zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(file_path: "str | Path") -> int:
    """Return (compressed_size % 1087) * 7900 + decompressed_size * 263 + file_size * 266."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1087) * 7900 + ds * 263 + fs * 266


def zst_compressed_mod_1069_times_7800_plus_decompressed_times_261_plus_file_size_times_264(file_path):
    """Return (compressed_size % 1069) * 7800 + decompressed_size * 261 + file_size * 264."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1069) * 7800 + ds * 261 + fs * 264


def zst_compressed_mod_1087_times_7900_plus_decompressed_times_263_plus_file_size_times_266(file_path):
    """Return (compressed_size % 1087) * 7900 + decompressed_size * 263 + file_size * 266."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1087) * 7900 + ds * 263 + fs * 266


def zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(file_path: "str | Path") -> int:
    """Return (compressed_size % 1091) * 8000 + decompressed_size * 265 + file_size * 268."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1091) * 8000 + ds * 265 + fs * 268


def zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(file_path: "str | Path") -> int:
    """Return (compressed_size % 1093) * 8100 + decompressed_size * 267 + file_size * 270."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1093) * 8100 + ds * 267 + fs * 270


def zst_compressed_mod_1091_times_8000_plus_decompressed_times_265_plus_file_size_times_268(file_path):
    """Return (compressed_size % 1091) * 8000 + decompressed_size * 265 + file_size * 268."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1091) * 8000 + ds * 265 + fs * 268


def zst_compressed_mod_1093_times_8100_plus_decompressed_times_267_plus_file_size_times_270(file_path):
    """Return (compressed_size % 1093) * 8100 + decompressed_size * 267 + file_size * 270."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1093) * 8100 + ds * 267 + fs * 270


def zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(file_path):
    """Return (compressed_size % 1097) * 8200 + decompressed_size * 269 + file_size * 272."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1097) * 8200 + ds * 269 + fs * 272


def zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(file_path):
    """Return (compressed_size % 1103) * 8300 + decompressed_size * 271 + file_size * 274."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1103) * 8300 + ds * 271 + fs * 274


def zst_compressed_mod_1097_times_8200_plus_decompressed_times_269_plus_file_size_times_272(file_path):
    """Return (compressed_size % 1097) * 8200 + decompressed_size * 269 + file_size * 272."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1097) * 8200 + ds * 269 + fs * 272


def zst_compressed_mod_1103_times_8300_plus_decompressed_times_271_plus_file_size_times_274(file_path):
    """Return (compressed_size % 1103) * 8300 + decompressed_size * 271 + file_size * 274."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1103) * 8300 + ds * 271 + fs * 274


def zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(file_path):
    """Return (compressed_size % 1109) * 8400 + decompressed_size * 273 + file_size * 276."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1109) * 8400 + ds * 273 + fs * 276


def zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(file_path):
    """Return (compressed_size % 1117) * 8500 + decompressed_size * 275 + file_size * 278."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1117) * 8500 + ds * 275 + fs * 278


def zst_compressed_mod_1109_times_8400_plus_decompressed_times_273_plus_file_size_times_276(file_path):
    """Return (compressed_size % 1109) * 8400 + decompressed_size * 273 + file_size * 276."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1109) * 8400 + ds * 273 + fs * 276


def zst_compressed_mod_1117_times_8500_plus_decompressed_times_275_plus_file_size_times_278(file_path):
    """Return (compressed_size % 1117) * 8500 + decompressed_size * 275 + file_size * 278."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1117) * 8500 + ds * 275 + fs * 278


def zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(file_path):
    """Return (compressed_size % 1123) * 8600 + decompressed_size * 277 + file_size * 280."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1123) * 8600 + ds * 277 + fs * 280


def zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(file_path):
    """Return (compressed_size % 1129) * 8700 + decompressed_size * 279 + file_size * 282."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1129) * 8700 + ds * 279 + fs * 282


def zst_compressed_mod_1123_times_8600_plus_decompressed_times_277_plus_file_size_times_280(file_path):
    """Return (compressed_size % 1123) * 8600 + decompressed_size * 277 + file_size * 280."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1123) * 8600 + ds * 277 + fs * 280


def zst_compressed_mod_1129_times_8700_plus_decompressed_times_279_plus_file_size_times_282(file_path):
    """Return (compressed_size % 1129) * 8700 + decompressed_size * 279 + file_size * 282."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1129) * 8700 + ds * 279 + fs * 282


def zst_compressed_mod_1151_times_8800_plus_decompressed_times_281_plus_file_size_times_284(file_path):
    """Return (compressed_size % 1151) * 8800 + decompressed_size * 281 + file_size * 284."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1151) * 8800 + ds * 281 + fs * 284


def zst_compressed_mod_1153_times_8900_plus_decompressed_times_283_plus_file_size_times_286(file_path):
    """Return (compressed_size % 1153) * 8900 + decompressed_size * 283 + file_size * 286."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1153) * 8900 + ds * 283 + fs * 286


def zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(file_path):
    """Return (compressed_size % 1163) * 9000 + decompressed_size * 285 + file_size * 288."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1163) * 9000 + ds * 285 + fs * 288


def zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(file_path):
    """Return (compressed_size % 1171) * 9100 + decompressed_size * 287 + file_size * 290."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1171) * 9100 + ds * 287 + fs * 290


def zst_compressed_mod_1163_times_9000_plus_decompressed_times_285_plus_file_size_times_288(file_path):
    """Return (compressed_size % 1163) * 9000 + decompressed_size * 285 + file_size * 288."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1163) * 9000 + ds * 285 + fs * 288


def zst_compressed_mod_1171_times_9100_plus_decompressed_times_287_plus_file_size_times_290(file_path):
    """Return (compressed_size % 1171) * 9100 + decompressed_size * 287 + file_size * 290."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1171) * 9100 + ds * 287 + fs * 290


def zst_compressed_mod_1181_times_9200_plus_decompressed_times_289_plus_file_size_times_292(file_path):
    """Return (compressed_size % 1181) * 9200 + decompressed_size * 289 + file_size * 292."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1181) * 9200 + ds * 289 + fs * 292


def zst_compressed_mod_1187_times_9300_plus_decompressed_times_291_plus_file_size_times_294(file_path):
    """Return (compressed_size % 1187) * 9300 + decompressed_size * 291 + file_size * 294."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1187) * 9300 + ds * 291 + fs * 294


def zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296(file_path):
    """Return (compressed_size % 1193) * 9400 + decompressed_size * 293 + file_size * 296."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1193) * 9400 + ds * 293 + fs * 296


def zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298(file_path):
    """Return (compressed_size % 1201) * 9500 + decompressed_size * 295 + file_size * 298."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1201) * 9500 + ds * 295 + fs * 298


def zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300(file_path):
    """Return (compressed_size % 1213) * 9600 + decompressed_size * 297 + file_size * 300."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1213) * 9600 + ds * 297 + fs * 300


def zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302(file_path):
    """Return (compressed_size % 1217) * 9700 + decompressed_size * 299 + file_size * 302."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1217) * 9700 + ds * 299 + fs * 302


def zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304(file_path):
    """Return (compressed_size % 1223) * 9800 + decompressed_size * 301 + file_size * 304."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1223) * 9800 + ds * 301 + fs * 304


def zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306(file_path):
    """Return (compressed_size % 1229) * 9900 + decompressed_size * 303 + file_size * 306."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1229) * 9900 + ds * 303 + fs * 306


def zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308(file_path):
    """Return (compressed_size % 1231) * 10000 + decompressed_size * 305 + file_size * 308."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1231) * 10000 + ds * 305 + fs * 308


def zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310(file_path):
    """Return (compressed_size % 1237) * 10100 + decompressed_size * 307 + file_size * 310."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1237) * 10100 + ds * 307 + fs * 310


def zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312(file_path):
    """Return (compressed_size % 1249) * 10200 + decompressed_size * 309 + file_size * 312."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1249) * 10200 + ds * 309 + fs * 312


def zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314(file_path):
    """Return (compressed_size % 1259) * 10300 + decompressed_size * 311 + file_size * 314."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1259) * 10300 + ds * 311 + fs * 314


def zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316(file_path):
    """Return (compressed_size % 1277) * 10400 + decompressed_size * 313 + file_size * 316."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1277) * 10400 + ds * 313 + fs * 316


def zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318(file_path):
    """Return (compressed_size % 1279) * 10500 + decompressed_size * 315 + file_size * 318."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1279) * 10500 + ds * 315 + fs * 318


def zst_compressed_mod_1283_times_10600_plus_decompressed_times_317_plus_file_size_times_320(file_path):
    """Return (compressed_size % 1283) * 10600 + decompressed_size * 317 + file_size * 320."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1283) * 10600 + ds * 317 + fs * 320


def zst_compressed_mod_1289_times_10700_plus_decompressed_times_319_plus_file_size_times_322(file_path):
    """Return (compressed_size % 1289) * 10700 + decompressed_size * 319 + file_size * 322."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1289) * 10700 + ds * 319 + fs * 322


def zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324(file_path):
    """Return (compressed_size % 1291) * 10800 + decompressed_size * 321 + file_size * 324."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1291) * 10800 + ds * 321 + fs * 324


def zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326(file_path):
    """Return (compressed_size % 1297) * 10900 + decompressed_size * 323 + file_size * 326."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1297) * 10900 + ds * 323 + fs * 326


def zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328(file_path):
    """Return (compressed_size % 1301) * 11000 + decompressed_size * 325 + file_size * 328."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1301) * 11000 + ds * 325 + fs * 328


def zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330(file_path):
    """Return (compressed_size % 1303) * 11100 + decompressed_size * 327 + file_size * 330."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1303) * 11100 + ds * 327 + fs * 330


def zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332(file_path):
    """Return (compressed_size % 1307) * 11200 + decompressed_size * 329 + file_size * 332."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1307) * 11200 + ds * 329 + fs * 332


def zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334(file_path):
    """Return (compressed_size % 1319) * 11300 + decompressed_size * 331 + file_size * 334."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1319) * 11300 + ds * 331 + fs * 334


def zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(file_path):
    """Return (compressed_size % 1321) * 11400 + decompressed_size * 333 + file_size * 336."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1321) * 11400 + ds * 333 + fs * 336


def zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(file_path):
    """Return (compressed_size % 1327) * 11500 + decompressed_size * 335 + file_size * 338."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1327) * 11500 + ds * 335 + fs * 338


def zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(file_path):
    """Return (compressed_size % 1321) * 11400 + decompressed_size * 333 + file_size * 336."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1321) * 11400 + ds * 333 + fs * 336


def zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(file_path):
    """Return (compressed_size % 1327) * 11500 + decompressed_size * 335 + file_size * 338."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1327) * 11500 + ds * 335 + fs * 338


def zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(file_path):
    """Return (compressed_size % 1361) * 11600 + decompressed_size * 337 + file_size * 340."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1361) * 11600 + ds * 337 + fs * 340


def zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(file_path):
    """Return (compressed_size % 1367) * 11700 + decompressed_size * 339 + file_size * 342."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1367) * 11700 + ds * 339 + fs * 342


def zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(file_path):
    """Return (compressed_size % 1361) * 11600 + decompressed_size * 337 + file_size * 340."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1361) * 11600 + ds * 337 + fs * 340


def zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(file_path):
    """Return (compressed_size % 1367) * 11700 + decompressed_size * 339 + file_size * 342."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1367) * 11700 + ds * 339 + fs * 342

def zst_compressed_mod_1373_times_11800_plus_decompressed_times_341_plus_file_size_times_344(file_path):
    """Return (compressed_size % 1373) * 11800 + decompressed_size * 341 + file_size * 344."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1373) * 11800 + ds * 341 + fs * 344

def zst_compressed_mod_1381_times_11900_plus_decompressed_times_343_plus_file_size_times_346(file_path):
    """Return (compressed_size % 1381) * 11900 + decompressed_size * 343 + file_size * 346."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1381) * 11900 + ds * 343 + fs * 346

def zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348(file_path):
    """Return (compressed_size % 1399) * 12000 + decompressed_size * 345 + file_size * 348."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1399) * 12000 + ds * 345 + fs * 348

def zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350(file_path):
    """Return (compressed_size % 1409) * 12100 + decompressed_size * 347 + file_size * 350."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1409) * 12100 + ds * 347 + fs * 350

def zst_compressed_mod_1423_times_12200_plus_decompressed_times_349_plus_file_size_times_352(file_path):
    """Return (compressed_size % 1423) * 12200 + decompressed_size * 349 + file_size * 352."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1423) * 12200 + ds * 349 + fs * 352

def zst_compressed_mod_1427_times_12300_plus_decompressed_times_351_plus_file_size_times_354(file_path):
    """Return (compressed_size % 1427) * 12300 + decompressed_size * 351 + file_size * 354."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1427) * 12300 + ds * 351 + fs * 354

def zst_compressed_mod_1429_times_12400_plus_decompressed_times_353_plus_file_size_times_356(file_path):
    """Return (compressed_size % 1429) * 12400 + decompressed_size * 353 + file_size * 356."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1429) * 12400 + ds * 353 + fs * 356

def zst_compressed_mod_1433_times_12500_plus_decompressed_times_355_plus_file_size_times_358(file_path):
    """Return (compressed_size % 1433) * 12500 + decompressed_size * 355 + file_size * 358."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1433) * 12500 + ds * 355 + fs * 358

def zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360(file_path):
    """Return (compressed_size % 1439) * 12600 + decompressed_size * 357 + file_size * 360."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1439) * 12600 + ds * 357 + fs * 360

def zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362(file_path):
    """Return (compressed_size % 1447) * 12700 + decompressed_size * 359 + file_size * 362."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1447) * 12700 + ds * 359 + fs * 362

def zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364(file_path):
    """Return (compressed_size % 1451) * 12800 + decompressed_size * 361 + file_size * 364."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1451) * 12800 + ds * 361 + fs * 364

def zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366(file_path):
    """Return (compressed_size % 1453) * 12900 + decompressed_size * 363 + file_size * 366."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1453) * 12900 + ds * 363 + fs * 366

def zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368(file_path):
    """Return (compressed_size % 1459) * 13000 + decompressed_size * 365 + file_size * 368."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1459) * 13000 + ds * 365 + fs * 368

def zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370(file_path):
    """Return (compressed_size % 1471) * 13100 + decompressed_size * 367 + file_size * 370."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1471) * 13100 + ds * 367 + fs * 370

def zst_compressed_mod_1481_times_13200_plus_decompressed_times_369_plus_file_size_times_372(file_path):
    """Return (compressed_size % 1481) * 13200 + decompressed_size * 369 + file_size * 372."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1481) * 13200 + ds * 369 + fs * 372

def zst_compressed_mod_1483_times_13300_plus_decompressed_times_371_plus_file_size_times_374(file_path):
    """Return (compressed_size % 1483) * 13300 + decompressed_size * 371 + file_size * 374."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1483) * 13300 + ds * 371 + fs * 374

def zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376(file_path):
    """Return (compressed_size % 1487) * 13400 + decompressed_size * 373 + file_size * 376."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1487) * 13400 + ds * 373 + fs * 376

def zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378(file_path):
    """Return (compressed_size % 1489) * 13500 + decompressed_size * 375 + file_size * 378."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1489) * 13500 + ds * 375 + fs * 378

def zst_compressed_mod_1493_times_13600_plus_decompressed_times_377_plus_file_size_times_380(file_path):
    """Return (compressed_size % 1493) * 13600 + decompressed_size * 377 + file_size * 380."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1493) * 13600 + ds * 377 + fs * 380

def zst_compressed_mod_1499_times_13700_plus_decompressed_times_379_plus_file_size_times_382(file_path):
    """Return (compressed_size % 1499) * 13700 + decompressed_size * 379 + file_size * 382."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1499) * 13700 + ds * 379 + fs * 382

def zst_compressed_mod_1511_times_13800_plus_decompressed_times_381_plus_file_size_times_384(file_path):
    """Return (compressed_size % 1511) * 13800 + decompressed_size * 381 + file_size * 384."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1511) * 13800 + ds * 381 + fs * 384

def zst_compressed_mod_1523_times_13900_plus_decompressed_times_383_plus_file_size_times_386(file_path):
    """Return (compressed_size % 1523) * 13900 + decompressed_size * 383 + file_size * 386."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1523) * 13900 + ds * 383 + fs * 386

def zst_compressed_mod_1531_times_14000_plus_decompressed_times_385_plus_file_size_times_388(file_path):
    """Return (compressed_size % 1531) * 14000 + decompressed_size * 385 + file_size * 388."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1531) * 14000 + ds * 385 + fs * 388

def zst_compressed_mod_1543_times_14100_plus_decompressed_times_387_plus_file_size_times_390(file_path):
    """Return (compressed_size % 1543) * 14100 + decompressed_size * 387 + file_size * 390."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1543) * 14100 + ds * 387 + fs * 390

def zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392(file_path):
    """Return (compressed_size % 1549) * 14200 + decompressed_size * 389 + file_size * 392."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1549) * 14200 + ds * 389 + fs * 392

def zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394(file_path):
    """Return (compressed_size % 1553) * 14300 + decompressed_size * 391 + file_size * 394."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1553) * 14300 + ds * 391 + fs * 394

def zst_compressed_mod_1559_times_14400_plus_decompressed_times_393_plus_file_size_times_396(file_path):
    """Return (compressed_size % 1559) * 14400 + decompressed_size * 393 + file_size * 396."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1559) * 14400 + ds * 393 + fs * 396

def zst_compressed_mod_1567_times_14500_plus_decompressed_times_395_plus_file_size_times_398(file_path):
    """Return (compressed_size % 1567) * 14500 + decompressed_size * 395 + file_size * 398."""
    cs = zst_compressed_size(file_path)
    ds = zst_decompressed_size(file_path)
    fs = zst_file_size_bytes(file_path)
    return (cs % 1567) * 14500 + ds * 395 + fs * 398
