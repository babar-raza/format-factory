"""Sprint 256: ZST analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ZST_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

TEXT = _ZST_SAMPLES / "text-compressed.zst"
MINIMAL = _ZST_SAMPLES / "minimal-synthetic.zst"
ZEROSEQ = _ZST_SAMPLES / "zeroSeq_2B.zst"


class TestZstFileSizeTimes20PlusDecompressedSizeMod100Times50PlusCompressedSizeMod13Times200:
    def _fn(self):
        from src.python.zst import zst_file_size_times_20_plus_decompressed_size_mod_100_times_50_plus_compressed_size_mod_13_times_200
        return zst_file_size_times_20_plus_decompressed_size_mod_100_times_50_plus_compressed_size_mod_13_times_200

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 12340

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 2250

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 3550

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
        assert fn(Path(TEXT)) == 12340

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 12340

    def test_text_largest(self):
        fn = self._fn()
        assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)

    def test_minimal_smallest(self):
        fn = self._fn()
        assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))


class TestZstCompressedSizeTimes15PlusDecompressedSizeMod70Times30PlusMaxByteValueTimes50:
    def _fn(self):
        from src.python.zst import zst_compressed_size_times_15_plus_decompressed_size_mod_70_times_30_plus_max_byte_value_times_50
        return zst_compressed_size_times_15_plus_decompressed_size_mod_70_times_30_plus_max_byte_value_times_50

    def test_text_compressed(self):
        assert self._fn()(TEXT) == 11330

    def test_minimal_synthetic(self):
        assert self._fn()(MINIMAL) == 180

    def test_zeroseq(self):
        assert self._fn()(ZEROSEQ) == 6465

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
        assert fn(Path(TEXT)) == 11330

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(TEXT)) == 11330

    def test_text_largest(self):
        fn = self._fn()
        assert fn(TEXT) > fn(ZEROSEQ) > fn(MINIMAL)

    def test_minimal_smallest(self):
        fn = self._fn()
        assert fn(MINIMAL) == min(fn(TEXT), fn(MINIMAL), fn(ZEROSEQ))
