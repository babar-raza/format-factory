"""Sprint 616 ZST analytics deepening tests - primes 1307, 1319."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1307_text():
    from zst.zst_analytics import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    assert zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332(str(TEXT)) == 3265014


def test_mod1307_minimal():
    from zst.zst_analytics import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    assert zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332(str(MINIMAL)) == 115649


def test_mod1307_random():
    from zst.zst_analytics import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    assert zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332(str(RANDOM)) == 3519728


def test_mod1319_text():
    from zst.zst_analytics import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    assert zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334(str(TEXT)) == 3293538


def test_mod1319_minimal():
    from zst.zst_analytics import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    assert zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334(str(MINIMAL)) == 116671


def test_mod1319_random():
    from zst.zst_analytics import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    assert zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334(str(RANDOM)) == 3549928


def test_mod1307_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    assert isinstance(zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332(str(TEXT)), int)


def test_mod1319_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    assert isinstance(zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334(str(TEXT)), int)


def test_mod1307_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    assert zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332(str(TEXT)) >= 0


def test_mod1319_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    assert zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334(str(TEXT)) >= 0


def test_mod1307_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    fn = zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1319_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    fn = zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    results = {fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}
    assert len(results) == 3


def test_mod1307_importable_from_package():
    from zst import zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332
    assert callable(zst_compressed_mod_1307_times_11200_plus_decompressed_times_329_plus_file_size_times_332)


def test_mod1319_importable_from_package():
    from zst import zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334
    assert callable(zst_compressed_mod_1319_times_11300_plus_decompressed_times_331_plus_file_size_times_334)
