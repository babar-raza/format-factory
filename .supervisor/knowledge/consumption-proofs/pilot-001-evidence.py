# Consumption proof: pilot-001
# Task: Add get_frame_type() to ZstDocument
# Knowledge source: KC-PYTHON-001 only (no implementation browsing)
# Verdict: see pilot-001.yaml

# From KC-PYTHON-001 contract:
# - ZST uses path-based variant: __init__(self, path, data=None)
# - Accessor methods return safe defaults on error/out-of-bounds
# - Relative import inside method body (not module level)
# - Return type-coerced result

# Proposed addition to src/python/zst/models.py:

    def get_frame_type(self) -> str:
        """Return the ZST frame type detected from the file header.

        Reads the magic bytes of the stored ZST file path to identify
        whether the frame is a standard frame ('standard') or a skippable
        frame ('skippable'). Returns '' if the file is missing or unreadable.
        """
        # Per KC-PYTHON-001 path-based variant: self._path holds the file path
        try:
            path = self._path
            if not hasattr(self, "_path") or path is None:
                return ""  # safe default
            import pathlib
            p = pathlib.Path(path)
            if not p.exists():
                return ""  # safe default — out-of-bounds per contract
            header = p.read_bytes()[:4]
            # Zstandard magic: 0xFD2FB528 (little-endian) = standard frame
            # Skippable frames: 0x184D2A50..0x184D2A5F
            if header[:4] == b"\x28\xb5\x2f\xfd":
                return str("standard")  # coerce to str per contract
            if header[:2] == b"\x50\x2a" or (len(header) >= 4 and header[0] == 0x50 and (header[3] & 0xF0) == 0x10):
                return str("skippable")
            return str("unknown")  # coerce to str, safe default
        except Exception:
            return ""  # safe default on any error
