"""Sprint 649 ZST analytics deepening tests - primes 1487, 1489."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1487_text():
    from zst.zst_analytics import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    assert zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376(str(TEXT)) == 3892542


def test_mod1487_minimal():
    from zst.zst_analytics import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    assert zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376(str(MINIMAL)) == 138133


def test_mod1487_random():
    from zst.zst_analytics import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    assert zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376(str(RANDOM)) == 4184128


def test_mod1489_text():
    from zst.zst_analytics import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    assert zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378(str(TEXT)) == 3921066


def test_mod1489_minimal():
    from zst.zst_analytics import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    assert zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378(str(MINIMAL)) == 139155


def test_mod1489_random():
    from zst.zst_analytics import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    assert zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378(str(RANDOM)) == 4214328


def test_mod1487_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    assert isinstance(zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376(str(TEXT)), int)


def test_mod1489_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    assert isinstance(zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378(str(TEXT)), int)


def test_mod1487_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    assert zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376(str(TEXT)) >= 0


def test_mod1489_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    assert zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378(str(TEXT)) >= 0


def test_mod1487_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    fn = zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1489_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    fn = zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1487_importable_from_package():
    from zst import zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376
    assert callable(zst_compressed_mod_1487_times_13400_plus_decompressed_times_373_plus_file_size_times_376)


def test_mod1489_importable_from_package():
    from zst import zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378
    assert callable(zst_compressed_mod_1489_times_13500_plus_decompressed_times_375_plus_file_size_times_378)
