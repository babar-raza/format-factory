"""Sprint 281: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod43Times250PlusDecompressedTimes15PlusFileSizeTimes22:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22
        return zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22

    def test_text_compressed(self): assert self._fn()(TEXT) == 15334
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 2735
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 6995
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 15334
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 15334
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedTimes7PlusDecompressedMod80Times70PlusFileSizeTimes16:
    def _fn(self):
        from src.python.zst import zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16
        return zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16

    def test_text_compressed(self): assert self._fn()(TEXT) == 11156
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 300
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 1485
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 11156
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 11156
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
