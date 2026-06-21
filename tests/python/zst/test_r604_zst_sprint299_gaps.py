"""Sprint 299: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZERO = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod97Times600PlusDecompressedSizeMod1100PlusMaxByteValueTimes80:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80
        return zst_file_size_mod_97_times_600_plus_decompressed_size_mod_1100_plus_max_byte_value_times_80

    def test_text_compressed(self): assert self._fn()(TEXT) == 56870
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 6001
    def test_zero_seq(self): assert self._fn()(ZERO) == 24133
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 56870
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 56870
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))


class TestZstCompressedSizeMod101Times350PlusDecompressedSizeMod1200PlusMinByteValueTimes700:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700
        return zst_compressed_size_mod_101_times_350_plus_decompressed_size_mod_1200_plus_min_byte_value_times_700

    def test_text_compressed(self): assert self._fn()(TEXT) == 47290
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 3501
    def test_zero_seq(self): assert self._fn()(ZERO) == 15763
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 47290
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 47290
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))
