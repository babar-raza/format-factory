"""ZST D6→D7 install proof: verify module importability and core API functionality."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

zstandard = pytest.importorskip("zstandard", reason="zstandard library not installed")


class TestZstInstalledD7Proof:
    def test_zst_module_importable(self):
        """import src.python.zst succeeds."""
        import src.python.zst as zst_mod
        assert zst_mod is not None
        assert hasattr(zst_mod, "compress_bytes")
        assert hasattr(zst_mod, "decompress_bytes")
        assert hasattr(zst_mod, "probe_frame")

    def test_zst_version_set(self):
        """__version__ is not None and not '0.0.0'."""
        from src.python.zst import __version__
        assert __version__ is not None
        assert __version__ != "0.0.0"
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_zst_compress_bytes_works(self):
        """compress_bytes(b"hello world") returns bytes."""
        from src.python.zst import compress_bytes
        result = compress_bytes(b"hello world")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_zst_decompress_roundtrip(self):
        """compress then decompress matches input."""
        from src.python.zst import compress_bytes, decompress_bytes
        original = b"The quick brown fox jumps over the lazy dog"
        compressed = compress_bytes(original)
        decompressed = decompress_bytes(compressed)
        assert decompressed == original

    def test_zst_probe_frame_works(self):
        """probe_frame on compressed data returns dict with frame info."""
        from src.python.zst import compress_bytes, probe_frame
        compressed = compress_bytes(b"test data for probing")
        info = probe_frame(compressed)
        assert isinstance(info, dict)
        assert "frame_content_size" in info or "content_size" in info or len(info) > 0
