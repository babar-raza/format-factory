"""
ZST Probe — Gate 4 Prototype
Decompresses a ZST file using python-zstandard and reports frame metadata.

STATUS: PROTOTYPE — NON-PRODUCTION
NOT for use in src/python/ or src/net/
Gate 4 planning/validation artifact only.

SECURITY WARNING:
- This prototype does NOT limit output size. Do not run on untrusted input.
- See README.md for security notes.
"""

from __future__ import annotations
import sys
import pathlib
from typing import Optional

# Import frame_header from same directory
_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))
from frame_header import parse_frame_header, describe


def _try_import_zstandard():
    """Try to import zstandard library. Returns module or None."""
    try:
        import zstandard  # python-zstandard (BSD-3-Clause)
        return zstandard
    except ImportError:
        return None


def probe(path: pathlib.Path) -> dict:
    """
    Probe a ZST file: extract frame metadata and attempt decompression.

    Returns dict with keys:
      - path: str
      - exists: bool
      - header: FrameHeaderInfo (or None)
      - header_description: str
      - decompressed_size: int (or None)
      - decompressed_sha256: str (or None)
      - decompression_error: str (or None)
      - zstandard_available: bool
    """
    result = {
        "path": str(path),
        "exists": path.exists(),
        "header": None,
        "header_description": "file not found",
        "decompressed_size": None,
        "decompressed_sha256": None,
        "decompression_error": None,
        "zstandard_available": False,
    }

    if not path.exists():
        return result

    raw = path.read_bytes()

    # Parse frame header (pure Python, no dependency)
    info = parse_frame_header(raw)
    result["header"] = info
    result["header_description"] = describe(info)

    # Attempt decompression via python-zstandard
    zstd = _try_import_zstandard()
    result["zstandard_available"] = zstd is not None

    if zstd is not None:
        try:
            dctx = zstd.ZstdDecompressor()
            # Always use stream_reader — handles both with/without Content_Size
            with dctx.stream_reader(raw) as reader:
                decompressed = reader.read()
            result["decompressed_size"] = len(decompressed)
            import hashlib
            result["decompressed_sha256"] = hashlib.sha256(decompressed).hexdigest()
        except zstd.ZstdError as e:
            result["decompression_error"] = str(e)
        except Exception as e:
            result["decompression_error"] = f"unexpected: {type(e).__name__}: {e}"

    return result


def main(paths: list[str]) -> None:
    """CLI entry point: probe each file and print a report."""
    if not paths:
        print("Usage: python zst_probe.py <file.zst> [...]")
        return

    for p in paths:
        path = pathlib.Path(p)
        r = probe(path)
        print(f"\n=== {path.name} ===")
        print(r["header_description"])
        if r["zstandard_available"]:
            if r["decompression_error"]:
                print(f"  decompression: ERROR — {r['decompression_error']}")
            else:
                print(f"  decompressed_size: {r['decompressed_size']} bytes")
                print(f"  decompressed_sha256: {r['decompressed_sha256']}")
        else:
            print("  [zstandard not available — decompression skipped]")


if __name__ == "__main__":
    main(sys.argv[1:])
