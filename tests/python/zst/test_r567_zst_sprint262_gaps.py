"""Sprint 262: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod13Times300PlusDecompressedSizeMod100PlusMaxByteValueTimes20:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20
        return zst_file_size_mod_13_times_300_plus_decompressed_size_mod_100_plus_max_byte_value_times_20

    def test_text_compressed(self): assert self._fn()(TEXT) == 6110
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 3001
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 5893
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 6110
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 6110
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedSizeMod29Times100PlusDecompressedSizeMod500PlusMinByteValueTimes200:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200
        return zst_compressed_size_mod_29_times_100_plus_decompressed_size_mod_500_plus_min_byte_value_times_200

    def test_text_compressed(self): assert self._fn()(TEXT) == 7890
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 1001
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 4513
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 7890
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 7890
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
