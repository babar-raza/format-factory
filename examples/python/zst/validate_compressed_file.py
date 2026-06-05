"""
R100 Example: ZST compress, validate, and decompress workflow.

Demonstrates the ZST codec probe/validate capabilities using
Format Factory's zst_codec library.
"""

import tempfile
from pathlib import Path
from zst.zst_codec import compress_bytes, decompress_bytes, validate_file, ZSTD_MAGIC


def main():
    original = b"Hello from Format Factory ZST example! " * 100
    print(f"Original size: {len(original)} bytes")

    # Compress
    compressed = compress_bytes(original)
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Starts with ZSTD magic: {compressed[:4] == ZSTD_MAGIC}")

    # Write to temp file and validate
    with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
        f.write(compressed)
        tmp = f.name

    try:
        result = validate_file(tmp)
        print(f"Validation result: valid={result['valid']}, exists={result['exists']}")

        # Decompress and verify
        restored = decompress_bytes(compressed)
        print(f"Roundtrip match: {restored == original}")
    finally:
        Path(tmp).unlink(missing_ok=True)

    print("Done.")


if __name__ == "__main__":
    main()
