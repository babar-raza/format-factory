"""Sprint 338: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeMod229Times10PlusDecompressedSizeMod3300PlusMaxByteValueTimes220:
    def _fn(self):
        from src.python.zst import zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220
        return zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220

    def test_text(self): assert self._fn()(T) == 27440
    def test_minimal(self): assert self._fn()(M) == 101
    def test_zero(self): assert self._fn()(Z) == 25343
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 27440
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 27440
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedSizeTimes16PlusDecompressedSizeMod600PlusMinByteValueTimes2400:
    def _fn(self):
        from src.python.zst import zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400
        return zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400

    def test_text(self): assert self._fn()(T) == 81542
    def test_minimal(self): assert self._fn()(M) == 161
    def test_zero(self): assert self._fn()(Z) == 24413
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 81542
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 81542
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
