"""Sprint 305: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZERO = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod109Times500PlusDecompressedSizeMod1500PlusMaxByteValueTimes100:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100
        return zst_file_size_mod_109_times_500_plus_decompressed_size_mod_1500_plus_max_byte_value_times_100

    def test_text_compressed(self): assert self._fn()(TEXT) == 39490
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 5001
    def test_zero_seq(self): assert self._fn()(ZERO) == 23913
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 39490
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 39490
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))


class TestZstCompressedSizeMod113Times450PlusDecompressedSizeMod1600PlusMinByteValueTimes900:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900
        return zst_compressed_size_mod_113_times_450_plus_decompressed_size_mod_1600_plus_min_byte_value_times_900

    def test_text_compressed(self): assert self._fn()(TEXT) == 49890
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 4501
    def test_zero_seq(self): assert self._fn()(ZERO) == 20263
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 49890
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 49890
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))
