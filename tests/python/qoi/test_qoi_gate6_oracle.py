"""Gate 6 deterministic oracle tests for QOI parser.

Oracle strategy: Build QOI files from known pixel data using the spec,
decode them, and compare pixel arrays against expected values.
No external tool dependency.
"""

import struct
import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from qoi.qoi_parser import (
    QOI_END_MARKER,
    QOI_MAGIC,
    parse_qoi_strict,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "qoi"


def _make_qoi(width, height, channels, colorspace, pixel_data):
    header = QOI_MAGIC + struct.pack(">II", width, height) + bytes([channels, colorspace])
    data = header + pixel_data + QOI_END_MARKER
    tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
    tmp.write(data)
    tmp.close()
    return Path(tmp.name)


class TestQoiOracleKnownValues:
    """Deterministic oracle: compare decoded pixels against expected values."""

    def test_known_1x1_red_oracle(self):
        """Oracle: 1x1-red.qoi decodes to exactly (255, 0, 0, 255)."""
        img = parse_qoi_strict(SAMPLES / "valid" / "1x1-red.qoi")
        assert img.pixels[0] == (255, 0, 0, 255)

    def test_known_2x2_black_oracle(self):
        """Oracle: 2x2-black.qoi decodes to 4 black pixels."""
        img = parse_qoi_strict(SAMPLES / "valid" / "2x2-black.qoi")
        assert len(img.pixels) == 4
        for px in img.pixels:
            assert px[0] == 0 and px[1] == 0 and px[2] == 0

    def test_known_4x1_gradient_oracle(self):
        """Oracle: 4x1-gradient.qoi has 4 pixels in sequence."""
        img = parse_qoi_strict(SAMPLES / "valid" / "4x1-gradient.qoi")
        assert len(img.pixels) == 4

    def test_synthetic_op_rgb_oracle(self):
        """Oracle: OP_RGB encodes literal (100, 150, 200)."""
        pixel_data = bytes([0xFE, 100, 150, 200])
        path = _make_qoi(1, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (100, 150, 200, 255)

    def test_synthetic_op_rgba_oracle(self):
        """Oracle: OP_RGBA encodes literal (10, 20, 30, 40)."""
        pixel_data = bytes([0xFF, 10, 20, 30, 40])
        path = _make_qoi(1, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (10, 20, 30, 40)

    def test_synthetic_op_run_oracle(self):
        """Oracle: OP_RUN with length 3 repeats default pixel 3 times."""
        # Default pixel is (0,0,0,255). OP_RUN 0xC2 = run of 3 (bias +1)
        pixel_data = bytes([0xC2])
        path = _make_qoi(3, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert len(img.pixels) == 3
        for px in img.pixels:
            assert px == (0, 0, 0, 255)

    def test_synthetic_2x2_rgb_oracle(self):
        """Oracle: 2x2 with OP_RGB + OP_RUN gives 4 identical pixels."""
        # First pixel via OP_RGB, then run of 3 more
        pixel_data = bytes([0xFE, 50, 100, 150, 0xC2])
        path = _make_qoi(2, 2, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert len(img.pixels) == 4
        for px in img.pixels:
            assert px == (50, 100, 150, 255)
