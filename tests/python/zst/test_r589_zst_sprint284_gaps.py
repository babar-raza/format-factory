"""Sprint 284: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod59Times200PlusDecompressedSizeMod300PlusMaxByteValueTimes40:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40
        return zst_file_size_mod_59_times_200_plus_decompressed_size_mod_300_plus_max_byte_value_times_40

    def test_text_compressed(self): assert self._fn()(TEXT) == 12130
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 2001
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 9573
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 12130
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 12130
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedSizeMod61Times150PlusDecompressedSizeMod500PlusMinByteValueTimes300:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300
        return zst_compressed_size_mod_61_times_150_plus_decompressed_size_mod_500_plus_min_byte_value_times_300

    def test_text_compressed(self): assert self._fn()(TEXT) == 14190
    def test_minimal_synthetic(self): assert self._fn()(MINIMAL) == 1501
    def test_zeroseq(self): assert self._fn()(ZEROSEQ) == 6763
    def test_returns_int(self): assert isinstance(self._fn()(TEXT), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(TEXT)) == 14190
    def test_string_path_accepted(self): assert self._fn()(str(TEXT)) == 14190
    def test_text_largest(self):
        fn = self._fn(); assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
