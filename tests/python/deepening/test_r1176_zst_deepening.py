"""Sprint 622 ZST analytics deepening tests - primes 1361, 1367."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1361_text():
    from zst.zst_analytics import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    assert zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(str(TEXT)) == 3379110


def test_mod1361_minimal():
    from zst.zst_analytics import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    assert zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(str(MINIMAL)) == 119737


def test_mod1361_random():
    from zst.zst_analytics import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    assert zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(str(RANDOM)) == 3640528


def test_mod1367_text():
    from zst.zst_analytics import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    assert zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(str(TEXT)) == 3407634


def test_mod1367_minimal():
    from zst.zst_analytics import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    assert zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(str(MINIMAL)) == 120759


def test_mod1367_random():
    from zst.zst_analytics import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    assert zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(str(RANDOM)) == 3670728


def test_mod1361_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    assert isinstance(zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(str(TEXT)), int)


def test_mod1367_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    assert isinstance(zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(str(TEXT)), int)


def test_mod1361_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    assert zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340(str(TEXT)) >= 0


def test_mod1367_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    assert zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342(str(TEXT)) >= 0


def test_mod1361_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    fn = zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1367_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    fn = zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1361_importable_from_package():
    from zst import zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340
    assert callable(zst_compressed_mod_1361_times_11600_plus_decompressed_times_337_plus_file_size_times_340)


def test_mod1367_importable_from_package():
    from zst import zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342
    assert callable(zst_compressed_mod_1367_times_11700_plus_decompressed_times_339_plus_file_size_times_342)
