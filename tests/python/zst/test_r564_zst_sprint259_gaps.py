"""Sprint 259: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod31Times200PlusDecompressedTimes11PlusFileSizeTimes15:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15
        return zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15

    def test_text_compressed(self): assert self._fn()(TEXT) == 13170
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 2161
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 5518
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 13170
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 13170
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedTimes5PlusDecompressedMod60Times40PlusFileSizeTimes12:
    def _fn(self):
        from src.python.zst import zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12
        return zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12

    def test_text_compressed(self): assert self._fn()(TEXT) == 5824
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 210
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 945
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 5824
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 5824
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
