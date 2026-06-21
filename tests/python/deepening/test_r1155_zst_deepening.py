"""Sprint 601 ZST analytics deepening tests - primes 1249, 1259."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1249_text():
    from zst.zst_analytics import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    assert zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312(str(TEXT)) == 2979774

def test_mod1249_minimal():
    from zst.zst_analytics import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    assert zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312(str(MINIMAL)) == 105429

def test_mod1249_random():
    from zst.zst_analytics import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    assert zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312(str(RANDOM)) == 3217728

def test_mod1259_text():
    from zst.zst_analytics import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    assert zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314(str(TEXT)) == 3008298

def test_mod1259_minimal():
    from zst.zst_analytics import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    assert zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314(str(MINIMAL)) == 106451

def test_mod1259_random():
    from zst.zst_analytics import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    assert zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314(str(RANDOM)) == 3247928

def test_mod1249_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    assert isinstance(zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312(str(TEXT)), int)

def test_mod1249_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    assert zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312(str(TEXT)) >= 0

def test_mod1249_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    fn2 = zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1249_importable_from_package():
    from zst import zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312
    assert callable(zst_compressed_mod_1249_times_10200_plus_decompressed_times_309_plus_file_size_times_312)

def test_mod1259_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    assert isinstance(zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314(str(TEXT)), int)

def test_mod1259_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    assert zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314(str(TEXT)) >= 0

def test_mod1259_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    fn2 = zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1259_importable_from_package():
    from zst import zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314
    assert callable(zst_compressed_mod_1259_times_10300_plus_decompressed_times_311_plus_file_size_times_314)
