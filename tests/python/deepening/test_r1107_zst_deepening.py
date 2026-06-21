"""Sprint 553 ZST analytics deepening tests - primes 1021, 1031."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1021_text():
    from zst.zst_analytics import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    assert zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(str(TEXT)) == 2067006


def test_mod1021_minimal():
    from zst.zst_analytics import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    assert zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(str(MINIMAL)) == 72725


def test_mod1021_random():
    from zst.zst_analytics import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    assert zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(str(RANDOM)) == 2251328


def test_mod1031_text():
    from zst.zst_analytics import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    assert zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(str(TEXT)) == 2095530


def test_mod1031_minimal():
    from zst.zst_analytics import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    assert zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(str(MINIMAL)) == 73747


def test_mod1031_random():
    from zst.zst_analytics import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    assert zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(str(RANDOM)) == 2281528


def test_mod1021_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    assert isinstance(zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(str(TEXT)), int)


def test_mod1031_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    assert isinstance(zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(str(TEXT)), int)


def test_mod1021_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    assert zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248(str(TEXT)) >= 0


def test_mod1031_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    assert zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250(str(TEXT)) >= 0


def test_mod1021_importable_from_package():
    from zst import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    assert callable(zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248)


def test_mod1031_importable_from_package():
    from zst import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    assert callable(zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250)


def test_mod1021_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    fn = zst_compressed_mod_1021_times_7000_plus_decompressed_times_245_plus_file_size_times_248
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1031_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    fn = zst_compressed_mod_1031_times_7100_plus_decompressed_times_247_plus_file_size_times_250
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
