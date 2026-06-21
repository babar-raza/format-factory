"""Sprint 643 ZST analytics deepening tests - primes 1459, 1471."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1459_text():
    from zst.zst_analytics import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    assert zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368(str(TEXT)) == 3778446


def test_mod1459_minimal():
    from zst.zst_analytics import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    assert zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368(str(MINIMAL)) == 134045


def test_mod1459_random():
    from zst.zst_analytics import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    assert zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368(str(RANDOM)) == 4063328


def test_mod1471_text():
    from zst.zst_analytics import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    assert zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370(str(TEXT)) == 3806970


def test_mod1471_minimal():
    from zst.zst_analytics import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    assert zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370(str(MINIMAL)) == 135067


def test_mod1471_random():
    from zst.zst_analytics import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    assert zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370(str(RANDOM)) == 4093528


def test_mod1459_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    assert isinstance(zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368(str(TEXT)), int)


def test_mod1471_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    assert isinstance(zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370(str(TEXT)), int)


def test_mod1459_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    assert zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368(str(TEXT)) >= 0


def test_mod1471_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    assert zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370(str(TEXT)) >= 0


def test_mod1459_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    fn = zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1471_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    fn = zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1459_importable_from_package():
    from zst import zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368
    assert callable(zst_compressed_mod_1459_times_13000_plus_decompressed_times_365_plus_file_size_times_368)


def test_mod1471_importable_from_package():
    from zst import zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370
    assert callable(zst_compressed_mod_1471_times_13100_plus_decompressed_times_367_plus_file_size_times_370)
