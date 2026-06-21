"""Sprint 350: ZST analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

T = _ZST_SAMPLES / "text-compressed.zst"
M = _ZST_SAMPLES / "minimal-synthetic.zst"
Z = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod67Times550PlusDecompressedTimes25PlusFileSizeTimes32:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32
        return zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32

    def test_text(self): assert self._fn()(T) == 20654
    def test_minimal(self): assert self._fn()(M) == 5845
    def test_zero(self): assert self._fn()(Z) == 14875
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 20654
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 20654
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))


class TestZstCompressedTimes12PlusDecompressedMod130Times105PlusFileSizeTimes26:
    def _fn(self):
        from src.python.zst import zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26
        return zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26

    def test_text(self): assert self._fn()(T) == 10336
    def test_minimal(self): assert self._fn()(M) == 485
    def test_zero(self): assert self._fn()(Z) == 2315
    def test_returns_int(self): assert isinstance(self._fn()(T), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(T), fn(M), fn(Z)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [T, M, Z]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(T)) == 10336
    def test_string_path_accepted(self): assert self._fn()(str(T)) == 10336
    def test_text_largest(self):
        fn = self._fn(); assert fn(T) > fn(Z) > fn(M)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(M) == min(fn(T), fn(M), fn(Z))
