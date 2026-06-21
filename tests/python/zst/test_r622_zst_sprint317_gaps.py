"""Sprint 317: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod157Times700PlusDecompressedSizeMod2300PlusMaxByteValueTimes150:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150
        return zst_file_size_mod_157_times_700_plus_decompressed_size_mod_2300_plus_max_byte_value_times_150

    def test_text(self): assert self._fn()(T) == 99040
    def test_minimal(self): assert self._fn()(M) == 7001
    def test_zero(self): assert self._fn()(Z) == 34613
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 99040
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 99040
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedSizeMod163Times650PlusDecompressedSizeMod2400PlusMinByteValueTimes1300:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300
        return zst_compressed_size_mod_163_times_650_plus_decompressed_size_mod_2400_plus_min_byte_value_times_1300

    def test_text(self): assert self._fn()(T) == 112840
    def test_minimal(self): assert self._fn()(M) == 6501
    def test_zero(self): assert self._fn()(Z) == 29263
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 112840
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 112840
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
