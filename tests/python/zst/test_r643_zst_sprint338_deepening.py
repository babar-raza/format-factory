"""Sprint 338 ZST deepening - test_r643.

Tests for:
  - zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
  - zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20

Sample data:
  block-128k.zst:     csize=131081, dsize=131068, maxb=0, minb=0
  dict-compressed.zst: csize=74, dsize=4160, maxb=122, minb=10
  empty-block.zst:    csize=11, dsize=0, maxb=0, minb=0
"""
from __future__ import annotations
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

_BLOCK = _SAMPLES / "block-128k.zst"
_DICT = _SAMPLES / "dict-compressed.zst"
_EMPTY = _SAMPLES / "empty-block.zst"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


class TestZstCompressedSizeMod571Times31PlusDecompressedMod8800Times5PlusMaxByteTimes240:
    def test_block_128k(self):
        _skip_if_missing(_BLOCK)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        assert zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(_BLOCK) == 49322

    def test_dict_compressed(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        assert zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(_DICT) == 52374

    def test_empty_block(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        assert zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(_EMPTY) == 341

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        assert isinstance(zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        assert zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(_EMPTY) >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240 as f
        assert f(_DICT) > f(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        assert isinstance(zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240
        with pytest.raises(Exception):
            zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240("/nonexistent/path/file.zst")

    def test_block_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_BLOCK)
        from src.python.zst import zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240 as f
        assert f(_BLOCK) > f(_EMPTY)

    def test_exported_in_init(self):
        import src.python.zst as m
        assert hasattr(m, "zst_compressed_size_mod_571_times_31_plus_decompressed_size_mod_8800_times_5_plus_max_byte_value_times_240")


class TestZstCompressedSizeTimes45PlusDecompressedTimes12PlusMaxByteTimes20:
    def test_block_128k(self):
        _skip_if_missing(_BLOCK)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        assert zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(_BLOCK) == 7471461

    def test_dict_compressed(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        assert zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(_DICT) == 55690

    def test_empty_block(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        assert zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(_EMPTY) == 495

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        assert isinstance(zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        assert zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(_EMPTY) >= 0

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT); _skip_if_missing(_BLOCK)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20 as f
        assert f(_BLOCK) > f(_DICT)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        assert isinstance(zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20
        with pytest.raises(Exception):
            zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20("/nonexistent/path/file.zst")

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20 as f
        assert f(_DICT) > f(_EMPTY)

    def test_exported_in_init(self):
        import src.python.zst as m
        assert hasattr(m, "zst_compressed_size_times_45_plus_decompressed_size_times_12_plus_max_byte_value_times_20")
