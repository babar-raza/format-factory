"""Sprint 619 ZST analytics deepening tests - primes 1321, 1327."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"


def test_mod1321_text():
    from zst.zst_analytics import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(str(TEXT)) == 3322062

def test_mod1321_minimal():
    from zst.zst_analytics import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(str(MINIMAL)) == 117693

def test_mod1321_random():
    from zst.zst_analytics import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(str(RANDOM)) == 3580128

def test_mod1327_text():
    from zst.zst_analytics import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(str(TEXT)) == 3350586

def test_mod1327_minimal():
    from zst.zst_analytics import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(str(MINIMAL)) == 118715

def test_mod1327_random():
    from zst.zst_analytics import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(str(RANDOM)) == 3610328

def test_mod1321_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert isinstance(zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(str(TEXT)), int)

def test_mod1327_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert isinstance(zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(str(TEXT)), int)

def test_mod1321_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336(str(TEXT)) >= 0

def test_mod1327_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338(str(TEXT)) >= 0

def test_mod1321_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    fn = zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert len({fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}) == 3

def test_mod1327_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    fn = zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert len({fn(str(TEXT)), fn(str(MINIMAL)), fn(str(RANDOM))}) == 3

def test_mod1321_importable_from_package():
    from zst import zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336
    assert callable(zst_compressed_mod_1321_times_11400_plus_decompressed_times_333_plus_file_size_times_336)

def test_mod1327_importable_from_package():
    from zst import zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338
    assert callable(zst_compressed_mod_1327_times_11500_plus_decompressed_times_335_plus_file_size_times_338)
