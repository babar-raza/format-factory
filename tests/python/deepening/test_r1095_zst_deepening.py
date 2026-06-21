"""Sprint 541 ZST analytics deepening tests — primes 971, 977."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod971_text():
    from zst.zst_analytics import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    assert zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232(str(TEXT)) == 1838814


def test_mod971_minimal():
    from zst.zst_analytics import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    assert zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232(str(MINIMAL)) == 64549


def test_mod971_random():
    from zst.zst_analytics import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    assert zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232(str(RANDOM)) == 2009728


def test_mod977_text():
    from zst.zst_analytics import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    assert zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234(str(TEXT)) == 1867338


def test_mod977_minimal():
    from zst.zst_analytics import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    assert zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234(str(MINIMAL)) == 65571


def test_mod977_random():
    from zst.zst_analytics import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    assert zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234(str(RANDOM)) == 2039928


def test_mod971_returns_int():
    from zst.zst_analytics import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    assert isinstance(zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232(str(TEXT)), int)


def test_mod977_returns_int():
    from zst.zst_analytics import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    assert isinstance(zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234(str(TEXT)), int)


def test_mod971_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    assert zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232(str(TEXT)) >= 0


def test_mod977_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    assert zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234(str(TEXT)) >= 0


def test_mod971_importable_from_package():
    from zst import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    assert callable(zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232)


def test_mod977_importable_from_package():
    from zst import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    assert callable(zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234)


def test_mod971_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    fn = zst_compressed_mod_971_times_6200_plus_decompressed_times_229_plus_file_size_times_232
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod977_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    fn = zst_compressed_mod_977_times_6300_plus_decompressed_times_231_plus_file_size_times_234
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
