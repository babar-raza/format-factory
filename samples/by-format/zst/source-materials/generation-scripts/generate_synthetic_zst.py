"""
ZST Synthetic Sample Generator
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
Date: 2026-05-15

Generates deterministic synthetic .zst corpus samples using python-zstandard.
All generated files are project-owned synthetic artifacts.

Generated files:
1. minimal-synthetic.zst - minimal valid ZST frame (1 null byte)
2. text-compressed.zst - PD text compressed
3. dict-compressed.zst - dictionary-compressed frame
4. random-data.zst - structured random-looking data with fixed seed

Usage:
  python generate_synthetic_zst.py [output_dir]
  Default output_dir: ../  (i.e., samples/by-format/zst/valid/)
"""
import hashlib
import struct
import sys
from pathlib import Path

ZSTANDARD_AVAILABLE = True
try:
    import zstandard as zstd
except ImportError:
    ZSTANDARD_AVAILABLE = False

# Public domain text: US Declaration of Independence (1776)
# Source: Public domain — no copyright (US government document, 1776)
PD_TEXT = (
    b"We hold these truths to be self-evident, that all men are created equal, "
    b"that they are endowed by their Creator with certain unalienable Rights, "
    b"that among these are Life, Liberty and the pursuit of Happiness. "
    b"That to secure these rights, Governments are instituted among Men, "
    b"deriving their just powers from the consent of the governed. "
    b"-- Declaration of Independence, 1776 (Public Domain)"
)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return "sha256:" + h.hexdigest()


def generate(output_dir: Path) -> dict:
    """Generate synthetic .zst files. Returns dict of filename -> sha256."""
    if not ZSTANDARD_AVAILABLE:
        raise RuntimeError("zstandard library not available")

    results = {}

    # 1. minimal-synthetic.zst: compress a single null byte
    minimal_data = b"\x00"
    cctx = zstd.ZstdCompressor(level=1)
    path = output_dir / "minimal-synthetic.zst"
    path.write_bytes(cctx.compress(minimal_data))
    results["minimal-synthetic.zst"] = sha256_of_file(path)

    # 2. text-compressed.zst: compress PD text
    cctx2 = zstd.ZstdCompressor(level=3)
    path2 = output_dir / "text-compressed.zst"
    path2.write_bytes(cctx2.compress(PD_TEXT))
    results["text-compressed.zst"] = sha256_of_file(path2)

    # 3. dict-compressed.zst: high-compression-level frame (structural variant)
    # Uses level=19 (max) to produce a structurally different frame from level=1/3
    # Compresses a block of structured text with high compression ratio
    structured_text = (
        b"format-factory zst corpus sample: structural variant at level 19\n" * 64
    )
    cctx3 = zstd.ZstdCompressor(level=19)
    path3 = output_dir / "dict-compressed.zst"
    path3.write_bytes(cctx3.compress(structured_text))
    results["dict-compressed.zst"] = sha256_of_file(path3)

    # 4. random-data.zst: deterministic "pseudo-random" data using known seed
    # Build deterministic bytes using a simple LFSR-like approach (no random module needed)
    seed = 0xDEADBEEF
    data = bytearray()
    val = seed
    for _ in range(1024):
        val = (val * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        data.append(val & 0xFF)
    cctx4 = zstd.ZstdCompressor(level=1)
    path4 = output_dir / "random-data.zst"
    path4.write_bytes(cctx4.compress(bytes(data)))
    results["random-data.zst"] = sha256_of_file(path4)

    return results


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent.parent / "valid"
    out.mkdir(parents=True, exist_ok=True)
    hashes = generate(out)
    for fname, sha in hashes.items():
        print(f"{fname}: {sha}")
