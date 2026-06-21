"""Sprint 253: ZST analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod19Times200PlusDecompressedSizeMod300PlusMaxByteValueTimes5:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_19_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_5
        return zst_file_size_mod_19_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_5

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 1895

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 2001

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 1783

    def test_returns_int(self):
        assert isinstance(self._fn()(TEXT), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(TEXT)) == 1895

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 1895

    def test_minimal_largest(self):
        fn = self._fn()
        assert fn(MINIMAL) > fn(TEXT) > fn(ZEROSEQ)

    def test_zeroseq_smallest(self):
        fn = self._fn()
        assert fn(ZEROSEQ) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedSizeMod11Times300PlusDecompressedSizeMod400PlusMinByteValueTimes100:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_11_times_300_plus_decompressed_size_mod_400_plus_min_byte_value_times_100
        return zst_compressed_size_mod_11_times_300_plus_decompressed_size_mod_400_plus_min_byte_value_times_100

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 5990

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 3001

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 1913

    def test_returns_int(self):
        assert isinstance(self._fn()(TEXT), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(TEXT)) == 5990

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 5990

    def test_text_largest(self):
        fn = self._fn()
        assert fn(TEXT) > fn(MINIMAL) > fn(ZEROSEQ)

    def test_zeroseq_smallest(self):
        fn = self._fn()
        assert fn(ZEROSEQ) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
