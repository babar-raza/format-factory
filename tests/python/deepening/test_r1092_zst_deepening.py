"""Sprint 538 ZST analytics deepening tests — primes 953, 967."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod953_text():
    from zst.zst_analytics import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    assert zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228(str(TEXT)) == 1781766


def test_mod953_minimal():
    from zst.zst_analytics import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    assert zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228(str(MINIMAL)) == 62505


def test_mod953_random():
    from zst.zst_analytics import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    assert zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228(str(RANDOM)) == 1949328


def test_mod967_text():
    from zst.zst_analytics import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    assert zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230(str(TEXT)) == 1810290


def test_mod967_minimal():
    from zst.zst_analytics import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    assert zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230(str(MINIMAL)) == 63527


def test_mod967_random():
    from zst.zst_analytics import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    assert zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230(str(RANDOM)) == 1979528


def test_mod953_returns_int():
    from zst.zst_analytics import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    assert isinstance(zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228(str(TEXT)), int)


def test_mod967_returns_int():
    from zst.zst_analytics import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    assert isinstance(zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230(str(TEXT)), int)


def test_mod953_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    assert zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228(str(TEXT)) >= 0


def test_mod967_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    assert zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230(str(TEXT)) >= 0


def test_mod953_importable_from_package():
    from zst import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    assert callable(zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228)


def test_mod967_importable_from_package():
    from zst import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    assert callable(zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230)


def test_mod953_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    fn = zst_compressed_mod_953_times_6000_plus_decompressed_times_225_plus_file_size_times_228
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod967_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    fn = zst_compressed_mod_967_times_6100_plus_decompressed_times_227_plus_file_size_times_230
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3
