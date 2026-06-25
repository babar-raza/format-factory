"""Clean consumer proof: ZST compress -> inspect -> decompress -> verify.

ZST (Zstandard) is a compression format — the "mutation" flow is:
  compress string -> save .zst file -> inspect via ZstDocument
  -> decompress -> verify original content.

Steps:
  1. Compress a known string to ZST bytes
  2. Save .zst file
  3. Inspect: ZstDocument, compressed_size, frame_count
  4. Decompress and verify content matches original

DOGFOOD CONTRACT:
  - uses `import zst` (installed package, not src/)
  - no src/ path manipulation
  - asserts real semantic result at every boundary

Runnable:
  python examples/python/zst/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import zst as zst_pkg
from zst import compress_string, decompress_to_string, compress_file, ZstDocument

SAMPLE_ZST = _REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "zst"

ORIGINAL_TEXT = "CONSUMER_PROOF: VERIFIED by Format Factory ZST deepening"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"ZST package: {zst_pkg.__file__}")
    print(f"Sample: {SAMPLE_ZST}")
    print()

    # Step 1: Inspect existing ZST file
    doc_sample = ZstDocument.from_file(str(SAMPLE_ZST))
    assert doc_sample.spec_qname == "zst:frame", f"spec_qname={doc_sample.spec_qname!r}"
    print(f"[INSPECT sample] spec_qname={doc_sample.spec_qname}")
    print(f"  compressed_size={doc_sample.compressed_size} bytes, frames={doc_sample.frame_count}")
    assert doc_sample.compressed_size > 0
    assert not doc_sample.is_empty

    # Step 2: Compress string to ZST
    compressed = compress_string(ORIGINAL_TEXT)
    assert isinstance(compressed, bytes), f"Expected bytes, got {type(compressed)}"
    print(f"\n[COMPRESS] '{ORIGINAL_TEXT[:40]}...'")
    print(f"  original={len(ORIGINAL_TEXT.encode())} bytes -> compressed={len(compressed)} bytes")

    out_path = OUTPUT_DIR / "consumer_proof.zst"
    out_path.write_bytes(compressed)
    print(f"  saved to {out_path} ({out_path.stat().st_size} bytes)")

    # Step 3: Inspect compressed file via ZstDocument
    doc2 = ZstDocument.from_file(str(out_path))
    assert doc2.spec_qname == "zst:frame"
    assert doc2.compressed_size == len(compressed)
    assert doc2.frame_count >= 1
    assert not doc2.is_empty
    print(f"\n[INSPECT consumer_proof.zst] compressed_size={doc2.compressed_size}, frames={doc2.frame_count}  OK")
    d = doc2.to_dict()
    print(f"  to_dict keys: {list(d.keys())!r}")

    # Step 4: Decompress and verify
    decompressed = decompress_to_string(compressed)
    assert decompressed == ORIGINAL_TEXT, f"Mismatch: {decompressed!r}"
    print(f"\n[DECOMPRESS] '{decompressed}'  OK")

    # Also verify from file bytes
    raw = out_path.read_bytes()
    decompressed2 = decompress_to_string(raw)
    assert decompressed2 == ORIGINAL_TEXT
    print(f"[FROM FILE] decompress verified from bytes  OK")

    print("\nCONSUMER_PROOF: PASS -- compress -> save -> inspect(ZstDocument) -> decompress -> verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
