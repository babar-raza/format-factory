"""Sprint 287: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod47Times350PlusDecompressedTimes17PlusFileSizeTimes24:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24
        return zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24

    def test_text_compressed(self): assert self._fn()(TEXT) == 26108
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 3757
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 9571
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 26108
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 26108
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedTimes8PlusDecompressedMod90Times80PlusFileSizeTimes18:
    def _fn(self):
        from src.python.zst import zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18
        return zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18

    def test_text_compressed(self): assert self._fn()(TEXT) == 9472
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 340
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 1690
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 9472
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 9472
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
