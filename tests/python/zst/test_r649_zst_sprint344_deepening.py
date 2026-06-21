"""Sprint 344 ZST deepening.

Tests for:
  - zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900
  - zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000
"""
from __future__ import annotations
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"
_DICT = _SAMPLES / "dict-compressed.zst"
_EMPTY = _SAMPLES / "empty-block.zst"
_BLOCK = _SAMPLES / "block-128k.zst"

def _skip_if_missing(p):
    if not p.exists(): pytest.skip(f"Sample not found: {p}")

class TestZstFileSizeMod863Times3200PlusDecompressedSizeMod9400PlusMaxByteValueTimes900:
    def test_dict_compressed(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert f(_DICT) == 350760
    def test_empty_block(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert f(_EMPTY) == 35200
    def test_block_128k(self):
        _skip_if_missing(_BLOCK)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert f(_BLOCK) == 2466468
    def test_returns_int(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert isinstance(f(_DICT), int)
    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert f(_EMPTY) >= 0
    def test_dict_greater_than_empty(self):
        _skip_if_missing(_DICT); _skip_if_missing(_EMPTY)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert f(_DICT) > f(_EMPTY)
    def test_path_string_accepted(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert isinstance(f(str(_DICT)), int)
    def test_missing_file_raises(self):
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        import pytest
        with pytest.raises(Exception): f("/nonexistent/path/file.zst")
    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT); _skip_if_missing(_BLOCK)
        from src.python.zst import zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900 as f
        assert f(_BLOCK) > f(_DICT)
    def test_exported_in_init(self):
        import src.python.zst as m
        assert hasattr(m, "zst_file_size_mod_863_times_3200_plus_decompressed_size_mod_9400_plus_max_byte_value_times_900")

class TestZstCompressedSizeMod877Times2200PlusDecompressedSizeMod9900PlusMinByteValueTimes4000:
    def test_dict_compressed(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert f(_DICT) == 206960
    def test_empty_block(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert f(_EMPTY) == 24200
    def test_block_128k(self):
        _skip_if_missing(_BLOCK)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert f(_BLOCK) == 899968
    def test_returns_int(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert isinstance(f(_DICT), int)
    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert f(_EMPTY) >= 0
    def test_dict_greater_than_empty(self):
        _skip_if_missing(_DICT); _skip_if_missing(_EMPTY)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert f(_DICT) > f(_EMPTY)
    def test_path_string_accepted(self):
        _skip_if_missing(_DICT)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert isinstance(f(str(_DICT)), int)
    def test_missing_file_raises(self):
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        import pytest
        with pytest.raises(Exception): f("/nonexistent/path/file.zst")
    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT); _skip_if_missing(_BLOCK)
        from src.python.zst import zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000 as f
        assert f(_BLOCK) > f(_DICT)
    def test_exported_in_init(self):
        import src.python.zst as m
        assert hasattr(m, "zst_compressed_size_mod_877_times_2200_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4000")
