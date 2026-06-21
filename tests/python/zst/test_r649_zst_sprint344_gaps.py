"""Sprint 344: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod73Times650PlusDecompressedTimes29PlusFileSizeTimes36:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36
        return zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36

    def test_text(self): assert self._fn()(T) == 55552
    def test_minimal(self): assert self._fn()(M) == 6889
    def test_zero(self): assert self._fn()(Z) == 17527
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 55552
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 55552
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedTimes14PlusDecompressedMod150Times115PlusFileSizeTimes30:
    def _fn(self):
        from src.python.zst import zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30
        return zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30

    def test_text(self): assert self._fn()(T) == 22318
    def test_minimal(self): assert self._fn()(M) == 555
    def test_zero(self): assert self._fn()(Z) == 2595
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 22318
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 22318
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
