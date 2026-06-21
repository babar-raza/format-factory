"""Sprint 247: ZST analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstCompressedMod17Times300PlusDecompressedTimes5PlusFileSizeTimes10:
    def _fn(self):
        from src.python.zst import zst_compressed_mod_17_times_300_plus_decompressed_times_5_plus_file_size_times_10
        return zst_compressed_mod_17_times_300_plus_decompressed_times_5_plus_file_size_times_10

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 4670

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 3105

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 2715

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
        assert fn(Path(TEXT)) == 4670

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 4670

    def test_text_larger_than_zeroseq(self):
        fn = self._fn()
        assert fn(TEXT) > fn(ZEROSEQ)

    def test_minimal_larger_than_zeroseq(self):
        fn = self._fn()
        assert fn(MINIMAL) > fn(ZEROSEQ)


class TestZstCompressedTimes8PlusDecompressedMod30Times100PlusCompressedMod7Times200:
    def _fn(self):
        from src.python.zst import zst_compressed_times_8_plus_decompressed_mod_30_times_100_plus_compressed_mod_7_times_200
        return zst_compressed_times_8_plus_decompressed_mod_30_times_100_plus_compressed_mod_7_times_200

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 3376

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 780

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 2300

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
        assert fn(Path(TEXT)) == 3376

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 3376

    def test_text_larger_than_minimal(self):
        fn = self._fn()
        assert fn(TEXT) > fn(MINIMAL)

    def test_zeroseq_larger_than_minimal(self):
        fn = self._fn()
        assert fn(ZEROSEQ) > fn(MINIMAL)
