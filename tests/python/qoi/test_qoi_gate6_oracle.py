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

    def test_synthetic_op_index_oracle(self):
        """Oracle: OP_INDEX lookup produces correct pixel from hash table."""
        # Pixel (100, 150, 200, 255) hashes to (100*3+150*5+200*7+255*11)%64
        # = (300+750+1400+2805)%64 = 5255%64 = 5255-82*64 = 5255-5248 = 7
        # Encode: OP_RGB (100,150,200), then OP_RGB (10,20,30) [different],
        # then OP_INDEX 7 to recall (100,150,200,255)
        pixel_data = bytes([
            0xFE, 100, 150, 200,   # px0: OP_RGB -> (100,150,200,255)
            0xFE, 10, 20, 30,      # px1: OP_RGB -> (10,20,30,255)
            0x00 | 7,              # px2: OP_INDEX[7] -> (100,150,200,255)
        ])
        path = _make_qoi(3, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (100, 150, 200, 255)
        assert img.pixels[1] == (10, 20, 30, 255)
        assert img.pixels[2] == (100, 150, 200, 255)

    def test_synthetic_op_diff_oracle(self):
        """Oracle: OP_DIFF applies small delta to previous pixel."""
        # Previous pixel after OP_RGB(100,100,100) is (100,100,100,255).
        # OP_DIFF encodes: 0b01_dr_dg_db, each 2-bit with bias +2.
        # Want dr=+1, dg=0, db=-1 -> encoded: (1+2)=3, (0+2)=2, (-1+2)=1
        # byte = 0b01_11_10_01 = 0x79
        pixel_data = bytes([
            0xFE, 100, 100, 100,   # px0: (100,100,100,255)
            0x79,                  # px1: OP_DIFF dr=+1,dg=0,db=-1 -> (101,100,99,255)
        ])
        path = _make_qoi(2, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (100, 100, 100, 255)
        assert img.pixels[1] == (101, 100, 99, 255)

    def test_synthetic_op_luma_oracle(self):
        """Oracle: OP_LUMA applies larger delta via green-channel-centered encoding."""
        # Previous pixel: (100,100,100,255) via OP_RGB.
        # OP_LUMA: byte1 = 0b10_dg+32, byte2 = (dr-dg+8)<<4 | (db-dg+8)
        # Want dg=+5, dr=+3, db=+7.
        # byte1 = 0x80 | (5+32) = 0x80 | 37 = 0xA5
        # dr_dg = dr-dg = 3-5 = -2, encoded = -2+8 = 6
        # db_dg = db-dg = 7-5 = 2, encoded = 2+8 = 10
        # byte2 = (6<<4) | 10 = 0x6A
        pixel_data = bytes([
            0xFE, 100, 100, 100,   # px0: (100,100,100,255)
            0xA5, 0x6A,            # px1: OP_LUMA -> (103,105,107,255)
        ])
        path = _make_qoi(2, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (100, 100, 100, 255)
        assert img.pixels[1] == (103, 105, 107, 255)

    def test_synthetic_multi_row_3x3_oracle(self):
        """Oracle: 3x3 pixel grid with OP_RGB + OP_RUN."""
        # Pixel (80,160,240,255) x9 via OP_RGB + OP_RUN of 8
        pixel_data = bytes([
            0xFE, 80, 160, 240,    # px0: OP_RGB
            0xC7,                  # OP_RUN length=8 (0x3F & 0xC7 = 7, +1 = 8)
        ])
        path = _make_qoi(3, 3, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert len(img.pixels) == 9
        for px in img.pixels:
            assert px == (80, 160, 240, 255)

    def test_synthetic_rgba_varying_alpha_oracle(self):
        """Oracle: RGBA pixels with different alpha values decode correctly."""
        pixel_data = bytes([
            0xFF, 255, 0, 0, 128,  # px0: (255,0,0,128)
            0xFF, 0, 255, 0, 64,   # px1: (0,255,0,64)
            0xFF, 0, 0, 255, 0,    # px2: (0,0,255,0)
        ])
        path = _make_qoi(3, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (255, 0, 0, 128)
        assert img.pixels[1] == (0, 255, 0, 64)
        assert img.pixels[2] == (0, 0, 255, 0)

    def test_synthetic_mixed_chunk_stream_oracle(self):
        """Oracle: Mixed INDEX+DIFF+LUMA+RUN chunks in one image."""
        # px0: OP_RGB (200,100,50,255) — literal
        # px1: OP_DIFF dr=-1,dg=+1,db=0 -> (199,101,50,255)
        #   byte = 0b01_(−1+2)_(+1+2)_(0+2) = 0b01_01_11_10 = 0x5E
        # px2: OP_LUMA dg=+10, dr=+12, db=+8
        #   byte1 = 0x80|(10+32) = 0xAA
        #   dr_dg=12-10=2, db_dg=8-10=-2; byte2=((2+8)<<4)|(-2+8)=(10<<4)|6=0xA6
        #   -> (199+12, 101+10, 50+8, 255) = (211,111,58,255)
        # px3: OP_INDEX for px0 (200,100,50,255)
        #   hash = (200*3+100*5+50*7+255*11)%64 = (600+500+350+2805)%64 = 4255%64
        #   4255/64 = 66*64 + 31 -> idx=31
        #   byte = 0x00|31 = 0x1F
        # px4-px5: OP_RUN length 2 (repeats px3=(200,100,50,255))
        #   byte = 0xC1 (0x3F & 0xC1 = 1, +1 = 2)
        pixel_data = bytes([
            0xFE, 200, 100, 50,    # px0: OP_RGB
            0x5E,                  # px1: OP_DIFF
            0xAA, 0xA6,           # px2: OP_LUMA
            0x1F,                  # px3: OP_INDEX[31]
            0xC1,                  # px4-5: OP_RUN(2)
        ])
        path = _make_qoi(6, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (200, 100, 50, 255)
        assert img.pixels[1] == (199, 101, 50, 255)
        assert img.pixels[2] == (211, 111, 58, 255)
        assert img.pixels[3] == (200, 100, 50, 255)  # INDEX recall
        assert img.pixels[4] == (200, 100, 50, 255)  # RUN
        assert img.pixels[5] == (200, 100, 50, 255)  # RUN

    def test_synthetic_op_diff_wrap_around_oracle(self):
        """Oracle: OP_DIFF wraps around 0/255 boundary correctly."""
        # Previous pixel: (1,1,254,255) via OP_RGB
        # OP_DIFF dr=-2, dg=-2, db=+1 -> (255,255,255,255)
        # encoded: (-2+2)=0, (-2+2)=0, (+1+2)=3 -> 0b01_00_00_11 = 0x43
        pixel_data = bytes([
            0xFE, 1, 1, 254,      # px0: (1,1,254,255)
            0x43,                  # px1: OP_DIFF dr=-2,dg=-2,db=+1 -> (255,255,255,255)
        ])
        path = _make_qoi(2, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (1, 1, 254, 255)
        assert img.pixels[1] == (255, 255, 255, 255)
