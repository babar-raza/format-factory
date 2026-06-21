"""Sprint 353: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod211Times8PlusDecompressedSizeMod3100PlusMaxByteValueTimes200:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200
        return zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200

    def test_text(self): assert self._fn()(T) == 25078
    def test_minimal(self): assert self._fn()(M) == 81
    def test_zero(self): assert self._fn()(Z) == 23013
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 25078
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 25078
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedSizeTimes12PlusDecompressedSizeMod400PlusMinByteValueTimes2000:
    def _fn(self):
        from src.python.zst import zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000
        return zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000

    def test_text(self): assert self._fn()(T) == 67654
    def test_minimal(self): assert self._fn()(M) == 121
    def test_zero(self): assert self._fn()(Z) == 20313
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 67654
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 67654
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
