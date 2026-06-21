"""Sprint 598 ZST analytics deepening tests - primes 1231, 1237."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1231_text():
    from zst.zst_analytics import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    assert zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308(str(TEXT)) == 2922726

def test_mod1231_minimal():
    from zst.zst_analytics import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    assert zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308(str(MINIMAL)) == 103385

def test_mod1231_random():
    from zst.zst_analytics import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    assert zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308(str(RANDOM)) == 3157328

def test_mod1237_text():
    from zst.zst_analytics import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    assert zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310(str(TEXT)) == 2951250

def test_mod1237_minimal():
    from zst.zst_analytics import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    assert zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310(str(MINIMAL)) == 104407

def test_mod1237_random():
    from zst.zst_analytics import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    assert zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310(str(RANDOM)) == 3187528

def test_mod1231_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    assert isinstance(zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308(str(TEXT)), int)

def test_mod1231_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    assert zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308(str(TEXT)) >= 0

def test_mod1231_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    fn2 = zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1231_importable_from_package():
    from zst import zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308
    assert callable(zst_compressed_mod_1231_times_10000_plus_decompressed_times_305_plus_file_size_times_308)

def test_mod1237_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    assert isinstance(zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310(str(TEXT)), int)

def test_mod1237_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    assert zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310(str(TEXT)) >= 0

def test_mod1237_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    fn2 = zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1237_importable_from_package():
    from zst import zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310
    assert callable(zst_compressed_mod_1237_times_10100_plus_decompressed_times_307_plus_file_size_times_310)
