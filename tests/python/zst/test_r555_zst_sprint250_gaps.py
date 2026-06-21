"""Sprint 250: ZST analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod31Times400PlusDecompressedTimes6PlusCompressedMod11Times150:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_31_times_400_plus_decompressed_times_6_plus_compressed_mod_11_times_150
        return zst_compressed_mod_31_times_400_plus_decompressed_times_6_plus_compressed_mod_11_times_150

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 13140

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 5506

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 10528

    def test_returns_int(self):
        assert isinstance(self._fn()(TEXT), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(TEXT)) == 13140

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 13140

    def test_text_largest(self):
        fn = self._fn()
        assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)

    def test_minimal_smallest(self):
        fn = self._fn()
        assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedTimes12PlusDecompressedMod50Times80PlusFileSizeTimes15:
    def _fn(self):
        from src.python.zst import zst_compressed_times_12_plus_decompressed_mod_50_times_80_plus_file_size_times_15
        return zst_compressed_times_12_plus_decompressed_mod_50_times_80_plus_file_size_times_15

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 10544

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 350

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 1715

    def test_returns_int(self):
        assert isinstance(self._fn()(TEXT), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(TEXT), fn(MINIMAL), fn(ZEROSEQ)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [TEXT, MINIMAL, ZEROSEQ]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(TEXT)) == 10544

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 10544

    def test_text_largest(self):
        fn = self._fn()
        assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)

    def test_minimal_smallest(self):
        fn = self._fn()
        assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
