"""
ZST Corpus Validator — Gate 4 Prototype
Validates all corpus samples from Gate 3 against the parsing strategy.

STATUS: PROTOTYPE — NON-PRODUCTION
Gate 4 planning/validation artifact only.

Expected corpus layout:
  samples/by-format/zst/valid/     — 8 valid samples
  samples/by-format/zst/invalid/   — 3 invalid samples

Validation:
  valid samples  → decompress without error; frame header readable
  invalid samples → raise ZstdError during decompression
  synthetic valid → round-trip (decompress original, compress synthetic, re-decompress)
"""

from __future__ import annotations
import sys
import pathlib
import hashlib

_HERE = pathlib.Path(__file__).parent
REPO_ROOT = _HERE.parent.parent.parent
sys.path.insert(0, str(_HERE))

from frame_header import parse_frame_header, ZSTD_MAGIC

VALID_DIR = REPO_ROOT / "samples" / "by-format" / "zst" / "valid"
INVALID_DIR = REPO_ROOT / "samples" / "by-format" / "zst" / "invalid"

VALID_FILES = [
    "block-128k.zst",
    "dict-compressed.zst",
    "empty-block.zst",
    "minimal-synthetic.zst",
    "random-data.zst",
    "rle-first-block.zst",
    "text-compressed.zst",
    "zeroSeq_2B.zst",
]

INVALID_FILES = [
    "off0.bin.zst",
    "truncated_huff_state.zst",
    "zeroSeq_extraneous.zst",
]

# Synthetic payloads for round-trip test
SYNTHETIC_PAYLOADS = [
    b"Hello, Zstandard world!",
    b"" * 0,  # empty
    b"A" * 1000,  # RLE-friendly
    b"\x00\x01\x02\x03" * 256,  # pattern
]


def _import_zstd():
    try:
        import zstandard
        return zstandard
    except ImportError:
        return None


def validate_valid_samples(zstd) -> list[dict]:
    results = []
    for fname in VALID_FILES:
        path = VALID_DIR / fname
        r = {"file": fname, "exists": path.exists(), "magic_ok": False,
             "decompressed": False, "size": None, "error": None}

        if not path.exists():
            r["error"] = "file not found"
            results.append(r)
            continue

        raw = path.read_bytes()

        # Check magic
        if raw[:4] == ZSTD_MAGIC:
            r["magic_ok"] = True
        else:
            # Some corpus files may be skippable frames or have no Content_Size
            info = parse_frame_header(raw)
            r["magic_ok"] = info.is_zstandard_frame or info.is_skippable_frame

        # Decompress
        if zstd is not None:
            try:
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(raw) as reader:
                    data = reader.read()
                r["decompressed"] = True
                r["size"] = len(data)
                r["sha256"] = hashlib.sha256(data).hexdigest()
            except zstd.ZstdError as e:
                r["error"] = str(e)
        else:
            r["error"] = "zstandard not available"

        results.append(r)
    return results


def validate_invalid_samples(zstd) -> list[dict]:
    results = []
    for fname in INVALID_FILES:
        path = INVALID_DIR / fname
        r = {"file": fname, "exists": path.exists(),
             "correctly_rejected": False, "error_message": None}

        if not path.exists():
            r["error_message"] = "file not found"
            results.append(r)
            continue

        if zstd is None:
            r["error_message"] = "zstandard not available"
            results.append(r)
            continue

        raw = path.read_bytes()
        try:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(raw) as reader:
                reader.read()
            # Should not reach here
            r["error_message"] = "unexpected: decompression succeeded (should have failed)"
        except zstd.ZstdError as e:
            r["correctly_rejected"] = True
            r["error_message"] = str(e)
        except Exception as e:
            # Non-ZstdError means unexpected failure mode
            r["error_message"] = f"unexpected error type: {type(e).__name__}: {e}"

        results.append(r)
    return results


def validate_round_trips(zstd) -> list[dict]:
    results = []
    if zstd is None:
        return [{"payload_index": i, "round_trip": False, "error": "zstandard not available"}
                for i in range(len(SYNTHETIC_PAYLOADS))]

    cctx = zstd.ZstdCompressor(level=1)
    dctx = zstd.ZstdDecompressor()

    for i, payload in enumerate(SYNTHETIC_PAYLOADS):
        r = {"payload_index": i, "original_size": len(payload),
             "round_trip": False, "error": None}
        try:
            compressed = cctx.compress(payload)
            with dctx.stream_reader(compressed) as reader:
                decompressed = reader.read()
            if decompressed == payload:
                r["round_trip"] = True
                r["compressed_size"] = len(compressed)
            else:
                r["error"] = "round-trip mismatch"
        except Exception as e:
            r["error"] = str(e)
        results.append(r)
    return results


def main() -> int:
    print("=== ZST Corpus Validation — Gate 4 Prototype ===\n")

    zstd = _import_zstd()
    if zstd is None:
        print("WARNING: python-zstandard not available. Decompression tests will be skipped.")

    passed = 0
    failed = 0

    print("--- Valid Samples ---")
    valid_results = validate_valid_samples(zstd)
    for r in valid_results:
        ok = r["decompressed"] and r["exists"]
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        size_str = f"  {r['size']} decompressed bytes" if r["size"] is not None else ""
        err_str = f"  ERROR: {r['error']}" if r["error"] else ""
        print(f"  [{status}] {r['file']}{size_str}{err_str}")

    print("\n--- Invalid Samples ---")
    invalid_results = validate_invalid_samples(zstd)
    for r in invalid_results:
        ok = r["correctly_rejected"] and r["exists"]
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {r['file']}  [{r['error_message']}]")

    print("\n--- Round-Trip Tests ---")
    rt_results = validate_round_trips(zstd)
    for r in rt_results:
        ok = r["round_trip"]
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        size_str = f"  {r['original_size']} -> {r.get('compressed_size', '?')} bytes" if ok else ""
        err_str = f"  {r['error']}" if r.get("error") else ""
        print(f"  [{status}] payload[{r['payload_index']}]{size_str}{err_str}")

    print(f"\n=== Results: {passed} PASS, {failed} FAIL ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
