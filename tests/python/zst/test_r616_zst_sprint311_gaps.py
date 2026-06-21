"""Sprint 311: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZERO = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod137Times600PlusDecompressedSizeMod1900PlusMaxByteValueTimes120:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120
        return zst_file_size_mod_137_times_600_plus_decompressed_size_mod_1900_plus_max_byte_value_times_120

    def test_text_compressed(self): assert self._fn()(TEXT) == 95910
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 6001
    def test_zero_seq(self): assert self._fn()(ZERO) == 28693
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 95910
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 95910
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))


class TestZstCompressedSizeMod139Times550PlusDecompressedSizeMod2000PlusMinByteValueTimes1100:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100
        return zst_compressed_size_mod_139_times_550_plus_decompressed_size_mod_2000_plus_min_byte_value_times_1100

    def test_text_compressed(self): assert self._fn()(TEXT) == 108740
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 5501
    def test_zero_seq(self): assert self._fn()(ZERO) == 24763
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 108740
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 108740
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))
