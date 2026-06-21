"""Sprint 347: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod241Times12PlusDecompressedSizeMod3500PlusMaxByteValueTimes240:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240
        return zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240

    def test_text(self): assert self._fn()(T) == 29802
    def test_minimal(self): assert self._fn()(M) == 121
    def test_zero(self): assert self._fn()(Z) == 27673
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 29802
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 29802
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedSizeTimes20PlusDecompressedSizeMod800PlusMinByteValueTimes2800:
    def _fn(self):
        from src.python.zst import zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800
        return zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800

    def test_text(self): assert self._fn()(T) == 95430
    def test_minimal(self): assert self._fn()(M) == 201
    def test_zero(self): assert self._fn()(Z) == 28513
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 95430
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 95430
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
