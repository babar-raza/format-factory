"""Sprint 544 ZST analytics deepening tests — primes 983, 991."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod983_text():
    from zst.zst_analytics import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    assert zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236(str(TEXT)) == 1895862


def test_mod983_minimal():
    from zst.zst_analytics import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    assert zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236(str(MINIMAL)) == 66593


def test_mod983_random():
    from zst.zst_analytics import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    assert zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236(str(RANDOM)) == 2070128


def test_mod991_text():
    from zst.zst_analytics import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    assert zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238(str(TEXT)) == 1924386


def test_mod991_minimal():
    from zst.zst_analytics import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    assert zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238(str(MINIMAL)) == 67615


def test_mod991_random():
    from zst.zst_analytics import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    assert zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238(str(RANDOM)) == 2100328


def test_mod983_returns_int():
    from zst.zst_analytics import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    assert isinstance(zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236(str(TEXT)), int)


def test_mod991_returns_int():
    from zst.zst_analytics import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    assert isinstance(zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238(str(TEXT)), int)


def test_mod983_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    assert zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236(str(TEXT)) >= 0


def test_mod991_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    assert zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238(str(TEXT)) >= 0


def test_mod983_importable_from_package():
    from zst import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    assert callable(zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236)


def test_mod991_importable_from_package():
    from zst import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    assert callable(zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238)


def test_mod983_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    fn = zst_compressed_mod_983_times_6400_plus_decompressed_times_233_plus_file_size_times_236
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod991_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    fn = zst_compressed_mod_991_times_6500_plus_decompressed_times_235_plus_file_size_times_238
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
