"""Sprint 274: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod41Times300PlusDecompressedTimes13PlusFileSizeTimes18:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18
        return zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18

    def test_text_compressed(self): assert self._fn()(TEXT) == 17766
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 3193
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 8119
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 17766
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 17766
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedTimes6PlusDecompressedMod70Times60PlusFileSizeTimes14:
    def _fn(self):
        from src.python.zst import zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14
        return zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14

    def test_text_compressed(self): assert self._fn()(TEXT) == 7840
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 260
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 1280
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 7840
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 7840
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
