"""Sprint 637 ZST analytics deepening tests - primes 1439, 1447."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1439_text():
    from zst.zst_analytics import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    assert zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360(str(TEXT)) == 3664350


def test_mod1439_minimal():
    from zst.zst_analytics import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    assert zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360(str(MINIMAL)) == 129957


def test_mod1439_random():
    from zst.zst_analytics import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    assert zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360(str(RANDOM)) == 3942528


def test_mod1439_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    assert isinstance(zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360(str(TEXT)), int)


def test_mod1439_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    assert zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360(str(TEXT)) >= 0


def test_mod1439_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    fn_ref = zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    results = {fn_ref(str(TEXT)), fn_ref(str(MINIMAL)), fn_ref(str(RANDOM))}
    assert len(results) == 3


def test_mod1439_importable_from_package():
    from zst import zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360
    assert callable(zst_compressed_mod_1439_times_12600_plus_decompressed_times_357_plus_file_size_times_360)


def test_mod1447_text():
    from zst.zst_analytics import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    assert zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362(str(TEXT)) == 3692874


def test_mod1447_minimal():
    from zst.zst_analytics import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    assert zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362(str(MINIMAL)) == 130979


def test_mod1447_random():
    from zst.zst_analytics import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    assert zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362(str(RANDOM)) == 3972728


def test_mod1447_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    assert isinstance(zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362(str(TEXT)), int)


def test_mod1447_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    assert zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362(str(TEXT)) >= 0


def test_mod1447_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    fn_ref = zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    results = {fn_ref(str(TEXT)), fn_ref(str(MINIMAL)), fn_ref(str(RANDOM))}
    assert len(results) == 3


def test_mod1447_importable_from_package():
    from zst import zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362
    assert callable(zst_compressed_mod_1447_times_12700_plus_decompressed_times_359_plus_file_size_times_362)
