"""Sprint 661 ZST analytics deepening tests - primes 1549, 1553."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1549_text():
    from zst.zst_analytics import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    assert zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392(str(TEXT)) == 4120734


def test_mod1549_minimal():
    from zst.zst_analytics import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    assert zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392(str(MINIMAL)) == 146309


def test_mod1549_random():
    from zst.zst_analytics import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    assert zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392(str(RANDOM)) == 4425728


def test_mod1553_text():
    from zst.zst_analytics import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    assert zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394(str(TEXT)) == 4149258


def test_mod1553_minimal():
    from zst.zst_analytics import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    assert zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394(str(MINIMAL)) == 147331


def test_mod1553_random():
    from zst.zst_analytics import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    assert zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394(str(RANDOM)) == 4455928


def test_mod1549_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    assert isinstance(zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392(str(TEXT)), int)


def test_mod1553_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    assert isinstance(zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394(str(TEXT)), int)


def test_mod1549_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    assert zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392(str(TEXT)) >= 0


def test_mod1553_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    assert zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394(str(TEXT)) >= 0


def test_mod1549_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    fn = zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1553_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    fn = zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1549_importable_from_package():
    from zst import zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392
    assert callable(zst_compressed_mod_1549_times_14200_plus_decompressed_times_389_plus_file_size_times_392)


def test_mod1553_importable_from_package():
    from zst import zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394
    assert callable(zst_compressed_mod_1553_times_14300_plus_decompressed_times_391_plus_file_size_times_394)
