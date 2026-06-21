"""Sprint 595 ZST analytics deepening tests - primes 1223, 1229."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1223_text():
    from zst.zst_analytics import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    assert zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304(str(TEXT)) == 2865678

def test_mod1223_minimal():
    from zst.zst_analytics import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    assert zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304(str(MINIMAL)) == 101341

def test_mod1223_random():
    from zst.zst_analytics import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    assert zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304(str(RANDOM)) == 3096928

def test_mod1229_text():
    from zst.zst_analytics import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    assert zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306(str(TEXT)) == 2894202

def test_mod1229_minimal():
    from zst.zst_analytics import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    assert zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306(str(MINIMAL)) == 102363

def test_mod1229_random():
    from zst.zst_analytics import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    assert zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306(str(RANDOM)) == 3127128

def test_mod1223_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    assert isinstance(zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304(str(TEXT)), int)

def test_mod1223_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    assert zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304(str(TEXT)) >= 0

def test_mod1223_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    fn2 = zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1223_importable_from_package():
    from zst import zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304
    assert callable(zst_compressed_mod_1223_times_9800_plus_decompressed_times_301_plus_file_size_times_304)

def test_mod1229_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    assert isinstance(zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306(str(TEXT)), int)

def test_mod1229_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    assert zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306(str(TEXT)) >= 0

def test_mod1229_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    fn2 = zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1229_importable_from_package():
    from zst import zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306
    assert callable(zst_compressed_mod_1229_times_9900_plus_decompressed_times_303_plus_file_size_times_306)
