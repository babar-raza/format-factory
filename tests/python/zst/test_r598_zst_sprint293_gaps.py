"""Sprint 293: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZERO = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod73Times400PlusDecompressedSizeMod700PlusMaxByteValueTimes60:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60
        return zst_file_size_mod_73_times_400_plus_decompressed_size_mod_700_plus_max_byte_value_times_60

    def test_text_compressed(self): assert self._fn()(TEXT) == 28850
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 4001
    def test_zero_seq(self): assert self._fn()(ZERO) == 16853
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 28850
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 28850
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))


class TestZstCompressedSizeMod79Times250PlusDecompressedSizeMod800PlusMinByteValueTimes500:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500
        return zst_compressed_size_mod_79_times_250_plus_decompressed_size_mod_800_plus_min_byte_value_times_500

    def test_text_compressed(self): assert self._fn()(TEXT) == 25140
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 2501
    def test_zero_seq(self): assert self._fn()(ZERO) == 11263
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZERO)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZERO]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 25140
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 25140
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZERO) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZERO))
