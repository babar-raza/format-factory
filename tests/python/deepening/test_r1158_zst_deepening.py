"""Sprint 604 ZST analytics deepening tests - primes 1277, 1279."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1277_text():
    from zst.zst_analytics import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    assert zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316(str(TEXT)) == 3036822

def test_mod1277_minimal():
    from zst.zst_analytics import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    assert zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316(str(MINIMAL)) == 107473

def test_mod1277_random():
    from zst.zst_analytics import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    assert zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316(str(RANDOM)) == 3278128

def test_mod1279_text():
    from zst.zst_analytics import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    assert zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318(str(TEXT)) == 3065346

def test_mod1279_minimal():
    from zst.zst_analytics import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    assert zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318(str(MINIMAL)) == 108495

def test_mod1279_random():
    from zst.zst_analytics import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    assert zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318(str(RANDOM)) == 3308328

def test_mod1277_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    assert isinstance(zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316(str(TEXT)), int)

def test_mod1277_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    assert zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316(str(TEXT)) >= 0

def test_mod1277_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    fn2 = zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1277_importable_from_package():
    from zst import zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316
    assert callable(zst_compressed_mod_1277_times_10400_plus_decompressed_times_313_plus_file_size_times_316)

def test_mod1279_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    assert isinstance(zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318(str(TEXT)), int)

def test_mod1279_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    assert zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318(str(TEXT)) >= 0

def test_mod1279_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    fn2 = zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1279_importable_from_package():
    from zst import zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318
    assert callable(zst_compressed_mod_1279_times_10500_plus_decompressed_times_315_plus_file_size_times_318)
