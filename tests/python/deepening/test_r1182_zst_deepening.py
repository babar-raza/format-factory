"""Sprint 628 ZST analytics deepening tests - primes 1399, 1409."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1399_text():
    from zst.zst_analytics import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    assert zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348(str(TEXT)) == 3493206


def test_mod1399_minimal():
    from zst.zst_analytics import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    assert zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348(str(MINIMAL)) == 123825


def test_mod1399_random():
    from zst.zst_analytics import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    assert zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348(str(RANDOM)) == 3761328


def test_mod1409_text():
    from zst.zst_analytics import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    assert zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350(str(TEXT)) == 3521730


def test_mod1409_minimal():
    from zst.zst_analytics import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    assert zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350(str(MINIMAL)) == 124847


def test_mod1409_random():
    from zst.zst_analytics import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    assert zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350(str(RANDOM)) == 3791528


def test_mod1399_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    assert isinstance(zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348(str(TEXT)), int)


def test_mod1409_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    assert isinstance(zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350(str(TEXT)), int)


def test_mod1399_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    assert zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348(str(TEXT)) >= 0


def test_mod1409_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    assert zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350(str(TEXT)) >= 0


def test_mod1399_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    fn = zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1409_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    fn = zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1399_importable_from_package():
    from zst import zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348
    assert callable(zst_compressed_mod_1399_times_12000_plus_decompressed_times_345_plus_file_size_times_348)


def test_mod1409_importable_from_package():
    from zst import zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350
    assert callable(zst_compressed_mod_1409_times_12100_plus_decompressed_times_347_plus_file_size_times_350)
