"""Sprint 613 ZST analytics deepening tests - primes 1301, 1303."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1301_text():
    from zst.zst_analytics import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    assert zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328(str(TEXT)) == 3207966


def test_mod1301_minimal():
    from zst.zst_analytics import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    assert zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328(str(MINIMAL)) == 113605


def test_mod1301_random():
    from zst.zst_analytics import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    assert zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328(str(RANDOM)) == 3459328


def test_mod1303_text():
    from zst.zst_analytics import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    assert zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330(str(TEXT)) == 3236490


def test_mod1303_minimal():
    from zst.zst_analytics import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    assert zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330(str(MINIMAL)) == 114627


def test_mod1303_random():
    from zst.zst_analytics import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    assert zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330(str(RANDOM)) == 3489528


def test_mod1301_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    assert isinstance(zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328(str(TEXT)), int)


def test_mod1303_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    assert isinstance(zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330(str(TEXT)), int)


def test_mod1301_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    assert zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328(str(TEXT)) >= 0


def test_mod1303_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    assert zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330(str(TEXT)) >= 0


def test_mod1301_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    fn = zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1303_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    fn = zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1301_importable_from_package():
    from zst import zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328
    assert callable(zst_compressed_mod_1301_times_11000_plus_decompressed_times_325_plus_file_size_times_328)


def test_mod1303_importable_from_package():
    from zst import zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330
    assert callable(zst_compressed_mod_1303_times_11100_plus_decompressed_times_327_plus_file_size_times_330)
