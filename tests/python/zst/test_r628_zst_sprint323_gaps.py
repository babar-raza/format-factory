"""Sprint 323: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod179Times5PlusDecompressedSizeMod2700PlusMaxByteValueTimes180:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180
        return zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180

    def test_text(self): assert self._fn()(T) == 22635
    def test_minimal(self): assert self._fn()(M) == 51
    def test_zero(self): assert self._fn()(Z) == 20658
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 22635
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 22635
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedSizeMod181Times10PlusDecompressedSizeMod2800PlusMinByteValueTimes1500:
    def _fn(self):
        from src.python.zst import zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500
        return zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500

    def test_text(self): assert self._fn()(T) == 49300
    def test_minimal(self): assert self._fn()(M) == 101
    def test_zero(self): assert self._fn()(Z) == 15263
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 49300
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 49300
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
