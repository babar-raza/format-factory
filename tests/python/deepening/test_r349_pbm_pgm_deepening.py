"""Sprint 139 — PBM bytes_per_pixel/is_all_black, PGM bytes_per_pixel/avg_pixel_value."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.pbm.pbm_parser import pbm_bytes_per_pixel, pbm_is_all_black
from src.python.pgm.pgm_parser import pgm_bytes_per_pixel, pgm_avg_pixel_value

P1 = str(_REPO / "samples/by-format/pbm/valid/1x1-black.pbm")
P2 = str(_REPO / "samples/by-format/pbm/valid/2x2-checker.pbm")
P3 = str(_REPO / "samples/by-format/pbm/valid/3x2-pattern.pbm")
G1 = str(_REPO / "samples/by-format/pgm/valid/1x1-white.pgm")
G2 = str(_REPO / "samples/by-format/pgm/valid/2x2-gradient.pgm")
G3 = str(_REPO / "samples/by-format/pgm/valid/3x1-ramp.pgm")

class TestPbmBytesPerPixel:
    def test_1x1(self):
        assert pbm_bytes_per_pixel(P1) == 12.0
    def test_2x2(self):
        assert pbm_bytes_per_pixel(P2) == 4.75
    def test_3x2(self):
        assert abs(pbm_bytes_per_pixel(P3) - 3.8333) < 0.01
    def test_return_type(self):
        assert isinstance(pbm_bytes_per_pixel(P1), float)
    def test_positive(self):
        assert pbm_bytes_per_pixel(P1) > 0

class TestPbmIsAllBlack:
    def test_1x1(self):
        assert pbm_is_all_black(P1) is True
    def test_2x2(self):
        assert pbm_is_all_black(P2) is False
    def test_3x2(self):
        assert pbm_is_all_black(P3) is False
    def test_return_type(self):
        assert isinstance(pbm_is_all_black(P1), bool)
    def test_consistency(self):
        assert pbm_is_all_black(P1) is True

class TestPgmBytesPerPixel:
    def test_1x1(self):
        assert pgm_bytes_per_pixel(G1) == 19.0
    def test_2x2(self):
        assert pgm_bytes_per_pixel(G2) == 7.25
    def test_3x1(self):
        assert abs(pgm_bytes_per_pixel(G3) - 8.3333) < 0.01
    def test_return_type(self):
        assert isinstance(pgm_bytes_per_pixel(G1), float)
    def test_positive(self):
        assert pgm_bytes_per_pixel(G1) > 0

class TestPgmAvgPixelValue:
    def test_1x1(self):
        assert pgm_avg_pixel_value(G1) == 255.0
    def test_2x2(self):
        assert pgm_avg_pixel_value(G2) == 127.5
    def test_3x1(self):
        assert abs(pgm_avg_pixel_value(G3) - 127.6667) < 0.01
    def test_return_type(self):
        assert isinstance(pgm_avg_pixel_value(G1), float)
    def test_bounded(self):
        assert 0.0 <= pgm_avg_pixel_value(G1) <= 255.0
