"""Sprint 320 ZST analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
TEXT = _ZST / "text-compressed.zst"
MINIMAL = _ZST / "minimal-synthetic.zst"
RANDOM = _ZST / "random-data.zst"

from src.python.zst.zst_codec import (
    zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210,
    zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850,
)


# --- F1: zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210 ---

class TestZstFileSizeMod263Times1050PlusDecompressed3600PlusMaxByte210:
    def test_text_returns_35250(self):
        assert zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(TEXT) == 35250

    def test_minimal_returns_10501(self):
        assert zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(MINIMAL) == 10501

    def test_random_returns_68224(self):
        assert zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(RANDOM) == 68224

    def test_text_returns_int(self):
        assert isinstance(zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(MINIMAL) >= 0

    def test_random_greater_than_text(self):
        assert (zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(RANDOM) >
                zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(TEXT))

    def test_accepts_string_path(self):
        assert zst_file_size_mod_263_times_1050_plus_decompressed_size_mod_3600_plus_max_byte_value_times_210(str(TEXT)) == 35250


# --- F2: zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850 ---

class TestZstCompressedSizeMod269Times975PlusDecompressed3700PlusMinByte1850:
    def test_text_returns_62515(self):
        assert zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(TEXT) == 62515

    def test_minimal_returns_9751(self):
        assert zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(MINIMAL) == 9751

    def test_random_returns_7849(self):
        assert zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(RANDOM) == 7849

    def test_text_returns_int(self):
        assert isinstance(zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(TEXT), int)

    def test_minimal_returns_int(self):
        assert isinstance(zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(MINIMAL), int)

    def test_random_returns_int(self):
        assert isinstance(zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(RANDOM), int)

    def test_text_nonnegative(self):
        assert zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(TEXT) >= 0

    def test_minimal_nonnegative(self):
        assert zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(MINIMAL) >= 0

    def test_text_greater_than_random(self):
        assert (zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(TEXT) >
                zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(RANDOM))

    def test_accepts_string_path(self):
        assert zst_compressed_size_mod_269_times_975_plus_decompressed_size_mod_3700_plus_min_byte_value_times_1850(str(TEXT)) == 62515
