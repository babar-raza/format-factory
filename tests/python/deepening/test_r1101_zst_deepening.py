"""Sprint 547 ZST analytics deepening tests - primes 997, 1009."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod997_text():
    from zst.zst_analytics import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    assert zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240(str(TEXT)) == 1952910


def test_mod997_minimal():
    from zst.zst_analytics import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    assert zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240(str(MINIMAL)) == 68637


def test_mod997_random():
    from zst.zst_analytics import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    assert zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240(str(RANDOM)) == 2130528


def test_mod1009_text():
    from zst.zst_analytics import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    assert zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242(str(TEXT)) == 1981434


def test_mod1009_minimal():
    from zst.zst_analytics import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    assert zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242(str(MINIMAL)) == 69659


def test_mod1009_random():
    from zst.zst_analytics import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    assert zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242(str(RANDOM)) == 2160728


def test_mod997_returns_int():
    from zst.zst_analytics import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    assert isinstance(zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240(str(TEXT)), int)


def test_mod1009_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    assert isinstance(zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242(str(TEXT)), int)


def test_mod997_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    assert zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240(str(TEXT)) >= 0


def test_mod1009_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    assert zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242(str(TEXT)) >= 0


def test_mod997_importable_from_package():
    from zst import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    assert callable(zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240)


def test_mod1009_importable_from_package():
    from zst import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    assert callable(zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242)


def test_mod997_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    fn = zst_compressed_mod_997_times_6600_plus_decompressed_times_237_plus_file_size_times_240
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1009_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    fn = zst_compressed_mod_1009_times_6700_plus_decompressed_times_239_plus_file_size_times_242
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
