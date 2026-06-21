"""Sprint 589 ZST analytics deepening tests - primes 1193, 1201."""
from pathlib import Path

SAMPLES = Path("samples/by-format/zst/valid")
TEXT = SAMPLES / "text-compressed.zst"
MINIMAL = SAMPLES / "minimal-synthetic.zst"
RANDOM = SAMPLES / "random-data.zst"

def test_mod1193_text():
    from zst.zst_analytics import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    assert zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296(str(TEXT)) == 2751582

def test_mod1193_minimal():
    from zst.zst_analytics import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    assert zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296(str(MINIMAL)) == 97253

def test_mod1193_random():
    from zst.zst_analytics import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    assert zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296(str(RANDOM)) == 2976128

def test_mod1201_text():
    from zst.zst_analytics import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    assert zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298(str(TEXT)) == 2780106

def test_mod1201_minimal():
    from zst.zst_analytics import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    assert zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298(str(MINIMAL)) == 98275

def test_mod1201_random():
    from zst.zst_analytics import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    assert zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298(str(RANDOM)) == 3006328

def test_mod1193_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    assert isinstance(zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296(str(TEXT)), int)

def test_mod1193_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    assert zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296(str(TEXT)) >= 0

def test_mod1193_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    fn2 = zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1193_importable_from_package():
    from zst import zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296
    assert callable(zst_compressed_mod_1193_times_9400_plus_decompressed_times_293_plus_file_size_times_296)

def test_mod1201_returns_int():
    from zst.zst_analytics import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    assert isinstance(zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298(str(TEXT)), int)

def test_mod1201_nonnegative():
    from zst.zst_analytics import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    assert zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298(str(TEXT)) >= 0

def test_mod1201_all_samples_differ():
    from zst.zst_analytics import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    fn2 = zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    results = {fn2(str(TEXT)), fn2(str(MINIMAL)), fn2(str(RANDOM))}
    assert len(results) == 3

def test_mod1201_importable_from_package():
    from zst import zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298
    assert callable(zst_compressed_mod_1201_times_9500_plus_decompressed_times_295_plus_file_size_times_298)
