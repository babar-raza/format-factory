"""Sprint 640 ZST analytics deepening tests - primes 1451, 1453."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1451_text():
    from zst.zst_analytics import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    assert zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364(str(TEXT)) == 3721398


def test_mod1451_minimal():
    from zst.zst_analytics import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    assert zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364(str(MINIMAL)) == 132001


def test_mod1451_random():
    from zst.zst_analytics import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    assert zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364(str(RANDOM)) == 4002928


def test_mod1453_text():
    from zst.zst_analytics import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    assert zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366(str(TEXT)) == 3749922


def test_mod1453_minimal():
    from zst.zst_analytics import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    assert zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366(str(MINIMAL)) == 133023


def test_mod1453_random():
    from zst.zst_analytics import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    assert zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366(str(RANDOM)) == 4033128


def test_mod1451_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    assert isinstance(zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364(str(TEXT)), int)


def test_mod1453_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    assert isinstance(zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366(str(TEXT)), int)


def test_mod1451_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    assert zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364(str(TEXT)) >= 0


def test_mod1453_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    assert zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366(str(TEXT)) >= 0


def test_mod1451_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    fn = zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1453_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    fn = zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1451_importable_from_package():
    from zst import zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364
    assert callable(zst_compressed_mod_1451_times_12800_plus_decompressed_times_361_plus_file_size_times_364)


def test_mod1453_importable_from_package():
    from zst import zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366
    assert callable(zst_compressed_mod_1453_times_12900_plus_decompressed_times_363_plus_file_size_times_366)
