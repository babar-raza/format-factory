"""Sprint 268: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod23Times150PlusDecompressedSizeMod80Times40PlusCompressedSizeTimes18:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_23_times_150_plus_decompressed_size_mod_80_times_40_plus_compressed_size_times_18
        return zst_file_size_mod_23_times_150_plus_decompressed_size_mod_80_times_40_plus_compressed_size_times_18

    def test_text_compressed(self): assert self._fn()(TEXT) == 10546
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 1720
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 1270
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 10546
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 10546
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(MINIMAL) > fn(ZEROSEQ)
    def test_zeroseq_smallest(self):
        fn = self._fn(); assert fn(ZEROSEQ) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstMaxByteValueTimes100PlusCompressedSizeMod17Times250PlusFileSizeMod31Times300:
    def _fn(self):
        from src.python.zst import zst_max_byte_value_times_100_plus_compressed_size_mod_17_times_250_plus_file_size_mod_31_times_300
        return zst_max_byte_value_times_100_plus_compressed_size_mod_17_times_250_plus_file_size_mod_31_times_300

    def test_text_compressed(self): assert self._fn()(TEXT) == 19300
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 5500
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 20900
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 19300
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 19300
    def test_zeroseq_largest(self):
        fn = self._fn(); assert fn(ZEROSEQ) > fn(TEXT) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
