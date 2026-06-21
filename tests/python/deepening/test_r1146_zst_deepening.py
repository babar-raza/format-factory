"""Sprint 592 ZST analytics deepening tests - primes 1213, 1217."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1213_text():
    from zst.zst_analytics import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    assert zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300(str(TEXT)) == 2808630

def test_mod1213_minimal():
    from zst.zst_analytics import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    assert zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300(str(MINIMAL)) == 99297

def test_mod1213_random():
    from zst.zst_analytics import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    assert zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300(str(RANDOM)) == 3036528

def test_mod1217_text():
    from zst.zst_analytics import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    assert zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302(str(TEXT)) == 2837154

def test_mod1217_minimal():
    from zst.zst_analytics import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    assert zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302(str(MINIMAL)) == 100319

def test_mod1217_random():
    from zst.zst_analytics import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    assert zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302(str(RANDOM)) == 3066728

def test_mod1213_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    assert isinstance(zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300(str(TEXT)), int)

def test_mod1213_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    assert zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300(str(TEXT)) >= 0

def test_mod1213_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    fn2 = zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1213_importable_from_package():
    from zst import zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300
    assert callable(zst_compressed_mod_1213_times_9600_plus_decompressed_times_297_plus_file_size_times_300)

def test_mod1217_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    assert isinstance(zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302(str(TEXT)), int)

def test_mod1217_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    assert zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302(str(TEXT)) >= 0

def test_mod1217_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    fn2 = zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1217_importable_from_package():
    from zst import zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302
    assert callable(zst_compressed_mod_1217_times_9700_plus_decompressed_times_299_plus_file_size_times_302)
