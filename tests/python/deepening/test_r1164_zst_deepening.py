"""Sprint 610 ZST analytics deepening tests - primes 1291, 1297."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1291_text():
    from zst.zst_analytics import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    assert zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324(str(TEXT)) == 3150918


def test_mod1291_minimal():
    from zst.zst_analytics import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    assert zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324(str(MINIMAL)) == 111561


def test_mod1291_random():
    from zst.zst_analytics import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    assert zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324(str(RANDOM)) == 3398928


def test_mod1297_text():
    from zst.zst_analytics import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    assert zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326(str(TEXT)) == 3179442


def test_mod1297_minimal():
    from zst.zst_analytics import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    assert zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326(str(MINIMAL)) == 112583


def test_mod1297_random():
    from zst.zst_analytics import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    assert zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326(str(RANDOM)) == 3429128


def test_mod1291_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    assert isinstance(zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324(str(TEXT)), int)


def test_mod1297_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    assert isinstance(zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326(str(TEXT)), int)


def test_mod1291_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    assert zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324(str(TEXT)) >= 0


def test_mod1297_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    assert zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326(str(TEXT)) >= 0


def test_mod1291_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    fn = zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1297_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    fn = zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1291_importable_from_package():
    from zst import zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324
    assert callable(zst_compressed_mod_1291_times_10800_plus_decompressed_times_321_plus_file_size_times_324)


def test_mod1297_importable_from_package():
    from zst import zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326
    assert callable(zst_compressed_mod_1297_times_10900_plus_decompressed_times_323_plus_file_size_times_326)
