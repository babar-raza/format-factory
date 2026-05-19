"""Gate 7 security and fuzz guard tests for QOI parser.

Deterministic malformed input guards. No heavy fuzzing.
"""

import struct
import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from qoi.qoi_parser import (
    QOI_END_MARKER,
    QOI_MAGIC,
    QoiDecodeError,
    QoiError,
    QoiInvalidHeaderError,
    QoiInvalidMagicError,
    QoiSizeError,
    parse_qoi,
    parse_qoi_strict,
)


def _write_tmp(data: bytes) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
    tmp.write(data)
    tmp.close()
    return tmp.name


class TestQoiFuzzGuards:
    """Malformed input guards for QOI parser."""

    def test_empty_file(self):
        path = _write_tmp(b"")
        with pytest.raises(QoiError):
            parse_qoi_strict(path)

    def test_random_bytes(self):
        import random
        random.seed(42)
        data = bytes(random.randint(0, 255) for _ in range(100))
        path = _write_tmp(data)
        result = parse_qoi(path)
        assert result["ok"] is False

    def test_wrong_magic_bytes(self):
        data = b"XXXX" + struct.pack(">II", 1, 1) + bytes([4, 0]) + QOI_END_MARKER
        path = _write_tmp(data)
        with pytest.raises(QoiInvalidMagicError):
            parse_qoi_strict(path)

    def test_truncated_header(self):
        data = QOI_MAGIC + b"\x00\x00"
        path = _write_tmp(data)
        with pytest.raises(QoiDecodeError, match="too short"):
            parse_qoi_strict(path)

    def test_huge_dimensions(self):
        """Dimensions exceeding MAX_DIMENSION should be rejected."""
        data = QOI_MAGIC + struct.pack(">II", 99999, 99999) + bytes([4, 0]) + QOI_END_MARKER
        path = _write_tmp(data)
        with pytest.raises(QoiSizeError):
            parse_qoi_strict(path)

    def test_truncated_pixel_data(self):
        """Header says 2x2 but pixel data is too short."""
        header = QOI_MAGIC + struct.pack(">II", 2, 2) + bytes([4, 0])
        data = header + bytes([0xFE, 10, 20, 30]) + QOI_END_MARKER
        path = _write_tmp(data)
        with pytest.raises(QoiDecodeError):
            parse_qoi_strict(path)

    def test_dict_api_never_raises(self):
        result = parse_qoi("/nonexistent")
        assert isinstance(result, dict)
        assert result["ok"] is False

    def test_all_zeros_file(self):
        """All-zeros file (not valid QOI magic)."""
        path = _write_tmp(b"\x00" * 100)
        result = parse_qoi(path)
        assert result["ok"] is False

    def test_missing_end_marker(self):
        """Valid header + pixel data but no end marker."""
        header = QOI_MAGIC + struct.pack(">II", 1, 1) + bytes([4, 0])
        # OP_RUN for 1 pixel, but no end marker
        data = header + bytes([0xC0])
        path = _write_tmp(data)
        result = parse_qoi(path)
        assert result["ok"] is False
